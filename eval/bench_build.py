import argparse
import random
import re
from collections import defaultdict
from datetime import date

from common import DATA, HOY, articulos, cita, corpus, escribir_jsonl, extraer_json, normas_id, redactar

CUOTAS = {"literal": 120, "temporal": 120, "rastreo": 90, "multisalto": 90, "premisa_falsa": 90, "sin_respuesta": 90}
SISTEMA = (
    "Eres un especialista en derecho laboral peruano que redacta preguntas de evaluación para un asistente legal. "
    "Escribes en español del Perú, como preguntaría un trabajador, un empleador o un estudiante de derecho. "
    "Nunca copias frases literales del artículo: parafraseas. Respondes solo con JSON válido."
)
FUERA = [
    "régimen de construcción civil y sus jornales", "trabajadoras y trabajadores del hogar", "régimen laboral agrario y su bonificación",
    "trabajadores mineros y jubilación minera", "régimen del contrato administrativo de servicios CAS en el Estado", "Ley del Servicio Civil y servidores públicos",
    "carrera pública magisterial de docentes estatales", "pensión de jubilación de la ONP y requisitos de aportes", "retiro del 95.5 % de fondos de AFP",
    "impuesto a la renta de cuarta categoría de independientes", "visas de trabajo y calidad migratoria en Migraciones", "seguro de desempleo estatal",
    "derecho laboral en Chile o Colombia", "contratos de locación de servicios regulados por el Código Civil", "pescadores artesanales y su régimen",
    "trabajadores portuarios", "futbolistas profesionales y sus contratos", "periodistas y su jornada", "médicos residentes del SERUMS",
    "régimen de la microempresa REMYPE y su inscripción", "beneficios del personal militar y policial", "licencia sindical en el sector público",
]


REDACTOR = [""]


def pool() -> list:
    salida = []
    for a in articulos().values():
        if ":b" in a.id and a.texto.lower().startswith(("aprobar", "apruébese", "apruebase", "derógase", "deróguese")):
            continue
        if len(a.texto) < 220 or len(a.texto) > 6000:
            continue
        if a.texto.lower().startswith(("el presente decreto", "la presente ley entra", "refrendo", "dado en la casa")):
            continue
        salida.append(a)
    return salida


def estratificado(articulos_: list, n: int, rnd: random.Random) -> list:
    por_tema = defaultdict(list)
    for a in articulos_:
        por_tema[normas_id()[a.norma_id].tema].append(a)
    for lista in por_tema.values():
        rnd.shuffle(lista)
    elegidos = []
    while len(elegidos) < n and any(por_tema.values()):
        for tema in sorted(por_tema):
            if por_tema[tema] and len(elegidos) < n:
                elegidos.append(por_tema[tema].pop())
    return elegidos


def bloque(a, extra: str = "") -> str:
    n = normas_id()[a.norma_id]
    return f"ID: {a.id}\nNorma: {n.corto} ({n.nombre[:140]})\n{a.etiqueta}. {a.titulo_articulo}\nTexto: {a.texto[:2200]}{extra}"


def pedir(instruccion: str, items: list[str]) -> list[dict]:
    prompt = instruccion + "\n\nDevuelve una lista JSON con un objeto por artículo, en el mismo orden, con las claves indicadas.\n\n" + "\n\n---\n\n".join(items)
    texto, REDACTOR[0] = redactar(prompt, SISTEMA)
    datos = extraer_json(texto)
    if isinstance(datos, dict):
        datos = next((v for v in datos.values() if isinstance(v, list)), [datos])
    return datos if isinstance(datos, list) else []


def emparejar(ids: list[str], datos: list[dict], clave: str = "id") -> list[dict]:
    def norm(v):
        v = str(v)
        return re.sub(r"\D", "", v) if clave == "par" else v

    por_id = {norm(d.get(clave)): d for d in datos if isinstance(d, dict)}
    if all(i in por_id for i in ids):
        return [por_id[i] for i in ids]
    if len(datos) == len(ids) and not por_id.keys() & set(ids):
        return datos
    return [por_id.get(i, {}) for i in ids]


def en_lotes(seq: list, n: int):
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def item(tipo: str, pregunta: str, respuesta: str, gold: list[str], estado: str, **extra) -> dict:
    return {"tipo": tipo, "pregunta": pregunta.strip(), "respuesta_ref": respuesta.strip(), "gold": gold, "estado": estado,
            "fecha_ref": extra.pop("fecha_ref", None), "abstener": estado in ("fuera_corpus",), "redactor": REDACTOR[0], **extra}


