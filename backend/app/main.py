import asyncio
import json
import uuid
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from . import db, gemini, ingest, vectorstore
from .auth import current_user
from .config import get_settings
from .errors import friendly_error


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.fail_stale_indexing()
    yield


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


def public(doc: dict) -> dict:
    return {k: doc[k] for k in ("id", "name", "size", "status", "pages", "chunks", "error", "created_at")}


@app.get("/api/documents")
async def list_documents(user_id: str = Depends(current_user)):
    return [public(d) for d in db.list_documents(user_id)]


@app.post("/api/documents", status_code=202)
async def upload_document(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(current_user),
):
    settings = get_settings()
    name = file.filename or "documento.pdf"
    if not name.lower().endswith(".pdf") or file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(415, "Solo se aceptan archivos PDF")
    content = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"El archivo supera {settings.max_upload_mb} MB")
    if not content.startswith(b"%PDF"):
        raise HTTPException(415, "El archivo no es un PDF válido")
    doc_id = str(uuid.uuid4())
    path = db.data_path() / "pdfs" / f"{doc_id}.pdf"
    path.write_bytes(content)
    db.create_document(doc_id, user_id, name, len(content))
    background.add_task(ingest.index_document, doc_id, user_id, name, path)
    return public(db.get_document(doc_id, user_id))


@app.delete("/api/documents/{doc_id}", status_code=204)
async def remove_document(doc_id: str, user_id: str = Depends(current_user)):
    if not db.get_document(doc_id, user_id):
        raise HTTPException(404, "Documento no encontrado")
    try:
        await vectorstore.delete_document(doc_id)
    except Exception:
        pass
    (db.data_path() / "pdfs" / f"{doc_id}.pdf").unlink(missing_ok=True)
    db.delete_document(doc_id)


@app.get("/api/documents/{doc_id}/file")
async def download_document(doc_id: str, user_id: str = Depends(current_user)):
    doc = db.get_document(doc_id, user_id)
    path = db.data_path() / "pdfs" / f"{doc_id}.pdf"
    if not doc or not path.exists():
        raise HTTPException(404, "Documento no encontrado")
    return FileResponse(path, media_type="application/pdf", filename=doc["name"])


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
    doc_ids: list[str] = []
    history: list[Turn] = []


def sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/api/chat")
async def chat(body: ChatRequest, user_id: str = Depends(current_user)):
    settings = get_settings()
    ready = [d for d in db.list_documents(user_id) if d["status"] == "ready"]
    if body.doc_ids:
        ready = [d for d in ready if d["id"] in body.doc_ids]
    if not ready:
        raise HTTPException(409, "No hay documentos listos para consultar")

    db.add_message(user_id, "user", body.question)

    async def events():
        answer: list[str] = []
        sources: list[dict] = []
        failure = ""
        try:
            vector = (await gemini.embed([body.question], query=True))[0]
            passages = await vectorstore.search(vector, user_id, [d["id"] for d in ready], settings.top_k)
            sources = [
                {"n": i, "doc_id": p["doc_id"], "doc_name": p["doc_name"], "page": p["page"], "text": p["text"]}
                for i, p in enumerate(passages, start=1)
            ]
            yield sse("sources", sources)
            if not passages:
                answer.append("No encontré fragmentos relacionados en tus documentos.")
                yield sse("token", answer[0])
            else:
                prompt = gemini.build_prompt(
                    body.question, passages, [t.model_dump() for t in body.history]
                )
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
