import asyncio
from types import SimpleNamespace

import httpx2
import pytest
from google.genai import errors


def preparar(monkeypatch, comportamiento):
    monkeypatch.setenv("GEMINI_MODEL", "a")
    monkeypatch.setenv("GEMINI_FALLBACK_MODELS", "b")
    monkeypatch.setenv("GEMINI_TIMEOUT_S", "0.2")
    from app import config, gemini

    config.get_settings.cache_clear()
    llamados = []

    async def generar(model, contents, config):
        llamados.append(model)

        async def partes():
            for paso in comportamiento[model]:
                if paso == "colgar":
                    await asyncio.sleep(5)
                elif paso == "sin red":
                    raise httpx2.ConnectError("x")
                elif isinstance(paso, int):
                    raise errors.APIError(paso, {"error": {"message": "x"}})
                else:
                    yield SimpleNamespace(text=paso)

        return partes()

    falso = SimpleNamespace(aio=SimpleNamespace(models=SimpleNamespace(generate_content_stream=generar)))
    monkeypatch.setattr(gemini, "client", lambda: falso)

    async def correr():
        return [t async for t in gemini.stream_answer("p")]

    return llamados, lambda: asyncio.run(correr())


@pytest.mark.parametrize("fallo", [404, 429, 503, "colgar", "sin red"])
def test_usa_el_respaldo(monkeypatch, fallo):
    llamados, correr = preparar(monkeypatch, {"a": [fallo], "b": ["ok"]})
    assert correr() == ["ok"] and llamados == ["a", "b"]


def test_respuesta_vacia_pasa_al_respaldo(monkeypatch):
    llamados, correr = preparar(monkeypatch, {"a": [], "b": ["ok"]})
    assert correr() == ["ok"] and llamados == ["a", "b"]


def test_clave_mala_no_usa_respaldo(monkeypatch):
    llamados, correr = preparar(monkeypatch, {"a": [401], "b": ["ok"]})
    with pytest.raises(errors.APIError):
        correr()
    assert llamados == ["a"]


def test_no_mezcla_respuestas(monkeypatch):
    llamados, correr = preparar(monkeypatch, {"a": ["mitad", 503], "b": ["ok"]})
    with pytest.raises(errors.APIError):
        correr()
    assert llamados == ["a"]


def test_fallan_todos(monkeypatch):
    llamados, correr = preparar(monkeypatch, {"a": [503], "b": ["colgar"]})
    with pytest.raises(TimeoutError):
        correr()
    assert llamados == ["a", "b"]
