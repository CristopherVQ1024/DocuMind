import argparse
import csv
import random
from collections import defaultdict

from common import DATA, RUNS, articulos, cita, leer_jsonl
from metricas import cohen_kappa, kappa_ponderado

CARPETA = DATA / "validacion"


def exportar_benchmark(por_tipo: int) -> None:
    rnd = random.Random(5)
    grupos = defaultdict(list)
    for q in leer_jsonl(DATA / "benchmark.jsonl"):
        grupos[q["tipo"]].append(q)
    filas = [q for g in grupos.values() for q in rnd.sample(g, min(por_tipo, len(g)))]
    for anotador in ("A", "B"):
        with (CARPETA / f"benchmark_{anotador}.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["qid", "tipo", "pregunta", "fecha_ref", "respuesta_ref", "estado_ref", "articulos_oro", "texto_oro",
                        "valida_0_1", "estado_correcto", "comentario"])
            for q in filas:
                textos = " || ".join(f"{cita(articulos()[a])}: {articulos()[a].texto[:1500]}" for a in q["gold"] if a in articulos())
                w.writerow([q["qid"], q["tipo"], q["pregunta"], q.get("fecha_ref") or "", q["respuesta_ref"], q["estado"],
                            ", ".join(q["gold"]), textos, "", "", ""])
    print(f"{len(filas)} preguntas en {CARPETA}/benchmark_A.csv y benchmark_B.csv")


def exportar_juez(n: int) -> None:
    rnd = random.Random(9)
    juicios = leer_jsonl(RUNS / "juez" / "juicios.jsonl")
    preguntas = {q["qid"]: q for q in leer_jsonl(DATA / "benchmark.jsonl")}
    elegidos = rnd.sample(juicios, min(n, len(juicios)))
    salidas = {}
    for j in elegidos:
        if j["corrida"] not in salidas:
            salidas[j["corrida"]] = {f["qid"]: f for f in leer_jsonl(RUNS / "generacion" / f"{j['corrida']}.jsonl")}
    with (CARPETA / "juez_experto.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["corrida", "qid", "pregunta", "fecha_ref", "respuesta_ref", "respuesta_sistema", "correccion_experto_0_2", "comentario"])
        for j in elegidos:
            q, s = preguntas[j["qid"]], salidas[j["corrida"]][j["qid"]]
            w.writerow([j["corrida"], j["qid"], q["pregunta"], q.get("fecha_ref") or "", q["respuesta_ref"], s["respuesta"], "", ""])
    print(f"{len(elegidos)} respuestas en {CARPETA}/juez_experto.csv")


def leer(ruta) -> list[dict]:
    with ruta.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def kappas() -> None:
    a, b = (leer(CARPETA / f"benchmark_{x}.csv") for x in ("A", "B"))
    pares = [(x, y) for x, y in zip(a, b) if x["valida_0_1"].strip() and y["valida_0_1"].strip()]
    if pares:
        va = [int(x["valida_0_1"]) for x, _ in pares]
        vb = [int(y["valida_0_1"]) for _, y in pares]
        acuerdo = sum(x == y == 1 for x, y in zip(va, vb)) / len(pares)
        print(f"benchmark: n={len(pares)} kappa={cohen_kappa(va, vb):.3f} validas_ambos={acuerdo:.3f}")
    ruta = CARPETA / "juez_experto.csv"
    if ruta.exists():
        juez = {(j["corrida"], j["qid"]): j["correccion"] for j in leer_jsonl(RUNS / "juez" / "juicios.jsonl")}
        filas = [f for f in leer(ruta) if f["correccion_experto_0_2"].strip()]
        if filas:
            h = [int(f["correccion_experto_0_2"]) for f in filas]
            m = [juez[(f["corrida"], f["qid"])] for f in filas]
            print(f"juez contra experto: n={len(filas)} kappa_ponderado={kappa_ponderado(m, h):.3f} acuerdo={sum(x == y for x, y in zip(m, h)) / len(h):.3f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["benchmark", "juez", "kappa"])
    ap.add_argument("--n", type=int, default=20)
    args = ap.parse_args()
    CARPETA.mkdir(parents=True, exist_ok=True)
    if args.accion == "benchmark":
        exportar_benchmark(args.n)
    elif args.accion == "juez":
        exportar_juez(args.n)
    else:
        kappas()


if __name__ == "__main__":
    main()
