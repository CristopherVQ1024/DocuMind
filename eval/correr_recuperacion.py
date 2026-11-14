import argparse
import json
import time

from common import DATA, RUNS, agregar_jsonl, leer_jsonl
from sistemas import SISTEMAS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sistemas", nargs="+", choices=list(SISTEMAS))
    ap.add_argument("--limite", type=int, default=0)
    args = ap.parse_args()
    preguntas = leer_jsonl(DATA / "benchmark.jsonl")
    if args.limite:
        preguntas = preguntas[: args.limite]
    carpeta = RUNS / "recuperacion"
    carpeta.mkdir(parents=True, exist_ok=True)
    for nombre in args.sistemas:
        ruta = carpeta / f"{nombre}.jsonl"
        hechas = {f["qid"] for f in leer_jsonl(ruta)}
        pendientes = [q for q in preguntas if q["qid"] not in hechas]
        print(f"{nombre}: {len(pendientes)} pendientes", flush=True)
        inicio = time.perf_counter()
        for i, q in enumerate(pendientes, 1):
            r = SISTEMAS[nombre](q["pregunta"])
            agregar_jsonl(ruta, {"qid": q["qid"], **r})
            if i % 50 == 0:
                print(f"  {nombre} {i}/{len(pendientes)} {time.perf_counter() - inicio:.0f}s", flush=True)
        print(json.dumps({"sistema": nombre, "segundos": round(time.perf_counter() - inicio, 1)}), flush=True)


if __name__ == "__main__":
    main()
