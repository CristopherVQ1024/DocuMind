#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
LOGS=/home/cristopher/Documentos/nucleo-anexos/DocuMind/logs
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false

case "${1:-}" in
  recuperacion)
    .venv/bin/python -u correr_recuperacion.py ingenuo bm25 denso denso_sin_cabecera hibrido hibrido_rr \
      hibrido_rr_trozos recencia propuesto tacna_minilm tacna_bge
    .venv/bin/python -u calibrar.py propuesto
    ;;
  generacion)
    TAU=$(.venv/bin/python -c "import json;print(json.load(open('runs/umbral_propuesto.json'))['umbral'])")
    PRIMERO=1
    for MODELO in ${MODELOS:-llama3.1:8b gemma3:12b}; do
      case "$MODELO" in gemma3:12b) export GEN_HILOS=${HILOS_GEMMA:-2} ;; *) export GEN_HILOS=4 ;; esac
      if [ "$PRIMERO" = 1 ]; then BASES="ingenuo hibrido_rr recencia tacna_minilm tacna_bge"; else BASES="${BASES_SEGUNDO:-ingenuo hibrido_rr tacna_bge}"; fi
      for S in $BASES; do
        .venv/bin/python -u correr_generacion.py "$S" "$MODELO" --qids test.json
      done
      .venv/bin/python -u correr_generacion.py propuesto "$MODELO" --umbral "$TAU" --qids test.json
      if [ "$PRIMERO" = 1 ]; then
        .venv/bin/python -u correr_generacion.py propuesto "$MODELO" --etiqueta _sincompuerta --qids test.json
        .venv/bin/python -u correr_generacion.py propuesto "$MODELO" --umbral "$TAU" --sin-vigencia --etiqueta _sinvigencia --qids test.json
      fi
      PRIMERO=0
    done
    ;;
  *)
    echo "uso: lanzar.sh recuperacion|generacion" >&2
    exit 1
    ;;
esac
