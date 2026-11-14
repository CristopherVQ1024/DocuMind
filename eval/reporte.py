import json
from collections import Counter, defaultdict

import numpy as np

from common import DATA, RUNS, leer_jsonl
from metricas import bootstrap_ic, f1_abstencion, holm, mcnemar, particion, recuperacion, respuesta, wilcoxon

TIPOS = ["literal", "temporal", "rastreo", "multisalto", "premisa_falsa", "sin_respuesta"]
REFERENCIA_REC = "hibrido_rr"
REFERENCIAS_GEN = ("propuesto", "propuesto_det")


def tabla(cabecera: list[str], filas: list[list]) -> str:
    def celda(v):
        return f"{v:.3f}" if isinstance(v, float) else str(v)
    lineas = ["| " + " | ".join(cabecera) + " |", "|" + "---|" * len(cabecera)]
    lineas += ["| " + " | ".join(celda(v) for v in f) + " |" for f in filas]
    return "\n".join(lineas)


def media(filas: list[dict], clave: str) -> float:
    vals = [f[clave] for f in filas if clave in f]
    return float(np.mean(vals)) if vals else float("nan")


def seccion_recuperacion(preguntas: dict, salida: list[str], resumen: dict) -> None:
    carpeta = RUNS / "recuperacion"
    por_sistema = {}
    for ruta in sorted(carpeta.glob("*.jsonl")):
        filas = {}
        for f in leer_jsonl(ruta):
            q = preguntas.get(f["qid"])
            if not q or particion(f["qid"]) != "test":
                continue
            m = recuperacion(f["ranking"], q["gold"])
            if m:
                filas[f["qid"]] = {**m, "tipo": q["tipo"], "segundos": f["segundos"], "llm": f.get("llm_llamadas", 0)}
        por_sistema[ruta.stem] = filas
    if not por_sistema:
        return
    cab = ["Sistema", "n", "Hit@1", "Recall@5", "Recall@10", "MRR@10", "nDCG@10", "Todos@10", "s/consulta"]
    filas_t = []
    for s, filas in sorted(por_sistema.items(), key=lambda x: -media(list(x[1].values()), "ndcg@10")):
        v = list(filas.values())
        filas_t.append([s, len(v), media(v, "hit@1"), media(v, "recall@5"), media(v, "recall@10"), media(v, "mrr@10"),
                        media(v, "ndcg@10"), media([x for x in v if x["tipo"] == "multisalto"], "todos@10"), media(v, "segundos")])
        resumen.setdefault("recuperacion", {})[s] = dict(zip(cab[1:], filas_t[-1][1:]))
    salida += ["## Recuperación (partición test, preguntas con evidencia)", tabla(cab, filas_t), ""]
    cab = ["Sistema"] + TIPOS[:-1]
    filas_t = [[s] + [media([x for x in filas.values() if x["tipo"] == t], "recall@5") for t in TIPOS[:-1]]
               for s, filas in sorted(por_sistema.items())]
    salida += ["### Recall@5 por tipo de pregunta", tabla(cab, filas_t), ""]
    if REFERENCIA_REC in por_sistema:
        ref = por_sistema[REFERENCIA_REC]
        pv, ics = {}, {}
        for s, filas in por_sistema.items():
            if s == REFERENCIA_REC:
                continue
            comunes = sorted(set(ref) & set(filas))
            a = np.array([ref[q]["ndcg@10"] for q in comunes])
            b = np.array([filas[q]["ndcg@10"] for q in comunes])
            pv[s] = wilcoxon(a, b)
            ics[s] = bootstrap_ic(a, b)
        aj = holm(pv)
        filas_t = [[s, ics[s][0], f"[{ics[s][1]:.3f}, {ics[s][2]:.3f}]", f"{pv[s]:.2e}", f"{aj[s]:.2e}"] for s in sorted(pv, key=pv.get)]
        salida += [f"### Diferencia de nDCG@10: {REFERENCIA_REC} menos cada sistema (Wilcoxon, IC bootstrap 95 %, Holm)",
                   tabla(["Sistema", "Δ media", "IC 95 %", "p", "p Holm"], filas_t), ""]


