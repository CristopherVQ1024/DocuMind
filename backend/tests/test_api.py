import time

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("QDRANT_URL", ":memory:")
    monkeypatch.setenv("DEV_AUTH_BYPASS", "true")
    monkeypatch.setenv("EMBED_DIM", "8")
    from app import config, gemini, indexer, normas, vectorstore

    config.get_settings.cache_clear()
    vectorstore.client.cache_clear()
    indexer.estado.listo = indexer.estado.indexando = False
    indexer.estado.error = ""

    async def fake_embed(texts, query=False):
        return [[float((hash(t) >> i) % 7 + 1) for i in range(8)] for t in texts]

    async def fake_stream(prompt):
        for piece in ["Según ", "el texto [1]."]:
            yield piece

    monkeypatch.setattr(gemini, "embed", fake_embed)
    monkeypatch.setattr(gemini, "stream_answer", fake_stream)
    from app.main import app

    with TestClient(app) as c:
        for _ in range(100):
            if c.get("/api/corpus").json()["estado"]["listo"]:
                break
            time.sleep(0.1)
        yield c


def test_parser_cubre_todas_las_normas():
    from app import normas

    todas = normas.cargar()
    assert {n.id for n in todas} >= {"ley-29733", "ds-016-2024-jus", "ley-30096", "ley-30999", "ds-126-2025-pcm"}
    assert all(len(n.articulos) > 10 for n in todas)
    ley = next(n for n in todas if n.id == "ley-29733")
    art = next(a for a in ley.articulos if a.numero == "28")
    assert "Título" in art.titulo and art.texto


def test_hijos_conservan_jerarquia():
    from app import indexer

    items = indexer.trozos()
    assert items and all(i["embed_text"].startswith(("Ley", "DS")) for i in items)
    assert max(len(i["text"]) for i in items) <= 800


def test_corpus_indexado(client):
    data = client.get("/api/corpus").json()
    assert data["estado"]["listo"] and data["estado"]["total"] == data["estado"]["progreso"]
    assert len(data["normas"]) == 5


def test_chat_con_citas_y_historial(client):
    with client.stream("POST", "/api/chat", json={"question": "¿Qué es el consentimiento?"}) as resp:
        body = "".join(resp.iter_text())
    assert "event: sources" in body and "event: token" in body and "event: done" in body
    history = client.get("/api/messages").json()
    assert [m["role"] for m in history] == ["user", "assistant"]
    assert history[1]["sources"][0]["etiqueta"]
    assert client.delete("/api/messages").status_code == 204
    assert client.get("/api/messages").json() == []
