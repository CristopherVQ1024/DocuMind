import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.normas import construir, guardar

normas = construir(Path(sys.argv[1]))
for n in normas:
    print(f"{n.corto}: {len(n.articulos)} artículos")
print(guardar(normas))
