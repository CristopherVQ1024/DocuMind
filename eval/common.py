import hashlib
import json
import os
import re
import sys
import time
from datetime import date
from functools import lru_cache
from pathlib import Path

import requests
from dotenv import load_dotenv

EVAL = Path(__file__).resolve().parent
ROOT = EVAL.parent
DATA = EVAL / "data"
CACHE = EVAL / "cache"
RUNS = EVAL / "runs"
for carpeta in (DATA, CACHE, RUNS):
    carpeta.mkdir(exist_ok=True)

sys.path.insert(0, str(ROOT / "backend"))
from app import normas  # noqa: E402

load_dotenv(ROOT / ".env")
HOY = date(2026, 11, 12)
OLLAMA = os.getenv("OLLAMA_URL", "http://localhost:11434")


def leer_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def escribir_jsonl(path: Path, filas: list[dict]) -> None:
    path.write_text("".join(json.dumps(f, ensure_ascii=False) + "\n" for f in filas), encoding="utf-8")


def agregar_jsonl(path: Path, fila: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False) + "\n")


@lru_cache
def corpus() -> list[normas.Norma]:
    return normas.cargar()


@lru_cache
def articulos() -> dict[str, normas.Articulo]:
    return normas.articulos_por_id()


@lru_cache
def normas_id() -> dict[str, normas.Norma]:
    return normas.normas_por_id()


def encabezado(a: normas.Articulo) -> str:
    n = normas_id()[a.norma_id]
    partes = [n.corto, n.nombre[:120], a.titulo, a.capitulo, a.etiqueta]
    cabeza = " | ".join(p for p in partes if p)
    return f"{cabeza}. {a.titulo_articulo}" if a.titulo_articulo else cabeza


def cita(a: normas.Articulo) -> str:
    return f"{normas_id()[a.norma_id].corto}, {a.etiqueta.lower() if a.etiqueta.startswith('Artículo') else a.etiqueta}"


def extraer_json(texto: str) -> dict | list | None:
    texto = re.sub(r"<think>.*?</think>", "", texto, flags=re.S).strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", texto, re.S)
    if m:
        texto = m.group(1)
    for abre, cierra in (("{", "}"), ("[", "]")):
        i, j = texto.find(abre), texto.rfind(cierra)
        if i != -1 and j > i:
            try:
                return json.loads(texto[i : j + 1])
            except json.JSONDecodeError:
                continue
    return None


def ollama(modelo: str, prompt: str, sistema: str = "", json_mode: bool = False, temperatura: float = 0.0,
           num_ctx: int = 8192) -> tuple[str, dict]:
    cuerpo = {
        "model": modelo,
        "prompt": prompt,
        "system": sistema,
        "stream": False,
        "options": {"temperature": temperatura, "num_ctx": num_ctx, "seed": 7},
        "keep_alive": "30m",
    }
    if json_mode:
        cuerpo["format"] = "json"
    if modelo.startswith(("gpt-oss", "qwen3")):
        cuerpo["think"] = "low" if modelo.startswith("gpt-oss") else False
    inicio = time.perf_counter()
    r = requests.post(f"{OLLAMA}/api/generate", json=cuerpo, timeout=600)
    r.raise_for_status()
    datos = r.json()
    uso = {
        "segundos": round(time.perf_counter() - inicio, 3),
        "tokens_in": datos.get("prompt_eval_count", 0),
        "tokens_out": datos.get("eval_count", 0),
    }
    return datos.get("response", ""), uso


@lru_cache
def _gemini():
    from google import genai
    from google.genai import types

    return genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options=types.HttpOptions(timeout=180_000))


_ultimo = [0.0]


def gemini(prompt: str, sistema: str = "", json_mode: bool = True, temperatura: float = 0.2,
           rpm: int = int(os.getenv("GEMINI_RPM", "8")), cache: bool = True) -> str:
    import httpx
    from google.genai import errors, types

    modelo = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    clave = hashlib.sha1(f"{modelo}|{sistema}|{prompt}|{temperatura}".encode()).hexdigest()
    ruta = CACHE / "gemini" / f"{clave}.txt"
    if cache and ruta.exists():
        return ruta.read_text(encoding="utf-8")
    espera = 5.0
    for intento in range(8):
        pausa = 60 / rpm - (time.monotonic() - _ultimo[0])
        if pausa > 0:
            time.sleep(pausa)
        _ultimo[0] = time.monotonic()
        try:
            r = _gemini().models.generate_content(
                model=modelo,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=sistema or None,
                    temperature=temperatura,
                    response_mime_type="application/json" if json_mode else None,
                ),
            )
            texto = r.text or ""
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_text(texto, encoding="utf-8")
            return texto
        except errors.APIError as exc:
            if exc.code not in (429, 500, 503, 504) or intento == 7:
                raise
            print(f"gemini {exc.code}, reintento en {espera:.0f}s", flush=True)
            time.sleep(espera)
            espera = min(espera * 2, 120)
        except httpx.HTTPError as exc:
            if intento == 7:
                raise
            print(f"gemini {type(exc).__name__}, reintento", flush=True)
    return ""


LOCAL = os.getenv("LLM_LOCAL", "gpt-oss:20b")


def redactar(prompt: str, sistema: str = "", temperatura: float = 0.2) -> tuple[str, str]:
    modelo = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    clave = hashlib.sha1(f"{modelo}|{sistema}|{prompt}|{temperatura}".encode()).hexdigest()
    previo = CACHE / "gemini" / f"{clave}.txt"
    if previo.exists():
        return previo.read_text(encoding="utf-8"), modelo
    local = prompt + "\n\nFormato de salida: un objeto JSON {\"items\": [...]} con un elemento por cada entrada recibida, en el mismo orden."
    clave = hashlib.sha1(f"{LOCAL}|{sistema}|{local}|{temperatura}".encode()).hexdigest()
    ruta = CACHE / "local" / f"{clave}.txt"
    if ruta.exists():
        return ruta.read_text(encoding="utf-8"), LOCAL
    texto, _ = ollama(LOCAL, local, sistema, json_mode=True, temperatura=temperatura, num_ctx=16384)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8")
    return texto, LOCAL