def literal(rnd, usados) -> list[dict]:
    elegidos = estratificado([a for a in pool() if a.id not in usados and a.estado != "derogado"], CUOTAS["literal"], rnd)
    salida = []
    for lote in en_lotes(elegidos, 6):
        explicita = [rnd.random() < 0.3 for _ in lote]
        items = [bloque(a, "\nModo: " + ("menciona la norma y el número de artículo" if e else "no menciones el número de artículo ni la norma")) for a, e in zip(lote, explicita)]
        datos = pedir(
            "Para cada artículo escribe una pregunta concreta que se responda con ese artículo y una respuesta de referencia de una o dos oraciones basada solo en el texto. "
            "Respeta el Modo indicado. Claves: id, pregunta, respuesta.", items)
        for a, e, d in zip(lote, explicita, emparejar([a.id for a in lote], datos)):
            if d.get("pregunta"):
                salida.append(item("literal", d["pregunta"], d.get("respuesta", ""), [a.id], "vigente" if a.estado != "derogado" else "derogado", cita_explicita=e))
                usados.add(a.id)
    return salida


def fecha_media(anio: int) -> str:
    return date(anio, 7, 1).isoformat()


def temporal(rnd, usados) -> list[dict]:
    candidatos = [a for a in pool() if a.estado == "modificado" and a.id not in usados]
    previos, posteriores, inexistentes = [], [], []
    for a in candidatos:
        e, v = int(a.existe_desde[:4]), int(a.version_desde[:4])
        if v - e >= 2:
            previos.append((a, rnd.randint(e + 1, v - 1)))
        if v < HOY.year:
            posteriores.append((a, rnd.randint(v + 1 if v + 1 < HOY.year else v, HOY.year)))
        if a.existe_desde != normas_id()[a.norma_id].publicada and int(a.existe_desde[:4]) - int(normas_id()[a.norma_id].publicada[:4]) >= 2:
            inexistentes.append((a, rnd.randint(int(normas_id()[a.norma_id].publicada[:4]) + 1, int(a.existe_desde[:4]) - 1)))
    rnd.shuffle(previos), rnd.shuffle(posteriores), rnd.shuffle(inexistentes)
    elegidos = [(a, y, "sin_version") for a, y in previos[:50]]
    vistos = {a.id for a, _, _ in elegidos}
    elegidos += [(a, y, "no_existia") for a, y in inexistentes if a.id not in vistos][:20]
    vistos |= {a.id for a, _, _ in elegidos}
    elegidos += [(a, y, "vigente") for a, y in posteriores if a.id not in vistos][: CUOTAS["temporal"] - len(elegidos)]
    salida = []
    for lote in en_lotes(elegidos, 6):
        items = [bloque(a, f"\nAño de referencia: {y}") for a, y, _ in lote]
        datos = pedir(
            "Para cada artículo escribe una pregunta sobre su contenido que fije explícitamente el año de referencia indicado, "
            "por ejemplo «en 2015, ¿cuántos días…?» o «según la norma vigente en 2012…». No menciones el número de artículo. Claves: id, pregunta.", items)
        for (a, y, estado), d in zip(lote, emparejar([a.id for a, _, _ in lote], datos)):
            if not d.get("pregunta"):
                continue
            ult = max((n for n in a.notas if n.fecha and n.accion in ("modificado", "incorporado")), key=lambda n: n.fecha, default=None)
            if estado == "vigente":
                ref = f"La redacción vigente en {y} es la actual, que rige desde {a.version_desde}. {a.texto[:300]}"
            elif estado == "sin_version":
                ref = f"La redacción actual del {cita(a)} rige desde {a.version_desde} ({ult.norma_por if ult else 'modificación'}). El texto aplicable en {y} no está en el corpus."
            else:
                ref = f"El {cita(a)} fue incorporado el {a.existe_desde}; en {y} esa disposición no existía."
            salida.append(item("temporal", d["pregunta"], ref, [a.id], estado, fecha_ref=fecha_media(y)))
            usados.add(a.id)
    return salida


