import json
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parent.parent / "corpus"

ORDINALES = r"(?:PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|SÉPTIMA|SÉTIMA|OCTAVA|NOVENA|DÉCIMA|UNDÉCIMA|DUODÉCIMA|DECIMOPRIMERA|DECIMOSEGUNDA|ÚNICA)"
RE_TITULO = re.compile(r"^T[ÍI]TULO\s+([IVXLC]+|PRELIMINAR)$")
RE_CAPITULO = re.compile(r"^CAP[ÍI]TULO\s+([IVXLC]+)$")
RE_ARTICULO = re.compile(r"^Art[ií]culo\s+((?:\d+|[IVXLC]+)(?:-[A-Z])?)\.\s*(.*)$")
RE_DISPOSICIONES = re.compile(r"^DISPOSICI(?:ÓN|ONES)\s+COMPLEMENTARIAS?\b(.*)$")
RE_ORDINAL = re.compile(rf"^({ORDINALES})\.\s*(.*)$")
RE_MAYUS = re.compile(r"^[^a-zñáéíóú]+$")
FINAL_DEBIL = (" y", " de", " del", " la", " el", " en", " para", " los", " las", " o", " a", " con", " por")
TIPOS_DISPOSICION = {"FINALES": "final", "TRANSITORIAS": "transitoria", "MODIFICATORIAS": "modificatoria", "DEROGATORIA": "derogatoria"}
RE_LISTA = re.compile(r"^(\d+[.)]|[a-z]\)|[-•])\s")
RUIDO = [
    r"^NORMAS LEGALES$",
    r"^SEPARATA ESPECIAL$",
    r"^El Peruano$",
    r"^\d{1,3}$",
    r"^(Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)\b.*\d{4}",
    r"^(Firmado por|Fecha:)",
    r"^Diario Oficial El Peruano",
    r"^\(Ley N° 31649\)$",
]


@dataclass
class Articulo:
    id: str
    norma_id: str
    numero: str
    etiqueta: str
    titulo_articulo: str
    titulo: str
    capitulo: str
    texto: str


@dataclass
class Norma:
    id: str
    nombre: str
    corto: str
    tipo: str
    tema: str
    publicada: str
    url: str
    articulos: list[Articulo] = field(default_factory=list)


def sigue_titulo(actual: str, siguiente: str) -> bool:
    if actual.endswith((".", ":")):
        return False
    return siguiente[:1].islower() or actual.lower().endswith(FINAL_DEBIL)


def limpiar(linea: str) -> str:
    linea = unicodedata.normalize("NFKC", linea).replace("­", "")
    return re.sub(r"\s+", " ", linea).strip()


def unir(lineas: list[str]) -> str:
    texto = ""
    for linea in lineas:
        if not texto:
            texto = linea
        elif RE_LISTA.match(linea):
            texto += "\n" + linea
        elif texto.endswith("-") and linea[:1].islower():
            texto = texto[:-1] + linea
        else:
            texto += " " + linea
    return texto.strip()


def reparar(lineas: list[str]) -> list[str]:
    salida: list[str] = []
    i = 0
    while i < len(lineas):
        if lineas[i] == "Artículo" and i + 1 < len(lineas) and re.match(r"^\d+\.$", lineas[i + 1]):
            j = i + 2
            palabras = []
            while j < len(lineas) and len(lineas[j].split()) <= 2 and len(palabras) < 14:
                palabras.append(lineas[j])
                j += 1
            salida.append(f"Artículo {lineas[i + 1]} " + " ".join(palabras))
            i = j
            continue
        m = re.match(r"^(\d+)\.$", lineas[i])
        if m:
            j = i + 1
            palabras: list[str] = []
            while j < len(lineas) and len(lineas[j].split()) <= 2 and len(palabras) < 14:
                palabras.append(lineas[j])
                j += 1
            if len(palabras) >= 2 and j < len(lineas) and lineas[j].startswith(f"{m.group(1)}.1 "):
                salida.append(f"Artículo {m.group(1)}. " + " ".join(palabras))
                i = j
                continue
        salida.append(lineas[i])
        i += 1
    return salida


def recortar(lineas: list[str], inicio: str, fin: str) -> list[str]:
    ini = re.compile(inicio)
    end = re.compile(fin)
    start = next(i for i, l in enumerate(lineas) if ini.match(l))
    stop = next((i for i in range(start + 1, len(lineas)) if end.match(lineas[i])), len(lineas))
    return lineas[start:stop]


