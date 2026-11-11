import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from . import db, gemini, indexer, normas, retrieval
from .auth import current_user
from .config import get_settings
from .errors import friendly_error


@asynccontextmanager
async def lifespan(_: FastAPI):
    task = asyncio.create_task(indexer.asegurar_indice())
    yield
    task.cancel()


app = FastAPI(title="DocuMind API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in get_settings().cors_origins.split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"ok": True}


@app.get("/api/corpus")
async def corpus(_: str = Depends(current_user)):
    return {
        "normas": [
            {
                "id": n.id,
                "nombre": n.nombre,
                "corto": n.corto,
                "tipo": n.tipo,
                "tema": n.tema,
                "publicada": n.publicada,
                "url": n.url,
                "articulos": len(n.articulos),
            }
            for n in normas.cargar()
        ],
        "estado": {
            "listo": indexer.estado.listo,
            "indexando": indexer.estado.indexando,
            "progreso": indexer.estado.progreso,
            "total": indexer.estado.total,
            "error": indexer.estado.error,
        },
    }


@app.get("/api/messages")
async def list_messages(user_id: str = Depends(current_user)):
    return [
        {k: m[k] for k in ("role", "text", "sources", "error")} for m in db.list_messages(user_id)
    ]


@app.delete("/api/messages", status_code=204)
async def clear_messages(user_id: str = Depends(current_user)):
    db.clear_messages(user_id)


class Turn(BaseModel):
    role: str
    text: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    history: list[Turn] = []


def sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/api/chat")
async def chat(body: ChatRequest, user_id: str = Depends(current_user)):
    if not indexer.estado.listo:
        raise HTTPException(409, "El corpus todavía se está indexando. Intenta en unos minutos.")

    db.add_message(user_id, "user", body.question)

    async def events():
        answer: list[str] = []
        sources: list[dict] = []
        failure = ""
        try:
            sources = await retrieval.recuperar(body.question)
            yield sse("sources", sources)
            if not sources:
                answer.append("No encontré normas relacionadas con tu pregunta.")
                yield sse("token", answer[0])
            else:
                prompt = gemini.build_prompt(body.question, sources, [t.model_dump() for t in body.history])
                async for piece in gemini.stream_answer(prompt):
                    answer.append(piece)
                    yield sse("token", piece)
            yield sse("done", {})
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            failure = friendly_error(exc)
            yield sse("error", {"message": failure})
        finally:
            text = "".join(answer)
            if text or failure:
                db.add_message(user_id, "assistant", text, sources, failure)

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