def rastreo(rnd, usados) -> list[dict]:
    candidatos = []
    for a in pool():
        notas = [n for n in a.notas if n.norma_por and n.fecha and n.accion in ("modificado", "incorporado", "derogado")]
        if notas and a.id not in usados:
            candidatos.append((a, max(notas, key=lambda n: n.fecha)))
    rnd.shuffle(candidatos)
    elegidos = candidatos[: CUOTAS["rastreo"]]
    salida = []
    REDACTOR[0] = "plantilla"
    verbos = {"modificado": "modificó", "incorporado": "incorporó", "derogado": "derogó"}
    for a, n in elegidos:
        norma = normas_id()[a.norma_id].corto
        sumilla = a.titulo_articulo.strip(" .:").lower()
        explicita = not sumilla or rnd.random() < 0.5
        if explicita:
            objeto = f"el {a.etiqueta.lower() if a.etiqueta.startswith('Artículo') else a.etiqueta} del {norma}"
        else:
            objeto = f"la disposición del {norma} sobre «{sumilla}»"
        pregunta = rnd.choice([f"¿Qué norma {verbos[n.accion]} {objeto}?", f"¿Mediante qué norma y en qué fecha se {verbos[n.accion]} {objeto}?"])
        ref = f"El {cita(a)} fue {n.accion} por {n.norma_por} ({n.por}), publicado el {n.fecha}."
        salida.append(item("rastreo", pregunta, ref, [a.id], "vigente" if a.estado != "derogado" else "derogado",
                           norma_modificatoria=n.norma_por, fecha_cambio=n.fecha, cita_explicita=explicita))
        usados.add(a.id)
    return salida


RE_REF_PROPIA = re.compile(r"art[íi]culos?\s+(\d+(?:-[A-Z])?)\s+(?:de\s+la\s+presente|del\s+presente|de\s+esta)\b", re.I)
RE_REF_NORMA = re.compile(r"art[íi]culo\s+(\d+(?:-[A-Z])?)\s+(?:de\s+la|del)\s+(Ley|Decreto\s+Supremo|Decreto\s+Legislativo)\s*N?\s*[°º]?\s*([\d][\d\-]*(?:-?[A-Z]{2,})?)", re.I)


def referencias(a) -> list[str]:
    por_corto = {n.corto.replace(" ", "").lower(): n for n in corpus()}
    destinos = []
    for m in RE_REF_PROPIA.finditer(a.texto):
        destinos.append(f"{a.norma_id}:{m.group(1)}")
    for m in RE_REF_NORMA.finditer(a.texto):
        tipo = {"ley": "Ley", "decreto supremo": "DS", "decreto legislativo": "D.Leg."}[re.sub(r"\s+", " ", m.group(2)).lower()]
        n = por_corto.get(f"{tipo}{m.group(3)}".replace(" ", "").lower())
        if n:
            destinos.append(f"{n.id}:{m.group(1)}")
    return [d for d in dict.fromkeys(destinos) if d in articulos() and d != a.id]


def multisalto(rnd, usados) -> list[dict]:
    pares = []
    for a in pool():
        for destino in referencias(a):
            b = articulos()[destino]
            if len(b.texto) >= 150 and a.id not in usados and "derogado" not in (a.estado, b.estado):
                pares.append((a, b))
    rnd.shuffle(pares)
    vistos, elegidos = set(), []
    for a, b in pares:
        if a.id in vistos or b.id in vistos:
            continue
        vistos |= {a.id, b.id}
        elegidos.append((a, b))
        if len(elegidos) == CUOTAS["multisalto"]:
            break
    salida = []
    for lote in en_lotes(elegidos, 4):
        items = [f"PAR {i + 1}\nArtículo A (remite a B):\n{bloque(a)}\n\nArtículo B:\n{bloque(b)}" for i, (a, b) in enumerate(lote)]
        datos = pedir(
            "Cada par tiene un artículo A que remite al artículo B. Escribe una pregunta práctica cuya respuesta completa exija combinar la regla de A con el contenido de B, "
            "sin mencionar números de artículo. Da una respuesta de referencia de dos oraciones. Claves: par, pregunta, respuesta.", items)
        for (a, b), d in zip(lote, emparejar([str(i + 1) for i in range(len(lote))], datos, "par")):
            if d.get("pregunta"):
                salida.append(item("multisalto", d["pregunta"], d.get("respuesta", ""), [a.id, b.id], "vigente"))
                usados |= {a.id, b.id}
    return salida


RE_CIFRA = re.compile(r"(?<![\d.,/-])\(?(\d{1,3})\)?\s*(?:\([a-zé ]+\)\s*)?(días hábiles|días calendario|días naturales|días|horas|meses|años|remuneraciones|por ciento|UIT)\b")


