import hashlib
import json
import logging
from dataclasses import dataclass

from . import gemini, normas, vectorstore
from .chunking import split_text
from .config import get_settings
from .db import data_path
from .errors import friendly_error

log = logging.getLogger("documind.indexer")
BATCH = 40


@dataclass
class Estado:
    listo: bool = False
    indexando: bool = False
    progreso: int = 0
    total: int = 0
    error: str = ""


estado = Estado()


def ruta(articulo: normas.Articulo, norma: normas.Norma) -> str:
    partes = [p for p in (articulo.titulo, articulo.capitulo) if p]
    return " > ".join(partes)


def encabezado(norma: normas.Norma, articulo: normas.Articulo) -> str:
    partes = [norma.corto, articulo.titulo, articulo.capitulo, articulo.etiqueta]
    cabeza = " | ".join(p for p in partes if p)
    return f"{cabeza}. {articulo.titulo_articulo}" if articulo.titulo_articulo else cabeza


def trozos() -> list[dict]:
    settings = get_settings()
    items: list[dict] = []
    for norma in normas.cargar():
        for articulo in norma.articulos:
            cabeza = encabezado(norma, articulo)
            for idx, parte in enumerate(split_text(articulo.texto, settings.chunk_chars, settings.chunk_overlap)):
                items.append(
                    {
                        "articulo_id": articulo.id,
                        "norma_id": norma.id,
                        "chunk_idx": idx,
                        "text": parte,
                        "embed_text": f"{cabeza}\n{parte}",
                    }
                )
    return items


def coleccion() -> str:
    settings = get_settings()
    base = (normas.CORPUS_DIR / "normas.json").read_bytes()
    clave = f"{settings.gemini_embed_model}|{settings.embed_dim}|{settings.chunk_chars}|{settings.chunk_overlap}"
    sello = hashlib.sha1(base + clave.encode()).hexdigest()[:8]
    return f"{settings.qdrant_collection}-{sello}"


def _cache_path():
    return data_path() / "embeddings.jsonl"


def _leer_cache() -> dict[str, list[float]]:
    path = _cache_path()
    if not path.exists():
        return {}
    cache = {}
    for linea in path.read_text(encoding="utf-8").splitlines():
        try:
            fila = json.loads(linea)
            cache[fila["k"]] = fila["v"]
        except (ValueError, KeyError):
            continue
    return cache


def _clave(texto: str) -> str:
    settings = get_settings()
    return hashlib.sha1(f"{settings.gemini_embed_model}|{settings.embed_dim}|{texto}".encode()).hexdigest()


async def asegurar_indice() -> None:
    if estado.indexando:
        return
    settings = get_settings()
    estado.indexando, estado.listo, estado.error = True, False, ""
    try:
        items = trozos()
        nombre = coleccion()
        estado.total, estado.progreso = len(items), 0
        if await vectorstore.count(nombre) == len(items):
            estado.progreso, estado.listo = len(items), True
            await vectorstore.drop_others(f"{settings.qdrant_collection}-", nombre)
            return
        await vectorstore.reset_collection(nombre)
        cache = _leer_cache()
        with _cache_path().open("a", encoding="utf-8") as salida:
            for inicio in range(0, len(items), BATCH):
                grupo = items[inicio : inicio + BATCH]
                faltan = [i for i in grupo if _clave(i["embed_text"]) not in cache]
                if faltan:
                    vectores = await gemini.embed([i["embed_text"] for i in faltan])
                    for item, vector in zip(faltan, vectores):
                        cache[_clave(item["embed_text"])] = vector
                        salida.write(json.dumps({"k": _clave(item["embed_text"]), "v": vector}) + "\n")
                    salida.flush()
                payload = [{k: v for k, v in i.items() if k != "embed_text"} for i in grupo]
                await vectorstore.add_points(nombre, payload, [cache[_clave(i["embed_text"])] for i in grupo])
                estado.progreso = inicio + len(grupo)
        await vectorstore.drop_others(f"{settings.qdrant_collection}-", nombre)
        estado.listo = True
    except Exception as exc:
        log.exception("Falló el indexado del corpus")
        estado.error = friendly_error(exc)
    finally:
        estado.indexando = False