def seccion_generacion(preguntas: dict, salida: list[str], resumen: dict) -> dict:
    carpeta = RUNS / "generacion"
    por_corrida = {}
    for ruta in sorted(carpeta.glob("*.jsonl")):
        filas = {}
        for f in leer_jsonl(ruta):
            q = preguntas.get(f["qid"])
            if not q or particion(f["qid"]) != "test":
                continue
            m = respuesta(q, f, f["contexto_aid"])
            m["tipo"] = q["tipo"]
            m["json_valido"] = float(f.get("json_valido", True))
            m["segundos"] = f["uso"].get("segundos", 0.0)
            m["tokens"] = f["uso"].get("tokens_in", 0) + f["uso"].get("tokens_out", 0)
            if q["estado"] != "vigente" and q["tipo"] in ("temporal", "premisa_falsa"):
                m["anacronismo"] = float(f.get("estado") == "vigente")
            m["estado_pred"] = f.get("estado", "")
            filas[f["qid"]] = m
        por_corrida[ruta.stem] = filas
    if not por_corrida:
        return por_corrida
    cab = ["Corrida", "n", "Cita P", "Cita R", "Estado ok", "Anacronismo", "Rastreo ok", "Abst P", "Abst R", "Abst F1", "JSON ok", "s/resp", "tokens"]
    filas_t = []
    for c, filas in sorted(por_corrida.items()):
        v = list(filas.values())
        ab = f1_abstencion(v)
        filas_t.append([c, len(v), media(v, "cita_precision"), media(v, "cita_recall"), media(v, "estado_ok"), media(v, "anacronismo"),
                        media(v, "rastreo_ok"), ab["abst_precision"], ab["abst_recall"], ab["abst_f1"], media(v, "json_valido"),
                        media(v, "segundos"), media(v, "tokens")])
        resumen.setdefault("generacion", {})[c] = dict(zip(cab[1:], filas_t[-1][1:]))
    salida += ["## Generación (partición test)", tabla(cab, filas_t), ""]
    for referencia in REFERENCIAS_GEN:
        for modelo in sorted({c.split("__")[1] for c in por_corrida}):
            nombre_ref = f"{referencia}__{modelo}"
            ref = por_corrida.get(nombre_ref)
            if not ref:
                continue
            pv, filas_t = {}, []
            for c, filas in por_corrida.items():
                if c.split("__")[1] != modelo or c == nombre_ref:
                    continue
                comunes = sorted(q for q in set(ref) & set(filas) if "estado_ok" in ref[q])
                if not comunes:
                    continue
                a = np.array([ref[q]["estado_ok"] for q in comunes])
                b = np.array([filas[q]["estado_ok"] for q in comunes])
                pv[c] = mcnemar(a, b)
                filas_t.append([c, len(comunes), float(a.mean()), float(b.mean())])
            if pv:
                aj = holm(pv)
                filas_t = [f + [f"{pv[f[0]]:.2e}", f"{aj[f[0]]:.2e}"] for f in filas_t]
                salida += [f"### Exactitud de estado temporal, {referencia} contra cada corrida con {modelo} (McNemar exacto, Holm)",
                           tabla(["Corrida", "n", referencia, "corrida", "p", "p Holm"], filas_t), ""]
    return por_corrida


def seccion_errores(preguntas: dict, por_corrida: dict, salida: list[str]) -> None:
    for c, filas in sorted(por_corrida.items()):
        if not c.startswith(REFERENCIAS_GEN):
            continue
        confusion = Counter((preguntas[q]["estado"], f["estado_pred"]) for q, f in filas.items()
                            if preguntas[q]["tipo"] in ("temporal", "premisa_falsa"))
        if confusion:
            filas_t = [[g, p, n] for (g, p), n in confusion.most_common(12)]
            salida += [f"### Matriz de confusión de estado, {c}", tabla(["Estado oro", "Estado predicho", "n"], filas_t), ""]


def seccion_juez(preguntas: dict, salida: list[str], resumen: dict) -> None:
    juicios = leer_jsonl(RUNS / "juez" / "juicios.jsonl")
    if not juicios:
        return
    grupos = defaultdict(list)
    for j in juicios:
        if particion(j["qid"]) == "test":
            grupos[j["corrida"]].append(j)
    filas_t = []
    for c, v in sorted(grupos.items()):
        corr = np.array([j["correccion"] for j in v])
        filas_t.append([c, len(v), float(corr.mean() / 2), float((corr == 2).mean()), float(np.mean([j["fidelidad"] for j in v]))])
        resumen.setdefault("juez", {})[c] = dict(zip(["n", "correccion", "correcta_total", "fidelidad"], filas_t[-1][1:]))
    salida += ["## Juez automático (muestra estratificada, partición test)",
               tabla(["Corrida", "n", "Corrección media", "Totalmente correcta", "Fidelidad"], filas_t), ""]


def main():
    preguntas = {q["qid"]: q for q in leer_jsonl(DATA / "benchmark.jsonl")}
    cuenta = Counter(q["tipo"] for q in preguntas.values())
    test = Counter(q["tipo"] for q in preguntas.values() if particion(q["qid"]) == "test")
    salida = ["# Resultados", "", tabla(["Tipo", "Total", "Test"], [[t, cuenta[t], test[t]] for t in TIPOS]), ""]
    resumen = {"benchmark": dict(cuenta)}
    seccion_recuperacion(preguntas, salida, resumen)
    por_corrida = seccion_generacion(preguntas, salida, resumen)
    seccion_errores(preguntas, por_corrida, salida)
    seccion_juez(preguntas, salida, resumen)
    (RUNS / "reporte.md").write_text("\n".join(salida), encoding="utf-8")
    (RUNS / "resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n".join(salida))


if __name__ == "__main__":
    main()
