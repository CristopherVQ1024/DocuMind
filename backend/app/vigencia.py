import re
from datetime import date

from .normas import Articulo

RE_ANIO = re.compile(r"(?<![\d\-/°º])(19[5-9]\d|20[0-4]\d)(?![\d\-])")
RE_FECHA = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](19\d\d|20\d\d)\b")
RE_NUMERO_NORMA = re.compile(r"(?:N\s*[°º]\s*|Ley\s+|D\.?\s*S\.?\s*|DS\s+)[\d\-A-Z]+")

ETIQUETAS = {
    "vigente": "VIGENTE en la fecha consultada",
    "sin_version": "ADVERTENCIA: esta redacción no regía en la fecha consultada",
    "no_existia": "NO EXISTÍA en la fecha consultada",
    "derogado": "DEROGADO en la fecha consultada",
}


def fecha_referencia(pregunta: str, hoy: date | None = None) -> tuple[date, bool]:
    if m := RE_FECHA.search(pregunta):
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1))), True
        except ValueError:
            pass
    anios = RE_ANIO.findall(RE_NUMERO_NORMA.sub(" ", pregunta))
    if anios:
        return date(int(anios[-1]), 7, 1), True
    return hoy or date.today(), False


def linea(a: Articulo, fecha: date) -> tuple[str, str]:
    estado = a.vigencia_en(fecha)
    ult = max((n for n in a.notas if n.fecha and n.accion in ("modificado", "incorporado")), key=lambda n: n.fecha, default=None)
    der = next((n for n in a.notas if n.accion == "derogado" and n.fecha == a.derogado_desde), None)
    partes = [f"Estado al {fecha.isoformat()}: {ETIQUETAS[estado]}."]
    if estado == "sin_version":
        partes.append(f"La redacción actual rige desde {a.version_desde}" + (f" ({ult.accion} por {ult.norma_por})" if ult else "") + "; el texto aplicable en esa fecha no está en el corpus.")
    elif estado == "no_existia":
        partes.append(f"Fue incorporado el {a.existe_desde}" + (f" por {ult.norma_por}" if ult else "") + ".")
    elif estado == "derogado":
        partes.append(f"Derogado desde {a.derogado_desde}" + (f" por {der.norma_por}" if der else "") + ".")
    historial = [f"{n.elemento or 'Artículo'} {n.accion} por {n.norma_por} el {n.fecha}" for n in a.notas if n.norma_por]
    if historial:
        partes.append("Historial: " + "; ".join(historial[:6]) + ".")
    return estado, " ".join(partes)