def premisa_falsa(rnd, usados) -> list[dict]:
    derogados = [a for a in articulos().values() if a.estado == "derogado" and len(a.texto) > 120]
    salida = []
    for lote in en_lotes(derogados, 6):
        items = [bloque(a, f"\nDerogado el {a.derogado_desde}") for a in lote]
        datos = pedir(
            "Cada artículo está derogado. Escribe una pregunta que lo trate como si siguiera vigente hoy, por ejemplo «según el artículo X de la norma Y, ¿cuál es el plazo…?». "
            "Puedes mencionar la norma y el artículo. Claves: id, pregunta.", items)
        for a, d in zip(lote, emparejar([a.id for a in lote], datos)):
            if d.get("pregunta"):
                ref = f"El {cita(a)} fue derogado el {a.derogado_desde}; la premisa de que sigue vigente es falsa."
                salida.append(item("premisa_falsa", d["pregunta"], ref, [a.id], "derogado", subtipo="derogada"))
                usados.add(a.id)
    resto = CUOTAS["premisa_falsa"] - len(salida)
    candidatos = []
    for a in pool():
        if a.id in usados or a.estado == "derogado":
            continue
        m = RE_CIFRA.search(a.texto)
        if m:
            n = int(m.group(1))
            falso = n * 2 if n <= 10 else n + 15 if n < 100 else n // 2
            candidatos.append((a, f"{n} {m.group(2)}", f"{falso} {m.group(2)}", str(falso)))
    por_id = {c[0].id: c for c in candidatos}
    elegidos = [por_id[a.id] for a in estratificado([c[0] for c in candidatos], len(candidatos), rnd)]
    for lote in en_lotes(elegidos, 6):
        if resto <= 0:
            break
        items = [bloque(a, f"\nDato correcto: {bien}\nDato falso que la pregunta debe dar por cierto: {mal}") for a, bien, mal, _ in lote]
        datos = pedir(
            "Para cada artículo escribe una pregunta de alguien mal informado que dé por cierto el dato falso indicado, escrito tal cual con su número, "
            "por ejemplo «Si el plazo es de 45 días, ¿desde cuándo se cuenta?». No menciones el número de artículo ni el dato correcto. Claves: id, pregunta.", items)
        for (a, bien, mal, cifra), d in zip(lote, emparejar([c[0].id for c in lote], datos)):
            pregunta = d.get("pregunta", "")
            if resto > 0 and re.search(rf"(?<!\d){cifra}(?!\d)", pregunta):
                ref = f"La premisa es falsa: no son {mal}. Según el {cita(a)}, son {bien}."
                salida.append(item("premisa_falsa", pregunta, ref, [a.id], "premisa_falsa", subtipo="dato_alterado", dato_falso=mal, dato_correcto=bien))
                usados.add(a.id)
                resto -= 1
    return salida


def sin_respuesta(rnd) -> list[dict]:
    temas = FUERA * 9
    rnd.shuffle(temas)
    salida = []
    for lote in en_lotes(temas, 10):
        if len(salida) >= CUOTAS["sin_respuesta"]:
            break
        prompt = (
            "Escribe una pregunta concreta y realista por cada tema de la lista. Son temas que NO regula el régimen laboral privado general peruano "
            "(o que pertenecen a otros regímenes, sectores o países). Varía el estilo y evita mencionar normas. Devuelve una lista JSON de objetos con claves tema y pregunta.\n\n"
            + "\n".join(f"- {t}" for t in lote)
        )
        texto, REDACTOR[0] = redactar(prompt, SISTEMA, temperatura=0.6)
        datos = extraer_json(texto)
        if isinstance(datos, dict):
            datos = next((v for v in datos.values() if isinstance(v, list)), [])
        for d in datos or []:
            if d.get("pregunta") and len(salida) < CUOTAS["sin_respuesta"]:
                salida.append(item("sin_respuesta", d["pregunta"], "La pregunta está fuera del corpus; el sistema debe abstenerse.", [], "fuera_corpus", tema=d.get("tema", "")))
    return salida


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", nargs="*", default=list(CUOTAS))
    args = ap.parse_args()
    rnd = random.Random(42)
    usados: set[str] = set()
    pasos = {"literal": literal, "temporal": temporal, "rastreo": rastreo, "multisalto": multisalto, "premisa_falsa": premisa_falsa}
    filas = []
    for tipo in CUOTAS:
        if tipo not in args.solo:
            continue
        nuevos = sin_respuesta(rnd) if tipo == "sin_respuesta" else pasos[tipo](rnd, usados)
        print(f"{tipo}: {len(nuevos)}", flush=True)
        filas += nuevos
    for i, f in enumerate(filas, 1):
        f["qid"] = f"q{i:04d}"
        f["validado"] = False
    escribir_jsonl(DATA / "benchmark.jsonl", filas)
    print(f"total: {len(filas)} -> {DATA / 'benchmark.jsonl'}")


if __name__ == "__main__":
    main()
