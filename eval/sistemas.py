import re
import time
import unicodedata
from datetime import date
from functools import lru_cache

import numpy as np

from common import HOY, articulos, extraer_json, normas_id, ollama
from app import vigencia
from indice import (EMB_BGE, EMB_MINILM, BM25, Trozos, embeber, embeber_consultas, rerankear, texto_articulo,
                    trozos_articulo, trozos_ingenuos)

TOP_ARTICULOS = 20
CONTEXTO = 5
RRF_K = 60
LLM_ENRUTADOR = "llama3.1:8b"


def fecha_referencia(pregunta: str) -> tuple[date, bool]:
    return vigencia.fecha_referencia(pregunta, HOY)


def orden_articulos(trozos: Trozos, indices: np.ndarray) -> list[str]:
    vistos = {}
    for i in indices:
        for aid in trozos.articulos_por_trozo[i]:
            vistos.setdefault(aid, None)
    return list(vistos)


def rrf(*rankings: list[str], k: int = RRF_K) -> list[str]:
    puntos: dict[str, float] = {}
    for r in rankings:
        for pos, aid in enumerate(r):
            puntos[aid] = puntos.get(aid, 0) + 1 / (k + pos + 1)
    return sorted(puntos, key=puntos.get, reverse=True)


class Denso:
    def __init__(self, trozos: Trozos, modelo: str):
        self.trozos, self.modelo = trozos, modelo
        self.matriz = embeber(trozos, modelo)

    def buscar(self, consulta: str, k: int = 100, mascara: np.ndarray | None = None) -> np.ndarray:
        q = embeber_consultas([consulta], self.modelo)[0]
        s = self.matriz @ q
        if mascara is not None:
            s = np.where(mascara, s, -np.inf)
        top = np.argpartition(-s, min(k, len(s) - 1))[:k]
        top = top[np.argsort(-s[top])]
        return top[np.isfinite(s[top])]


class Lexico:
    def __init__(self, trozos: Trozos):
        self.trozos = trozos
        self.bm25 = BM25(trozos.embebidos)

    def buscar(self, consulta: str, k: int = 100) -> np.ndarray:
        s = self.bm25.puntajes(consulta)
        top = np.argpartition(-s, min(k, len(s) - 1))[:k]
        return top[np.argsort(-s[top])]


@lru_cache
def denso_bge() -> Denso:
    return Denso(trozos_articulo(), EMB_BGE)


@lru_cache
def denso_bge_crudo() -> Denso:
    t = trozos_articulo()
    crudo = Trozos(t.nombre + "-crudo", t.ids, t.textos, t.textos, t.articulos_por_trozo, t.meta)
    return Denso(crudo, EMB_BGE)


@lru_cache
def denso_minilm_crudo() -> Denso:
    t = trozos_articulo()
    crudo = Trozos(t.nombre + "-crudo", t.ids, t.textos, t.textos, t.articulos_por_trozo, t.meta)
    return Denso(crudo, EMB_MINILM)


@lru_cache
def denso_ingenuo() -> Denso:
    return Denso(trozos_ingenuos(), EMB_BGE)


@lru_cache
def lexico() -> Lexico:
    return Lexico(trozos_articulo())


def resultado(ranking: list[str], contexto: list[dict], inicio: float, **extra) -> dict:
    return {"ranking": ranking[:TOP_ARTICULOS], "contexto": contexto, "segundos": round(time.perf_counter() - inicio, 3), **extra}


def pasajes(aids: list[str]) -> list[dict]:
    return [{"aid": aid, "texto": texto_articulo(aid)} for aid in aids[:CONTEXTO]]


def ingenuo(pregunta: str) -> dict:
    t0 = time.perf_counter()
    d = denso_ingenuo()
    top = d.buscar(pregunta, k=40)
    ranking = orden_articulos(d.trozos, top)
    contexto = [{"aid": d.trozos.articulos_por_trozo[i][0], "texto": d.trozos.textos[i]} for i in top[:CONTEXTO]]
    return resultado(ranking, contexto, t0)


def bm25(pregunta: str) -> dict:
    t0 = time.perf_counter()
    ranking = orden_articulos(lexico().trozos, lexico().buscar(pregunta))
    return resultado(ranking, pasajes(ranking), t0)


def denso(pregunta: str) -> dict:
    t0 = time.perf_counter()
    d = denso_bge()
    ranking = orden_articulos(d.trozos, d.buscar(pregunta))
    return resultado(ranking, pasajes(ranking), t0)


def denso_sin_cabecera(pregunta: str) -> dict:
    t0 = time.perf_counter()
    d = denso_bge_crudo()
    ranking = orden_articulos(d.trozos, d.buscar(pregunta))
    return resultado(ranking, pasajes(ranking), t0)


