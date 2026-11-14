import argparse
import json

import numpy as np

from common import DATA, RUNS, leer_jsonl
from metricas import particion


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sistema", nargs="?", default="propuesto")
    args = ap.parse_args()
    preguntas = {q["qid"]: q for q in leer_jsonl(DATA / "benchmark.jsonl")}
    filas = [f for f in leer_jsonl(RUNS / "recuperacion" / f"{args.sistema}.jsonl")
             if f["qid"] in preguntas and particion(f["qid"]) == "dev" and f.get("puntajes")]
    tope = np.array([f["puntajes"][0] for f in filas])
    debe = np.array([bool(preguntas[f["qid"]]["abstener"]) for f in filas])
    mejor = (0.0, None)
    for tau in np.unique(np.round(tope, 3)):
        pred = tope < tau
        tp, fp, fn = (pred & debe).sum(), (pred & ~debe).sum(), (~pred & debe).sum()
        f1 = 2 * tp / (2 * tp + fp + fn) if tp else 0.0
        if f1 > mejor[0]:
            mejor = (float(f1), float(tau))
    salida = {"sistema": args.sistema, "n_dev": len(filas), "f1_dev": round(mejor[0], 4), "umbral": mejor[1]}
    (RUNS / f"umbral_{args.sistema}.json").write_text(json.dumps(salida, indent=2))
    print(salida)


if __name__ == "__main__":
    main()
