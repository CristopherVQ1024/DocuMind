import json
from dataclasses import dataclass, field
from datetime import date
from functools import lru_cache
from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parent.parent / "corpus"


@dataclass
class Nota:
    accion: str
    elemento: str
    por: str
    norma_por: str
    fecha: str
    texto: str


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
    pagina: int = 0
    estado: str = "vigente"
    existe_desde: str = ""
    version_desde: str = ""
    derogado_desde: str = ""
    notas: list[Nota] = field(default_factory=list)

    def vigencia_en(self, fecha: date) -> str:
        # vigente, sin_version, no_existia o derogado
        f = fecha.isoformat()
        if self.existe_desde and f < self.existe_desde:
            return "no_existia"
        if self.derogado_desde and f >= self.derogado_desde:
            return "derogado"
        if self.version_desde and f < self.version_desde:
            return "sin_version"
        return "vigente"


@dataclass
class Norma:
    id: str
    nombre: str
    corto: str
    tipo: str
    tema: str
    publicada: str
    url: str
    pagina: int = 0
    articulos: list[Articulo] = field(default_factory=list)


def _articulo(datos: dict) -> Articulo:
    return Articulo(**{**datos, "notas": [Nota(**n) for n in datos.get("notas", [])]})


@lru_cache
def cargar() -> list[Norma]:
    datos = json.loads((CORPUS_DIR / "normas.json").read_text(encoding="utf-8"))
    return [Norma(**{**n, "articulos": [_articulo(a) for a in n["articulos"]]}) for n in datos]


@lru_cache
def articulos_por_id() -> dict[str, Articulo]:
    return {a.id: a for n in cargar() for a in n.articulos}


@lru_cache
def normas_por_id() -> dict[str, Norma]:
    return {n.id: n for n in cargar()}
