import json
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
from scipy import sparse

from common import CACHE, articulos, corpus, encabezado, normas_id

EMB_BGE = "BAAI/bge-m3"
EMB_MINILM = "sentence-transformers/all-MiniLM-L6-v2"
RERANKER = "jinaai/jina-reranker-v2-base-multilingual"
STOP = set(
    "a al algo ante antes asi aun cada como con contra cual cuales cuando de del desde donde dos e el ella ellas ello ellos en entre era es esa esas "
    "ese eso esos esta estas este esto estos fue fueron ha han hasta hay la las le les lo los mas me mi mientras muy ni no nos o otra otras otro otros "
    "para pero por porque que quien se sea segun ser si sin sobre su sus tal tambien tiene tienen todo todos tu un una uno unos y ya cual cuanto cuantos "
    "debe deben puede pueden mi mis".split()
)


@dataclass
class Trozos:
    nombre: str
    ids: list[str]
    textos: list[str]
    embebidos: list[str]
    articulos_por_trozo: list[list[str]]
    meta: list[dict] = field(default_factory=list)


@lru_cache
def tokenizador():
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(EMB_BGE)


def partir_tokens(texto: str, tam: int, solape: int) -> list[str]:
    tok = tokenizador()
    ids = tok(texto, add_special_tokens=False, return_offsets_mapping=True)
    offs = ids["offset_mapping"]
    if len(offs) <= tam:
        return [texto]
    piezas, inicio = [], 0
    while inicio < len(offs):
        fin = min(inicio + tam, len(offs))
        piezas.append(texto[offs[inicio][0] : offs[fin - 1][1]].strip())
        if fin == len(offs):
            break
        inicio = fin - solape
    return piezas


def anio(fecha: str) -> int | None:
    return int(fecha[:4]) if fecha else None


@lru_cache
def trozos_articulo(tam: int = 250, solape: int = 30) -> Trozos:
    ids, textos, emb, arts, meta = [], [], [], [], []
    for norma in corpus():
        for a in norma.articulos:
            cabeza = encabezado(a)
            for k, parte in enumerate(partir_tokens(a.texto, tam, solape)):
                ids.append(f"{a.id}#{k}")
                textos.append(parte)
                emb.append(f"{cabeza}\n{parte}")
                arts.append([a.id])
                num = re.match(r"(\d+)", a.numero)
                meta.append({
                    "source": "Compendio de normas laborales del régimen privado",
                    "document_type": norma.tipo.lower(),
                    "title": norma.corto,
                    "topic": norma.tema,
                    "year": anio(norma.publicada),
                    "article_number": int(num.group(1)) if num and ":b" not in a.id else None,
                })
    return Trozos(f"art{tam}-{solape}", ids, textos, emb, arts, meta)


@lru_cache
def trozos_ingenuos(tam: int = 1000, solape: int = 200) -> Trozos:
    ids, textos, arts = [], [], []
    for norma in corpus():
        texto, spans = "", []
        for a in norma.articulos:
            ini = len(texto)
            texto += f"{a.etiqueta}. {a.titulo_articulo + '. ' if a.titulo_articulo else ''}{a.texto}\n"
            spans.append((ini, len(texto), a.id))
        inicio, k = 0, 0
        while inicio < len(texto):
            fin = min(inicio + tam, len(texto))
            solapados = [(min(fin, f) - max(inicio, i), aid) for i, f, aid in spans if i < fin and f > inicio]
            solapados.sort(reverse=True)
            ids.append(f"{norma.id}#{k}")
            textos.append(texto[inicio:fin])
            arts.append([aid for _, aid in solapados])
            k += 1
            if fin == len(texto):
                break
            inicio = fin - solape
    return Trozos(f"naive{tam}-{solape}", ids, textos, textos, arts)


def normalizar(texto: str) -> list[str]:
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return [t for t in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", texto) if t not in STOP and len(t) > 1]


class BM25:
    def __init__(self, textos: list[str], k1: float = 1.2, b: float = 0.75):
        docs = [normalizar(t) for t in textos]
        self.vocab = {}
        filas, cols, vals = [], [], []
        for i, d in enumerate(docs):
            for t, c in Counter(d).items():
                j = self.vocab.setdefault(t, len(self.vocab))
                filas.append(i), cols.append(j), vals.append(c)
        tf = sparse.csr_matrix((vals, (filas, cols)), shape=(len(docs), len(self.vocab)), dtype=np.float32)
        largos = np.array([len(d) for d in docs], dtype=np.float32)
        df = np.bincount(tf.indices, minlength=len(self.vocab))
        self.idf = np.log(1 + (len(docs) - df + 0.5) / (df + 0.5)).astype(np.float32)
        norma = k1 * (1 - b + b * largos / max(largos.mean(), 1))
        tf = tf.tocoo()
        pesos = tf.data * (k1 + 1) / (tf.data + norma[tf.row])
        self.matriz = sparse.csr_matrix((pesos, (tf.row, tf.col)), shape=tf.shape).tocsc()

    def puntajes(self, consulta: str) -> np.ndarray:
        cols = [self.vocab[t] for t in normalizar(consulta) if t in self.vocab]
        if not cols:
            return np.zeros(self.matriz.shape[0], dtype=np.float32)
        sub = self.matriz[:, cols]
        return np.asarray(sub @ self.idf[cols]).ravel()


@lru_cache
def modelo_emb(nombre: str):
    import torch
    from sentence_transformers import SentenceTransformer

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA no disponible")
    m = SentenceTransformer(nombre, device="cuda", model_kwargs={"torch_dtype": torch.float16})
    m.max_seq_length = 1024 if "bge" in nombre else 256
    return m


def embeber(trozos: Trozos, modelo: str) -> np.ndarray:
    ruta = CACHE / f"emb-{trozos.nombre}-{modelo.split('/')[-1]}.npy"
    if ruta.exists():
        return np.load(ruta)
    m = modelo_emb(modelo)
    orden = np.argsort([len(t) for t in trozos.embebidos])
    vecs = m.encode([trozos.embebidos[i] for i in orden], batch_size=32, normalize_embeddings=True,
                    show_progress_bar=True, convert_to_numpy=True).astype(np.float32)
    salida = np.empty_like(vecs)
    salida[orden] = vecs
    np.save(ruta, salida)
    return salida


def embeber_consultas(textos: list[str], modelo: str) -> np.ndarray:
    return modelo_emb(modelo).encode(textos, batch_size=32, normalize_embeddings=True, convert_to_numpy=True).astype(np.float32)


@lru_cache
def reranker():
    import torch
    from sentence_transformers import CrossEncoder

    return CrossEncoder(RERANKER, trust_remote_code=True, device="cuda", max_length=1024,
                        model_kwargs={"torch_dtype": torch.float16})


def rerankear(consulta: str, textos: list[str]) -> list[float]:
    if not textos:
        return []
    puntajes = reranker().predict([(consulta, t) for t in textos], batch_size=16, show_progress_bar=False)
    return [float(s) for s in puntajes]


def texto_articulo(aid: str, limite: int = 2400) -> str:
    a = articulos()[aid]
    return f"{encabezado(a)}\n{a.texto[:limite]}"


def guardar_resumen():
    t = trozos_articulo()
    n = trozos_ingenuos()
    resumen = {"articulos": len(articulos()), "normas": len(normas_id()), "trozos_articulo": len(t.ids), "trozos_ingenuos": len(n.ids)}
    (CACHE / "resumen_indices.json").write_text(json.dumps(resumen, indent=1))
    return resumen
