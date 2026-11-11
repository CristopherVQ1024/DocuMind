import subprocess
import sys
from pathlib import Path


def paginas(pdf: Path) -> int:
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
    return int(next(l.split()[1] for l in info.splitlines() if l.startswith("Pages:")))


def ancho_alto(pdf: Path) -> tuple[float, float]:
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
    partes = next(l for l in info.splitlines() if l.startswith("Page size:")).split()
    return float(partes[2]), float(partes[4])


def extraer(pdf: Path, columnas: int) -> str:
    ancho, alto = ancho_alto(pdf)
    salida = []
    for pagina in range(1, paginas(pdf) + 1):
        for c in range(columnas):
            x = int(ancho / columnas * c)
            w = int(ancho / columnas)
            texto = subprocess.run(
                ["pdftotext", "-f", str(pagina), "-l", str(pagina), "-x", str(x), "-y", "0",
                 "-W", str(w), "-H", str(int(alto)), str(pdf), "-"],
                capture_output=True, text=True, check=True,
            ).stdout
            salida.append(texto)
    return "\n".join(salida)


if __name__ == "__main__":
    pdf, destino, columnas = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
    destino.write_text(extraer(pdf, columnas), encoding="utf-8")
