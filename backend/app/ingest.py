import asyncio
import logging
import re
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from . import db, gemini, vectorstore
from .chunking import chunk_pages
from .config import get_settings
from .errors import friendly_error

log = logging.getLogger("documind.ingest")


def extract_pages(path: Path, max_pages: int) -> list[str]:
    reader = PdfReader(BytesIO(path.read_bytes()))
    if len(reader.pages) > max_pages:
        raise ValueError(f"El PDF tiene {len(reader.pages)} páginas y el máximo es {max_pages}")
    return [re.sub(r"\s+", " ", page.extract_text() or "").strip() for page in reader.pages]


async def index_document(doc_id: str, user_id: str, name: str, path: Path) -> None:
    settings = get_settings()
    try:
        pages = await asyncio.to_thread(extract_pages, path, settings.max_pages)
        chunks = chunk_pages(pages, settings.chunk_chars, settings.chunk_overlap)
        if not chunks:
            raise ValueError("No se encontró texto en el PDF. Puede ser un escaneo sin texto")
        vectors = await gemini.embed([c.text for c in chunks])
        await vectorstore.ensure_collection()
        await vectorstore.add_chunks(doc_id, user_id, name, chunks, vectors)
        db.update_document(doc_id, status="ready", pages=len(pages), chunks=len(chunks))
    except Exception as exc:
        log.exception("Falló el indexado de %s", doc_id)
        try:
            await vectorstore.delete_document(doc_id)
        except Exception:
            pass
        db.update_document(doc_id, status="error", error=friendly_error(exc))
