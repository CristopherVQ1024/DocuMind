import argparse
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from common import DATA, RUNS, agregar_jsonl, extraer_json, leer_jsonl, ollama

SISTEMA = """Eres un asistente de derecho laboral peruano del régimen privado. Respondes solo con los pasajes numerados que recibes.
Devuelve únicamente un objeto JSON con estas claves:
- "respuesta": respuesta breve en español, con la norma y el artículo que la sustentan.
- "citas": lista con los números de los pasajes que usaste, por ejemplo [1, 3].
- "estado": una de estas etiquetas sobre la disposición que responde la pregunta:
  "vigente" si la regla aplica en la fecha de la pregunta (hoy, si no indica fecha);
  "sin_version" si la pregunta se refiere a una fecha en la que la redacción disponible todavía no regía;
  "no_existia" si la disposición aún no existía en la fecha preguntada;
  "derogado" si la disposición está derogada;
  "premisa_falsa" si la pregunta da por cierto un dato que los pasajes contradicen;
  "fuera_corpus" si los pasajes no permiten responder.
- "abstiene": true si no puedes responder con los pasajes, false en otro caso.
- "norma_modificatoria": si la pregunta pide qué norma cambió una disposición, la norma que la modificó o incorporó; si no, "".
No inventes normas, artículos, cifras ni fechas que no estén en los pasajes."""


def prompt(pregunta: str, contexto: list[dict], fecha: str | None) -> str:
    bloques = []
    for i, p in enumerate(contexto, 1):
        extra = f"\n{p['vigencia']}" if p.get("vigencia") else ""
        bloques.append(f"[{i}] {p['texto']}{extra}")
    cabeza = f"Fecha de referencia de la consulta: {fecha}\n\n" if fecha else ""
    return f"{cabeza}Pasajes:\n\n" + "\n\n".join(bloques) + f"\n\nPregunta: {pregunta}"


def normalizar(datos: dict | None, contexto: list[dict]) -> dict:
    datos = datos if isinstance(datos, dict) else {}
    citas = []
    for c in datos.get("citas") or []:
        try:
            n = int(str(c).strip("[] "))
        except ValueError:
            continue
        if 1 <= n <= len(contexto):
            citas.append(contexto[n - 1]["aid"])
    estado = str(datos.get("estado", "")).strip().lower()
    return {
        "respuesta": str(datos.get("respuesta", "")),
        "citas_aid": list(dict.fromkeys(citas)),
        "estado": estado,
        "abstiene": bool(datos.get("abstiene")) or estado == "fuera_corpus",
        "norma_modificatoria": str(datos.get("norma_modificatoria", "") or ""),
        "json_valido": bool(datos),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sistema")
    ap.add_argument("modelo")
    ap.add_argument("--umbral", type=float, default=None)
    ap.add_argument("--sin-vigencia", action="store_true")
    ap.add_argument("--etiqueta", default="")
    ap.add_argument("--qids", default="")
    ap.add_argument("--hilos", type=int, default=int(os.getenv("GEN_HILOS", "1")))
    args = ap.parse_args()
    preguntas = {q["qid"]: q for q in leer_jsonl(DATA / "benchmark.jsonl")}
    if args.qids:
        permitidas = set(json.loads((DATA / args.qids).read_text()))
        preguntas = {k: v for k, v in preguntas.items() if k in permitidas}
    recuperacion = {f["qid"]: f for f in leer_jsonl(RUNS / "recuperacion" / f"{args.sistema}.jsonl")}
    nombre = f"{args.sistema}{args.etiqueta}__{args.modelo.replace(':', '-')}"
    ruta = RUNS / "generacion" / f"{nombre}.jsonl"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    hechas = {f["qid"] for f in leer_jsonl(ruta)}
    pendientes = [q for qid, q in preguntas.items() if qid in recuperacion and qid not in hechas]
    print(f"{nombre}: {len(pendientes)} pendientes", flush=True)
    inicio = time.perf_counter()
    candado = threading.Lock()
    hechas_ahora = [0]

    def responder(q):
        r = recuperacion[q["qid"]]
        contexto = [dict(p) for p in r["contexto"]]
        if args.sin_vigencia:
            for p in contexto:
                p.pop("vigencia", None)
        fecha = r.get("fecha_ref") if not args.sin_vigencia else None
        if args.umbral is not None and (not r.get("puntajes") or r["puntajes"][0] < args.umbral):
            salida = {"respuesta": "La consulta no se puede responder con las normas del corpus.", "citas_aid": [], "estado": "fuera_corpus",
                      "abstiene": True, "norma_modificatoria": "", "json_valido": True}
            uso = {"segundos": 0.0, "tokens_in": 0, "tokens_out": 0, "compuerta": True}
        else:
            texto, uso = ollama(args.modelo, prompt(q["pregunta"], contexto, fecha), SISTEMA, json_mode=True, num_ctx=12288)
            salida = normalizar(extraer_json(texto), contexto)
        with candado:
            agregar_jsonl(ruta, {"qid": q["qid"], **salida, "uso": uso, "contexto_aid": [p["aid"] for p in contexto]})
            hechas_ahora[0] += 1
            if hechas_ahora[0] % 50 == 0:
                print(f"  {hechas_ahora[0]}/{len(pendientes)} {time.perf_counter() - inicio:.0f}s", flush=True)

    with ThreadPoolExecutor(max(1, args.hilos)) as ex:
        list(ex.map(responder, pendientes))
    print(f"listo {nombre} {time.perf_counter() - inicio:.0f}s", flush=True)


if __name__ == "__main__":
    main()