def candidatos_hibridos(pregunta: str) -> list[str]:
    d = denso_bge()
    r_denso = orden_articulos(d.trozos, d.buscar(pregunta))
    r_lex = orden_articulos(lexico().trozos, lexico().buscar(pregunta))
    return rrf(r_denso, r_lex)


def hibrido(pregunta: str) -> dict:
    t0 = time.perf_counter()
    ranking = candidatos_hibridos(pregunta)
    return resultado(ranking, pasajes(ranking), t0)


def rerank_articulos(pregunta: str, aids: list[str]) -> list[tuple[str, float]]:
    puntajes = rerankear(pregunta, [texto_articulo(a, 1800) for a in aids])
    return sorted(zip(aids, puntajes), key=lambda x: -x[1])


def hibrido_rr(pregunta: str, n: int = 40) -> dict:
    t0 = time.perf_counter()
    orden = rerank_articulos(pregunta, candidatos_hibridos(pregunta)[:n])
    ranking = [a for a, _ in orden]
    return resultado(ranking, pasajes(ranking), t0, puntajes=[round(s, 4) for _, s in orden[:TOP_ARTICULOS]])


def hibrido_rr_trozos(pregunta: str, n: int = 40) -> dict:
    t0 = time.perf_counter()
    d, lx = denso_bge(), lexico()
    idx = list(dict.fromkeys(list(d.buscar(pregunta, 60)) + list(lx.buscar(pregunta, 60))))
    cand = idx[: n * 2]
    puntajes = rerankear(pregunta, [d.trozos.embebidos[i] for i in cand])
    orden = [i for i, _ in sorted(zip(cand, puntajes), key=lambda x: -x[1])]
    ranking = orden_articulos(d.trozos, np.array(orden))
    contexto = [{"aid": d.trozos.articulos_por_trozo[i][0], "texto": d.trozos.embebidos[i]} for i in orden[:CONTEXTO]]
    return resultado(ranking, contexto, t0)


def recencia(pregunta: str, lam: float = 0.15) -> dict:
    t0 = time.perf_counter()
    fecha, explicita = fecha_referencia(pregunta)
    orden = rerank_articulos(pregunta, candidatos_hibridos(pregunta)[:40])
    rescored = []
    for aid, s in orden:
        a = articulos()[aid]
        anio_doc = int(a.version_desde[:4])
        if explicita:
            penal = abs(fecha.year - anio_doc) / 36
        else:
            penal = (HOY.year - anio_doc) / 36
        rescored.append((aid, s - lam * penal))
    rescored.sort(key=lambda x: -x[1])
    ranking = [a for a, _ in rescored]
    return resultado(ranking, pasajes(ranking), t0, fecha_ref=fecha.isoformat())


def linea_vigencia(aid: str, fecha: date) -> tuple[str, str]:
    return vigencia.linea(articulos()[aid], fecha)


def propuesto(pregunta: str, vigencia: bool = True) -> dict:
    t0 = time.perf_counter()
    fecha, explicita = fecha_referencia(pregunta)
    orden = rerank_articulos(pregunta, candidatos_hibridos(pregunta)[:40])
    ranking = [a for a, _ in orden]
    contexto = []
    for aid, s in orden[:CONTEXTO]:
        p = {"aid": aid, "texto": texto_articulo(aid), "puntaje": round(s, 4)}
        if vigencia:
            p["estado"], p["vigencia"] = linea_vigencia(aid, fecha)
        contexto.append(p)
    return resultado(ranking, contexto, t0, fecha_ref=fecha.isoformat(), fecha_explicita=explicita,
                     puntajes=[round(s, 4) for _, s in orden[:TOP_ARTICULOS]])


CORRECTOR = (
    "Eres un corrector ortográfico. Detecta errores ortográficos y contracciones en preguntas.\n\n"
    "INSTRUCCIÓN: Responde ÚNICAMENTE con JSON válido, sin texto adicional.\n\nFORMATO:\n"
    '{\n    "has_spelling_errors": true/false,\n    "corrected_question": "pregunta corregida" o null\n}\n\n'
    "QUÉ CORREGIR:\n- Acentos: que→qué, cual→cuál, como→cómo, donde→dónde\n- Contracciones: q→qué, xq→por qué, pa→para, d→de\n"
    "- Signos: agregar ¿ ?\n- Preservar: DNI, CTS, ONU\n\nRESPONDE SOLO JSON."
)
EXTRACTOR = """Eres un experto en análisis de texto legal. Tu tarea es extraer ÚNICAMENTE los metadatos variables mencionados explícitamente en la pregunta.

METADATOS VARIABLES A EXTRAER:
- article_number: Número de artículo (ej: "artículo 2" → 2, "artículo 139" → 139)
- title: Norma específica (ej: "DS 003-97-TR", "Ley 29783", "D. Leg. 713")
- year: Año específico (ej: "1997", "2015")

REGLAS ESTRICTAS:
1. Solo extrae información EXPLÍCITAMENTE mencionada
2. Si no se menciona específicamente, deja el campo como null
3. Responde SOLO con el JSON válido con las claves article_number, title y year

EJEMPLOS:
- "¿Qué dice el artículo 16 del Decreto Supremo 003-97-TR?" → {{"article_number": 16, "title": "DS 003-97-TR", "year": null}}
- "¿Qué normas laborales de 1991 existen?" → {{"article_number": null, "title": null, "year": 1991}}
- "¿Cómo funciona el despido arbitrario?" → {{"article_number": null, "title": null, "year": null}}

Pregunta: {question}
Extrae SOLO los metadatos variables mencionados:"""


