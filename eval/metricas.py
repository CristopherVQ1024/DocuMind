import hashlib
import math
import re

import numpy as np
from scipy import stats

KS = (1, 3, 5, 10)


def particion(qid: str) -> str:
    return "dev" if int(hashlib.sha1(qid.encode()).hexdigest(), 16) % 5 == 0 else "test"


def recuperacion(ranking: list[str], gold: list[str]) -> dict:
    if not gold:
        return {}
    pos = {aid: i + 1 for i, aid in enumerate(ranking)}
    rangos = sorted(pos[g] for g in gold if g in pos)
    fila = {}
    for k in KS:
        dentro = [r for r in rangos if r <= k]
        fila[f"hit@{k}"] = float(bool(dentro))
        fila[f"recall@{k}"] = len(dentro) / len(gold)
    fila["mrr@10"] = 1 / rangos[0] if rangos and rangos[0] <= 10 else 0.0
    dcg = sum(1 / math.log2(r + 1) for r in rangos if r <= 10)
    idcg = sum(1 / math.log2(i + 2) for i in range(min(len(gold), 10)))
    fila["ndcg@10"] = dcg / idcg
    fila["todos@10"] = float(all(g in pos and pos[g] <= 10 for g in gold))
    return fila


def numero_norma(texto: str) -> str:
    m = re.search(r"(\d{2,5}(?:-\d{2,4})?(?:-[A-Z]{2,})?)", texto or "")
    return m.group(1) if m else ""


def respuesta(fila_q: dict, salida: dict, aids_contexto: list[str]) -> dict:
    citas = [c for c in salida.get("citas_aid", []) if c]
    gold = set(fila_q["gold"])
    fila = {}
    if gold:
        fila["cita_precision"] = len([c for c in citas if c in gold]) / len(citas) if citas else 0.0
        fila["cita_recall"] = len(gold & set(citas)) / len(gold)
    estado = salida.get("estado", "")
    if fila_q["tipo"] in ("temporal", "premisa_falsa"):
        fila["estado_ok"] = float(estado == fila_q["estado"])
    if fila_q["tipo"] == "rastreo" and fila_q.get("norma_modificatoria"):
        objetivo = numero_norma(fila_q["norma_modificatoria"])
        fila["rastreo_ok"] = float(bool(objetivo) and objetivo in (salida.get("respuesta", "") + " " + salida.get("norma_modificatoria", "")))
    fila["abstiene"] = float(bool(salida.get("abstiene")))
    fila["debe_abstener"] = float(bool(fila_q.get("abstener")))
    return fila


def f1_abstencion(filas: list[dict]) -> dict:
    tp = sum(f["abstiene"] and f["debe_abstener"] for f in filas)
    fp = sum(f["abstiene"] and not f["debe_abstener"] for f in filas)
    fn = sum(not f["abstiene"] and f["debe_abstener"] for f in filas)
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return {"abst_precision": p, "abst_recall": r, "abst_f1": 2 * p * r / (p + r) if p + r else 0.0}


def bootstrap_ic(a: np.ndarray, b: np.ndarray, n: int = 10000, semilla: int = 7) -> tuple[float, float, float]:
    rng = np.random.default_rng(semilla)
    d = a - b
    medias = d[rng.integers(0, len(d), (n, len(d)))].mean(axis=1)
    return float(d.mean()), float(np.percentile(medias, 2.5)), float(np.percentile(medias, 97.5))


def wilcoxon(a: np.ndarray, b: np.ndarray) -> float:
    if np.allclose(a, b):
        return 1.0
    return float(stats.wilcoxon(a, b, zero_method="pratt").pvalue)


def mcnemar(a: np.ndarray, b: np.ndarray) -> float:
    n01 = int(((a == 1) & (b == 0)).sum())
    n10 = int(((a == 0) & (b == 1)).sum())
    if n01 + n10 == 0:
        return 1.0
    return float(stats.binomtest(n01, n01 + n10, 0.5).pvalue)


def holm(pvalores: dict[str, float]) -> dict[str, float]:
    orden = sorted(pvalores, key=pvalores.get)
    m = len(orden)
    ajust, previo = {}, 0.0
    for i, k in enumerate(orden):
        previo = max(previo, min(1.0, (m - i) * pvalores[k]))
        ajust[k] = previo
    return ajust


def cohen_kappa(a: list, b: list) -> float:
    etiquetas = sorted(set(a) | set(b))
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(e) / n) * (b.count(e) / n) for e in etiquetas)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def kappa_ponderado(a: list[int], b: list[int], niveles: int = 3) -> float:
    o = np.zeros((niveles, niveles))
    for x, y in zip(a, b):
        o[x, y] += 1
    o /= o.sum()
    e = np.outer(o.sum(axis=1), o.sum(axis=0))
    i, j = np.indices((niveles, niveles))
    w = ((i - j) / (niveles - 1)) ** 2
    return float(1 - (w * o).sum() / (w * e).sum()) if (w * e).sum() else 1.0