def parsear_norma(meta: dict, texto: str) -> Norma:
    ruido = [re.compile(p) for p in RUIDO + meta.get("ruido", [])]
    crudas = [limpiar(l) for l in texto.splitlines()]
    lineas = [l for l in crudas if l and not any(r.match(l) for r in ruido)]
    lineas = reparar(recortar(lineas, meta["inicio"], meta["fin"]))

    norma = Norma(**{k: meta[k] for k in ("id", "nombre", "corto", "tipo", "tema", "publicada", "url")})
    titulo = capitulo = ""
    actual: dict | None = None
    en_disposiciones = False

    def cerrar():
        nonlocal actual
        if actual and unir(actual["cuerpo"]):
            norma.articulos.append(
                Articulo(
                    id=f"{norma.id}:{actual['numero']}",
                    norma_id=norma.id,
                    numero=actual["numero"],
                    etiqueta=actual["etiqueta"],
                    titulo_articulo=actual["titulo_articulo"],
                    titulo=actual["titulo"],
                    capitulo=actual["capitulo"],
                    texto=unir(actual["cuerpo"]),
                )
            )
        actual = None

    def nombre_de(i: int) -> tuple[str, int]:
        partes = []
        while i < len(lineas) and len(partes) < 3 and RE_MAYUS.match(lineas[i]) and not _es_marca(lineas[i]):
            partes.append(lineas[i])
            i += 1
        return " ".join(partes), i

    def _es_marca(l: str) -> bool:
        return bool(RE_TITULO.match(l) or RE_CAPITULO.match(l) or RE_DISPOSICIONES.match(l) or RE_ORDINAL.match(l))

    i = 0
    while i < len(lineas):
        linea = lineas[i]
        if m := RE_TITULO.match(linea):
            cerrar()
            nombre, i = nombre_de(i + 1)
            titulo = f"Título {m.group(1).capitalize() if m.group(1) == 'PRELIMINAR' else m.group(1)}" + (f". {nombre.capitalize()}" if nombre else "")
            capitulo = ""
            en_disposiciones = False
            continue
        if m := RE_CAPITULO.match(linea):
            cerrar()
            nombre, i = nombre_de(i + 1)
            capitulo = f"Capítulo {m.group(1)}" + (f". {nombre.capitalize()}" if nombre else "")
            continue
        if m := RE_DISPOSICIONES.match(linea):
            cerrar()
            extra, i = nombre_de(i + 1) if not m.group(1).strip() else (m.group(1).strip(), i + 1)
            en_disposiciones = True
            titulo = "Disposiciones complementarias"
            capitulo = (m.group(0) + " " + extra if not m.group(1).strip() and extra else m.group(0)).capitalize()
            if not m.group(1).strip() and extra:
                capitulo = f"Disposiciones complementarias {extra.lower()}"
            continue
        if en_disposiciones:
            if m := RE_ORDINAL.match(linea):
                cerrar()
                tipo = next((v for k, v in TIPOS_DISPOSICION.items() if k in capitulo.upper()), "")
                etiqueta = f"{m.group(1).capitalize()} disposición complementaria {tipo}".strip()
                resto = m.group(2).strip()
                actual = {
                    "numero": f"D{len([a for a in norma.articulos if a.titulo == titulo]) + 1}-{m.group(1)[:3]}",
                    "etiqueta": etiqueta,
                    "titulo_articulo": resto,
                    "titulo": titulo,
                    "capitulo": capitulo,
                    "cuerpo": [],
                }
                i += 1
                while i < len(lineas) and resto and sigue_titulo(resto, lineas[i]):
                    resto += " " + lineas[i]
                    actual["titulo_articulo"] = resto
                    i += 1
                continue
            if actual is not None:
                actual["cuerpo"].append(linea)
            i += 1
            continue
        if m := RE_ARTICULO.match(linea):
            cerrar()
            numero, resto = m.group(1), m.group(2).strip()
            i += 1
            if not resto and i < len(lineas):
                resto = lineas[i]
                i += 1
            while i < len(lineas) and sigue_titulo(resto, lineas[i]):
                resto += " " + lineas[i]
                i += 1
            actual = {
                "numero": numero,
                "etiqueta": f"Artículo {numero}",
                "titulo_articulo": resto.rstrip("."),
                "titulo": titulo,
                "capitulo": capitulo,
                "cuerpo": [],
            }
            continue
        if actual is not None:
            actual["cuerpo"].append(linea)
        i += 1
    cerrar()
    return norma


def construir(txt_dir: Path) -> list[Norma]:
    fuentes = json.loads((CORPUS_DIR / "fuentes.json").read_text(encoding="utf-8"))
    return [parsear_norma(f, (txt_dir / f["archivo"]).read_text(encoding="utf-8")) for f in fuentes]


def guardar(normas: list[Norma]) -> Path:
    destino = CORPUS_DIR / "normas.json"
    destino.write_text(
        json.dumps([asdict(n) for n in normas], ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return destino


@lru_cache
def cargar() -> list[Norma]:
    datos = json.loads((CORPUS_DIR / "normas.json").read_text(encoding="utf-8"))
    return [Norma(**{**n, "articulos": [Articulo(**a) for a in n["articulos"]]}) for n in datos]


@lru_cache
def articulos_por_id() -> dict[str, Articulo]:
    return {a.id: a for n in cargar() for a in n.articulos}
