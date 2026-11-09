import io

import pytest
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas


def make_pdf(pages: list[str]) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    for text in pages:
        c.drawString(72, 750, text)
        c.showPage()
    c.save()
    return buf.getvalue()


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("QDRANT_URL", ":memory:")
    monkeypatch.setenv("DEV_AUTH_BYPASS", "true")
    monkeypatch.setenv("EMBED_DIM", "8")
    from app import config, gemini, vectorstore

    config.get_settings.cache_clear()
    vectorstore.client.cache_clear()

    async def fake_embed(texts, query=False):
        return [[float((hash(t) >> i) % 7 + 1) for i in range(8)] for t in texts]

    async def fake_stream(prompt):
        for piece in ["Según ", "el texto [1]."]:
            yield piece

    monkeypatch.setattr(gemini, "embed", fake_embed)
    monkeypatch.setattr(gemini, "stream_answer", fake_stream)
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_chunking():
    from app.chunking import chunk_pages

    chunks = chunk_pages(["a" * 3000, "", "hola mundo"], 1200, 200)
    assert chunks[-1].page == 3
    assert all(len(c.text) <= 1200 for c in chunks)
    assert {c.page for c in chunks} == {1, 3}


def test_rejects_non_pdf(client):
    r = client.post("/api/documents", files={"file": ("x.pdf", b"nope", "application/pdf")})
    assert r.status_code == 415


def test_upload_index_chat_delete(client):
    pdf = make_pdf(["Qdrant es una base de datos vectorial.", "Nginx es un proxy inverso."])
    r = client.post("/api/documents", files={"file": ("guia.pdf", pdf, "application/pdf")})
    assert r.status_code == 202
    doc_id = r.json()["id"]

    docs = client.get("/api/documents").json()
    assert docs[0]["status"] == "ready" and docs[0]["pages"] == 2

    with client.stream("POST", "/api/chat", json={"question": "¿Qué es Qdrant?"}) as resp:
        body = "".join(resp.iter_text())
    assert "event: sources" in body and "event: token" in body and "event: done" in body
    assert "guia.pdf" in body

    history = client.get("/api/messages").json()
    assert [m["role"] for m in history] == ["user", "assistant"]
    assert history[1]["text"] == "Según el texto [1]." and history[1]["sources"][0]["doc_name"] == "guia.pdf"
    assert client.delete("/api/messages").status_code == 204
    assert client.get("/api/messages").json() == []

    assert client.delete(f"/api/documents/{doc_id}").status_code == 204
    assert client.get("/api/documents").json() == []


def test_chat_without_documents(client):
    assert client.post("/api/chat", json={"question": "hola"}).status_code == 409
