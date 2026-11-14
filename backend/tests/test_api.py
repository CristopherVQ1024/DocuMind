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
        for _ in range(600):
            if c.get("/api/corpus").json()["estado"]["listo"]:
                break
            time.sleep(0.1)
        yield c


def test_parser_cubre_todas_las_normas():
    from app import normas

    todas = normas.cargar()
    assert {n.id for n in todas} >= {"ds-003-97-tr", "ds-001-97-tr", "dleg-713", "ley-29783", "ds-005-2012-tr"}
    assert len(todas) == 135 and sum(len(n.articulos) for n in todas) > 3000
    art = normas.articulos_por_id()["ds-003-97-tr:16"]
    assert "extinci" in art.titulo_articulo.lower() and art.texto


def test_vigencia_por_fecha():
    from datetime import date

    from app import normas, vigencia

    art = normas.articulos_por_id()["ds-003-97-tr:6"]
    assert art.vigencia_en(date(2001, 7, 1)) == "sin_version"
    assert art.vigencia_en(date(2010, 1, 1)) == "vigente"
    assert vigencia.fecha_referencia("¿Qué regía en 2001 según el D.S. 003-97-TR?")[0] == date(2001, 7, 1)
    assert vigencia.fecha_referencia("¿Qué dice la Ley 29783?")[1] is False
    estado, nota = vigencia.linea(art, date(2001, 7, 1))
    assert estado == "sin_version" and "28051" in nota


def test_hijos_conservan_jerarquia():
    from app import indexer

    items = indexer.trozos()
    assert items and all(i["embed_text"].startswith(("Ley", "DS", "RM", "D.", "DL", "DU", "RS")) for i in items)
    assert max(len(i["text"]) for i in items) <= 800


def test_corpus_indexado(client):
    data = client.get("/api/corpus").json()
    assert data["estado"]["listo"] and data["estado"]["total"] == data["estado"]["progreso"]
    assert len(data["normas"]) == 135


def test_chat_con_citas_y_historial(client):
    with client.stream("POST", "/api/chat", json={"question": "¿Cuántos días de vacaciones corresponden?"}) as resp:
        body = "".join(resp.iter_text())
    assert "event: sources" in body and "event: token" in body and "event: done" in body
    history = client.get("/api/messages").json()
    assert [m["role"] for m in history] == ["user", "assistant"]
    assert history[1]["sources"][0]["etiqueta"] and history[1]["sources"][0]["estado"]
    assert client.delete("/api/messages").status_code == 204
    assert client.get("/api/messages").json() == []