def _canon(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"decreto\s+supremo|d\.\s*s\.", "ds", texto)
    texto = re.sub(r"decreto\s+legislativo|d\.\s*leg\.?|dleg", "dleg", texto)
    texto = re.sub(r"resolucion\s+ministerial|r\.\s*m\.", "rm", texto)
    texto = re.sub(r"decreto\s+de\s+urgencia", "du", texto)
    texto = re.sub(r"n\s*[°º.]", " ", texto)
    return re.sub(r"[^a-z0-9]", "", texto)


@lru_cache
def titulos_validos() -> dict[str, str]:
    return {_canon(n.corto): n.corto for n in normas_id().values()}


def tacna(pregunta: str, modelo_emb: str = "minilm", top_k: int = 15, top_n: int = 5) -> dict:
    t0 = time.perf_counter()
    llamadas, tokens = 0, 0
    crudo, uso = ollama(LLM_ENRUTADOR, f"Analiza esta pregunta: '{pregunta}'", CORRECTOR, json_mode=True)
    llamadas, tokens = llamadas + 1, tokens + uso["tokens_in"] + uso["tokens_out"]
    datos = extraer_json(crudo) or {}
    consulta = datos.get("corrected_question") if datos.get("has_spelling_errors") and datos.get("corrected_question") else pregunta
    crudo, uso = ollama(LLM_ENRUTADOR, EXTRACTOR.format(question=consulta), json_mode=True)
    llamadas, tokens = llamadas + 1, tokens + uso["tokens_in"] + uso["tokens_out"]
    filtros = extraer_json(crudo) or {}
    validos = {}
    if isinstance(filtros.get("title"), str) and _canon(filtros["title"]) in titulos_validos():
        validos["title"] = titulos_validos()[_canon(filtros["title"])]
    try:
        if filtros.get("article_number") is not None:
            validos["article_number"] = int(filtros["article_number"])
    except (TypeError, ValueError):
        pass
    try:
        if filtros.get("year") is not None and 1950 <= int(filtros["year"]) <= HOY.year:
            validos["year"] = int(filtros["year"])
    except (TypeError, ValueError):
        pass
    d = denso_minilm_crudo() if modelo_emb == "minilm" else denso_bge_crudo()
    estrategias = []
    for filtro in (validos, {k: v for k, v in validos.items() if k != "title"},
                   {k: v for k, v in validos.items() if k not in ("title", "year")}, {}):
        if filtro not in estrategias:
            estrategias.append(filtro)
    usada, top = {}, np.array([], dtype=int)
    for filtro in estrategias:
        mascara = np.array([all(m.get(k) == v for k, v in filtro.items()) for m in d.trozos.meta]) if filtro else None
        if mascara is not None and not mascara.any():
            continue
        top = d.buscar(consulta, k=top_k, mascara=mascara)
        usada = filtro
        if len(top):
            break
    textos = [d.trozos.textos[i] for i in top]
    puntajes = rerankear(consulta, textos)
    orden = [i for i, _ in sorted(zip(top, puntajes), key=lambda x: -x[1])]
    ranking = orden_articulos(d.trozos, np.array(orden))
    contexto = [{"aid": d.trozos.articulos_por_trozo[i][0], "texto": d.trozos.textos[i]} for i in orden[:top_n]]
    return resultado(ranking, contexto, t0, filtros=usada, llm_llamadas=llamadas, llm_tokens=tokens)


SISTEMAS = {
    "ingenuo": ingenuo,
    "bm25": bm25,
    "denso": denso,
    "denso_sin_cabecera": denso_sin_cabecera,
    "hibrido": hibrido,
    "hibrido_rr": hibrido_rr,
    "hibrido_rr_trozos": hibrido_rr_trozos,
    "tacna_minilm": lambda q: tacna(q, "minilm"),
    "tacna_bge": lambda q: tacna(q, "bge"),
    "recencia": recencia,
    "propuesto": propuesto,
}
