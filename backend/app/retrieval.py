from . import gemini, indexer, normas, vectorstore, vigencia
from .config import get_settings


async def recuperar(pregunta: str) -> list[dict]:
    settings = get_settings()
    fecha, _ = vigencia.fecha_referencia(pregunta)
    vector = (await gemini.embed([pregunta], query=True))[0]
    golpes = await vectorstore.search(indexer.coleccion(), vector, settings.top_k)
    mejores: dict[str, float] = {}
    for g in golpes:
        mejores.setdefault(g["articulo_id"], g["score"])
    elegidos = list(mejores)[: settings.max_articles]
    por_id = normas.articulos_por_id()
    normas_por_id = {n.id: n for n in normas.cargar()}
    fuentes = []
    for n, articulo_id in enumerate(elegidos, start=1):
        articulo = por_id[articulo_id]
        norma = normas_por_id[articulo.norma_id]
        texto = articulo.texto
        estado, nota = vigencia.linea(articulo, fecha)
        if len(texto) > settings.article_chars:
            texto = texto[: settings.article_chars].rsplit(" ", 1)[0] + " …"
        fuentes.append(
            {
                "n": n,
                "articulo_id": articulo.id,
                "norma_id": norma.id,
                "norma": norma.nombre,
                "corto": norma.corto,
                "etiqueta": articulo.etiqueta,
                "titulo_articulo": articulo.titulo_articulo,
                "ruta": indexer.ruta(articulo, norma),
                "url": norma.url,
                "score": round(mejores[articulo_id], 4),
                "text": texto,
                "estado": estado,
                "vigencia": nota,
            }
        )
    return fuentes
