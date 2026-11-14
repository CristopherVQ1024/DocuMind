import json
import time

import torch

from sistemas import SISTEMAS

PREGUNTAS = [
    "¿Cuántos días de vacaciones remuneradas corresponden al trabajador por cada año de servicios?",
    "¿Qué establecía en 2001 el artículo 6 del D.S. 003-97-TR sobre la remuneración?",
    "¿Cuál es la pensión de jubilación en el régimen del Decreto Ley 19990?",
]

for nombre, fn in SISTEMAS.items():
    inicio = time.perf_counter()
    for p in PREGUNTAS:
        r = fn(p)
        print(json.dumps({"sistema": nombre, "top3": r["ranking"][:3], "fecha": r.get("fecha_ref"),
                          "s": r["segundos"]}, ensure_ascii=False), flush=True)
    print(f"{nombre} total {time.perf_counter() - inicio:.1f}s vram_pico {torch.cuda.max_memory_allocated() / 2**30:.2f} GiB", flush=True)
