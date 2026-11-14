import argparse

from common import RUNS, escribir_jsonl, leer_jsonl

CONSERVAR = ("premisa_falsa", "fuera_corpus")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corridas", nargs="+")
    args = ap.parse_args()
    estados = {}
    for f in leer_jsonl(RUNS / "recuperacion" / "propuesto.jsonl"):
        estados[f["qid"]] = {p["aid"]: p.get("estado", "vigente") for p in f["contexto"]}
    for corrida in args.corridas:
        sistema, modelo = corrida.split("__")
        salida = []
        for f in leer_jsonl(RUNS / "generacion" / f"{corrida}.jsonl"):
            f = dict(f)
            mapa = estados.get(f["qid"], {})
            if not f.get("abstiene") and f.get("estado") not in CONSERVAR and mapa:
                aid = next((c for c in f.get("citas_aid", []) if c in mapa), next(iter(mapa)))
                f["estado_llm"] = f.get("estado", "")
                f["estado"] = mapa[aid]
            salida.append(f)
        destino = RUNS / "generacion" / f"{sistema}_det__{modelo}.jsonl"
        escribir_jsonl(destino, salida)
        print(f"{destino.name}: {len(salida)}")


if __name__ == "__main__":
    main()
