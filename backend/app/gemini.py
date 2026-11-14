import asyncio
import time
from collections import deque
from collections.abc import AsyncIterator
from functools import lru_cache

from google import genai
from google.genai import errors, types

from .config import get_settings

SYSTEM_PROMPT = (
    "Eres DocuMind, un asistente sobre derecho laboral peruano del régimen privado. "
    "Respondes solo con la información de los artículos numerados que recibes. "
    "Cita cada afirmación con su número entre corchetes, por ejemplo [1], y nombra la norma y el artículo, por ejemplo D.S. 003-97-TR, artículo 34. "
    "Cada artículo trae su estado en la fecha de la consulta. Si está derogado, no existía o su redacción no regía en esa fecha, adviértelo y no lo presentes como vigente. "
    "Si la pregunta da por cierto algo que los artículos contradicen, corrígelo. "
    "Si los artículos no contienen la respuesta, dilo claramente y no inventes. "
    "Responde en español, de forma clara y breve, en texto plano sin formato Markdown. "
    "Es orientación informativa y no reemplaza la asesoría de un abogado."
)


@lru_cache
def client() -> genai.Client:
    return genai.Client(api_key=get_settings().gemini_api_key)


_window: deque[tuple[float, int]] = deque()
_gate = asyncio.Lock()
EMBED_TOKENS_PER_MINUTE = 24000


async def _wait_for_budget(tokens: int):
    async with _gate:
        while True:
            now = time.monotonic()
            while _window and now - _window[0][0] > 60:
                _window.popleft()
            if sum(t for _, t in _window) + tokens <= EMBED_TOKENS_PER_MINUTE:
                _window.append((now, tokens))
                return
            await asyncio.sleep(max(_window[0][0] + 60 - now, 1))


async def _retry(call, attempts: int = 5):
    delay = 5.0
    for attempt in range(attempts):
        try:
            return await call()
        except errors.APIError as exc:
            if exc.code not in (429, 500, 503) or attempt == attempts - 1:
                raise
            await asyncio.sleep(delay)
            delay *= 2


async def embed(texts: list[str], query: bool = False) -> list[list[float]]:
    settings = get_settings()
    vectors: list[list[float]] = []
    batches: list[list[str]] = []
    current: list[str] = []
    used = 0
    for text in texts:
        cost = len(text) // 3 + 1
        if current and (used + cost > 10000 or len(current) >= 50):
            batches.append(current)
            current, used = [], 0
        current.append(text)
        used += cost
    if current:
        batches.append(current)
    for batch in batches:
        await _wait_for_budget(sum(len(t) // 3 + 1 for t in batch))

        async def call(batch=batch):
            return await client().aio.models.embed_content(
                model=settings.gemini_embed_model,
                contents=batch,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_QUERY" if query else "RETRIEVAL_DOCUMENT",
                    output_dimensionality=settings.embed_dim,
                ),
            )

        result = await _retry(call)
        vectors.extend(list(e.values) for e in result.embeddings)
    return vectors


def build_prompt(question: str, passages: list[dict], history: list[dict]) -> str:
    context = "\n\n".join(
        f"[{p['n']}] {p['corto']}, {p['etiqueta']}. {p['titulo_articulo']} ({p['ruta']})\n{p['text']}\n{p.get('vigencia', '')}"
        for p in passages
    )
    past = "\n".join(
        f"{'Usuario' if m['role'] == 'user' else 'Asistente'}: {m['text']}" for m in history[-6:]
    )
    parts = [f"Fragmentos:\n{context}"]
    if past:
        parts.append(f"Conversación previa:\n{past}")
    parts.append(f"Pregunta: {question}")
    return "\n\n".join(parts)


async def stream_answer(prompt: str) -> AsyncIterator[str]:
    settings = get_settings()
    delay = 2.0
    for attempt in range(4):
        started = False
        try:
            stream = await client().aio.models.generate_content_stream(
                model=settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, temperature=0.2),
            )
            async for part in stream:
                if part.text:
                    started = True
                    yield part.text
            return
        except errors.APIError as exc:
            if started or exc.code not in (429, 500, 503) or attempt == 3:
                raise
            await asyncio.sleep(delay)
            delay *= 2
