import json
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.normas import CORPUS_DIR, Articulo, Nota, Norma

FUENTE = "Compendio de normas laborales del régimen privado"
URL = ""
CABECERA = re.compile(r"^\s*Compendio de normas laborales del régimen privado\s*\n\s*\d+\s*\n")
TIPOS = r"(?:DECRETO\s+SUPREMO|DECRETO\s+LEGISLATIVO|DECRETO\s+LEY|DECRETO\s+DE\s+URGENCIA|RESOLUCI[ÓO]N\s+MINISTERIAL|RESOLUCI[ÓO]N\s+DE\s+SUPERINTENDENCIA|RESOLUCI[ÓO]N\s+VICEMINISTERIAL|RESOLUCI[ÓO]N\s+DIRECTORAL|LEY|Decreto\s+Legislativo|Decreto\s+Supremo|Ley)"
RE_INDICE = re.compile(rf"({TIPOS})\s*(?:N\s*[°º]\s*)?([\d][\d\-A-Z]*)\s*\((\d{{1,2}})/(\d{{1,2}})/(\d{{2,4}})\)\s*(\d{{2,4}})\b")
RE_ARTICULO = re.compile(r"[“\"]?\s*\b(?:Art[íi]culo|ART[ÍI]CULO)\s+(\d+(?:\s?[-–]\s?[A-Z]\b)?|[ÚU]nico|ÚNICO)\s*[°º]?\s*(?:\.?\s*[-–]+\s*|\.\s+(?=[A-ZÁÉÍÓÚ¿“]))")
ORDINALES = "PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|SÉPTIMA|SÉTIMA|OCTAVA|NOVENA|DÉCIMA|UNDÉCIMA|DUODÉCIMA|DECIMOTERCERA|DECIMOCUARTA|DECIMOQUINTA|ÚNICA"
RE_DISPOSICION = re.compile(rf"[“\"]?\s*\b({ORDINALES}|{ORDINALES.title()})\s*\.?\s*[-–]+\s*")
RE_TITULO = re.compile(r"\bT[ÍI]TULO\s+([IVXL]+|PRELIMINAR)\b\.?\s*")
RE_CAPITULO = re.compile(r"\bCAP[ÍI]TULO\s+([IVXL]+|[ÚU]NICO)\b\.?\s*")
RE_CORTE = re.compile(r"\bT[ÍI]TULO\s+(?:[IVXL]+|PRELIMINAR)\b\.?\s*|\bCAP[ÍI]TULO\s+(?:[IVXL]+|[ÚU]NICO)\b\.?\s*")
RE_NOTA = re.compile(
    r"\(\*+\)\s*(?P<elem>[A-ZÁÉÍÓÚÑ][^()]{0,140}?)?\s*\b(?P<accion>[Mm]odificad|[Dd]erogad|[Ii]ncorporad|[Ss]ustituid|[Aa]dicionad|[Aa]gregad|[Pp]recisad|[Ss]uspendid|[Dd]ejad)[oa]s?\b"
    r"(?:\s+sin\s+efecto)?\s+(?:por|mediante|en\s+virtud\s+de|conforme(?:\s+a)?(?:\s+el|\s+la)?)\s+(?P<por>.{0,260}?)"
    r",?\s*(?:publicad[oa]s?|vigente)\s+(?:en\s+el\s+[^,]{0,45}?\s+)?el\s+"
    r"(?P<fecha>\d{1,2}\s*[-/.]\s*\d{1,2}\s*[-/.]\s*\d{2,4}|\d{1,2}\s+(?:de\s+)?[a-záéíóú]+\s+(?:de(?:l)?\s+)?\d{4})\s*\.?"
)
RE_CONCORDANCIA = re.compile(r"\(\*+\)\s*(?:De\s+conformidad|Confr|Concordancia|Mediante|Según|Ver|Nota)[^()]{0,400}?\d{4}\s*\.?")
RE_MARCA = re.compile(r"\s*\(\*+\)")
RE_NORMA_REF = re.compile(
    r"(Ley|Decreto\s+Legislativo|Decreto\s+Supremo|Decreto\s+de\s+Urgencia|Decreto\s+Ley|Resolución\s+Ministerial|Resolución\s+de\s+Superintendencia)\s*(?:N\s*[°º.]\s*s?\.?\s*)?(\d+(?:\s*-\s*\d+)*(?:\s*-\s*[A-Z]{2,})?)",
    re.I,
)
NOMBRES_NORMA = {"ley": "Ley", "decreto legislativo": "Decreto Legislativo", "decreto supremo": "Decreto Supremo",
                 "decreto de urgencia": "Decreto de Urgencia", "decreto ley": "Decreto Ley",
                 "resolución ministerial": "Resolución Ministerial", "resolución de superintendencia": "Resolución de Superintendencia"}
MESES = {m: i for i, m in enumerate(
    "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split(), 1)}
MESES["setiembre"] = 9
CORTO = {
    "DECRETO SUPREMO": "DS", "DECRETO LEGISLATIVO": "D. Leg.", "DECRETO LEY": "DL",
    "DECRETO DE URGENCIA": "DU", "RESOLUCIÓN MINISTERIAL": "RM", "RESOLUCIÓN DE SUPERINTENDENCIA": "RS",
    "RESOLUCIÓN VICEMINISTERIAL": "RVM", "RESOLUCIÓN DIRECTORAL": "RD", "LEY": "Ley",
}


def limpio(texto: str) -> str:
    texto = unicodedata.normalize("NFKC", texto).replace("­", "")
    texto = re.sub(r"\bT (?=[a-záéíóúñ]{2,})", "T", texto)
    texto = re.sub(r"(\w)-\s*\n\s*(?=[a-záéíóúñ])", r"\1", texto)
    return re.sub(r"\s+", " ", texto).strip()


def fecha_iso(texto: str) -> str:
    texto = texto.strip().lower()
    if m := re.match(r"(\d{1,2})\s*[-/.]\s*(\d{1,2})\s*[-/.]\s*(\d{2,4})", texto):
        d, mes, a = (int(x) for x in m.groups())
    elif m := re.match(r"(\d{1,2})\s+(?:de\s+)?([a-záéíóú]+)\s+(?:de(?:l)?\s+)?(\d{4})", texto):
        d, mes, a = int(m.group(1)), MESES.get(m.group(2), 0), int(m.group(3))
    else:
        return ""
    if a < 100:
        a += 1900 if a > 30 else 2000
    if not (1 <= mes <= 12 and 1 <= d <= 31):
        return ""
    return f"{a:04d}-{mes:02d}-{d:02d}"


def norma_ref(texto: str) -> str:
    m = RE_NORMA_REF.search(texto)
    if not m:
        return ""
    numero = re.sub(r"\s+", "", m.group(2))
    return f"{NOMBRES_NORMA[re.sub(r'\s+', ' ', m.group(1)).lower()]} N° {numero}"


def paginas(origen: Path) -> dict[int, str]:
    por_pagina: dict[int, list[str]] = defaultdict(list)
    for fila in json.loads(origen.read_text(encoding="utf-8")):
        por_pagina[fila["metadata"]["page"]].append(fila["content"])
    return {p: "\n".join(v) for p, v in por_pagina.items()}


def indice(pags: dict[int, str]) -> list[dict]:
    texto = "\n".join(CABECERA.sub("", pags[p]) for p in range(3, 23))
    texto = unicodedata.normalize("NFKC", texto)
    texto = re.sub(r"\bT (?=[a-záéíóúñ]{2,})", "T", texto)
    marcas = list(RE_INDICE.finditer(texto))
    entradas = []
    tema = "CONTRATACIÓN LABORAL"
    for i, m in enumerate(marcas):
        fin = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        resto = re.sub(r"\s+", " ", texto[m.end():fin]).strip()
        siguiente = ""
        partes = re.split(r"(?<=[.”])\s+", resto)
        while partes and re.fullmatch(r"[^a-záéíóúñ\d]{4,}", partes[-1]) and re.search(r"[A-ZÁÉÍÓÚÑ]{4,}", partes[-1]):
            siguiente = partes.pop() + (" " + siguiente if siguiente else "")
        tipo = re.sub(r"\s+", " ", m.group(1)).upper().replace("RESOLUCION", "RESOLUCIÓN")
        numero = m.group(2).rstrip("-")
        d, mes, a = int(m.group(3)), int(m.group(4)), int(m.group(5))
        a = a + (1900 if a > 30 else 2000) if a < 100 else a
        entradas.append(
            {
                "tipo": tipo,
                "numero": numero,
                "publicada": f"{a:04d}-{mes:02d}-{d:02d}",
                "pagina": int(m.group(6)),
                "nombre": " ".join(partes).strip(),
                "tema": tema.strip().capitalize(),
            }
        )
        if siguiente:
            tema = siguiente
    return entradas


def slug(tipo: str, numero: str) -> str:
    base = {"DS": "ds", "D. Leg.": "dleg", "DL": "dl", "DU": "du", "RM": "rm", "RS": "rs", "RVM": "rvm", "RD": "rd", "Ley": "ley"}
    return f"{base[CORTO[tipo]]}-{numero.lower()}"


def notas_de(texto: str) -> tuple[str, list[Nota]]:
    notas = []
    for m in RE_NOTA.finditer(texto):
        elem = (m.group("elem") or "").strip()
        elem = elem.split(".")[-1].strip() if "." in elem else elem
        accion = m.group("accion").lower()
        accion = {"modificad": "modificado", "derogad": "derogado", "incorporad": "incorporado", "sustituid": "modificado",
                  "adicionad": "incorporado", "agregad": "incorporado", "precisad": "precisado", "suspendid": "suspendido",
                  "dejad": "derogado"}[accion]
        por = re.sub(r"\s+", " ", m.group("por")).strip(" ,")
        notas.append(Nota(accion, elem[:60], por[:200], norma_ref(por), fecha_iso(m.group("fecha")), m.group(0).strip()[:400]))
    texto = RE_NOTA.sub(" ", texto)
    texto = RE_CONCORDANCIA.sub(" ", texto)
    texto = RE_MARCA.sub("", texto)
    return re.sub(r"\s+", " ", texto).strip(" “”\""), notas


def es_entero(elemento: str) -> bool:
    e = elemento.lower()
    return e == "" or e.startswith(("artículo", "articulo", "disposición", "disposicion"))


def vigencia(articulo: Articulo, publicada: str) -> None:
    cambios = [n.fecha for n in articulo.notas if n.fecha and n.accion in ("modificado", "incorporado")]
    entera_inc = [n.fecha for n in articulo.notas if n.fecha and n.accion == "incorporado" and es_entero(n.elemento)]
    derog = [n.fecha for n in articulo.notas if n.fecha and n.accion == "derogado" and es_entero(n.elemento)]
    articulo.existe_desde = min(entera_inc) if entera_inc else publicada
    articulo.version_desde = max(cambios + [articulo.existe_desde])
    if derog:
        articulo.derogado_desde = min(derog)
        articulo.estado = "derogado"
    elif cambios:
        articulo.estado = "modificado"


RE_PREVIO_INLINE = re.compile(r"\b(el|del|al|los|las|la|y|e|o|en|con|según|conforme|presente|mismo|dicho)\s*$")
RE_CITADO = re.compile(r"(siguientes?|t[ée]rminos|texto|redacci[óo]n|tenor|forma)\s*:\s*[“\"]?\s*$|:\s*[“\"]\s*$", re.I)
RE_SUMILLA =re.compile(r"((?:\b[A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ\-,;/()“”\"]*\.?\s+){1,16})$")


def unidades(texto: str) -> list[tuple[int, int, str, str]]:
    marcas = []
    for m in RE_ARTICULO.finditer(texto):
        previo = texto[max(0, m.start() - 25):m.start()]
        if RE_PREVIO_INLINE.search(previo) or RE_CITADO.search(texto[max(0, m.start() - 160):m.start()]):
            continue
        marcas.append((m.start(), m.end(), "art", m.group(1)))
    for m in RE_DISPOSICION.finditer(texto):
        previo = texto[max(0, m.start() - 3):m.start()].rstrip()
        if previo.endswith((".", ":", ";", ")", "”", "\"")) or m.start() == 0 or previo[-1:].isupper():
            marcas.append((m.start(), m.end(), "disp", m.group(1)))
    marcas.sort()
    return marcas


def sumilla_final(cuerpo: str) -> tuple[str, str]:
    m = RE_SUMILLA.search(cuerpo + " ")
    if not m:
        return cuerpo, ""
    cola = m.group(1).strip()
    palabras = [p for p in re.split(r"\s+", cola) if p]
    if len(palabras) < 2 and len(cola) < 8:
        return cuerpo, ""
    if re.fullmatch(r"(?:[IVXL]+\.?|[A-Z]\)?|N°|DS|TR)", cola):
        return cuerpo, ""
    return cuerpo[: m.start()].rstrip(), cola


def contexto(tramo: str, titulo: str, capitulo: str) -> tuple[str, str]:
    marcas = [(m.start(), "t", m.group(1)) for m in RE_TITULO.finditer(tramo)]
    marcas += [(m.start(), "c", m.group(1)) for m in RE_CAPITULO.finditer(tramo)]
    for _, clase, valor in sorted(marcas):
        if clase == "t":
            titulo, capitulo = f"Título {valor.capitalize() if valor == 'PRELIMINAR' else valor}", ""
        else:
            capitulo = f"Capítulo {valor.capitalize() if not valor.isupper() or len(valor) > 4 else valor}"
    return titulo, capitulo


RE_TITULO_SUELTO = re.compile(
    r"^([A-ZÁÉÍÓÚ][a-záéíóúñ]+(?:\s+(?:[a-záéíóúñ/]+|[A-Z]{2,}|N°|\d+|Ley|Estado|Ministerio|Trabajo|Empleo|Reglamento|Sunafil|SUNAFIL)){0,9}?)\s+"
    r"(?=(?:El|La|Los|Las|Lo|Para|En|Se|Toda|Todo|Todos|Cuando|Si|Es|Son|Por|Sin|Con|A|Al|Del|De|Mediante|Durante|Los/las|Las/los|Dentro)\s|\d+\.\d+\s|\d+\.\s|[a-z]\)\s)"
)


def titulo_de(cuerpo: str) -> tuple[str, str]:
    m = re.match(r"^([^.]{3,140}?)\s*[.:]\s+(?=[A-ZÁÉÍÓÚ0-9“\"(])", cuerpo)
    if m and not re.search(r"\b(el|la|los|las|de|del)\s*$", m.group(1)) and len(m.group(1).split()) <= 14 and not re.search(r"\b(es|son|será|serán|tiene|tienen|deberá|puede|podrá)\b", m.group(1)):
        return m.group(1).strip(), cuerpo[m.end():].strip()
    m = RE_TITULO_SUELTO.match(cuerpo)
    if m and len(m.group(1).split()) <= 10:
        return m.group(1).strip(), cuerpo[m.end():].strip()
    return "", cuerpo


def parsear(entrada: dict, texto: str, pagina_de) -> Norma:
    tipo_corto = CORTO[entrada["tipo"]]
    nid = slug(entrada["tipo"], entrada["numero"])
    norma = Norma(
        id=nid,
        nombre=entrada["nombre"],
        corto=f"{tipo_corto} {entrada['numero']}" if tipo_corto != "Ley" else f"Ley {entrada['numero']}",
        tipo=entrada["tipo"].capitalize(),
        tema=entrada["tema"],
        publicada=entrada["publicada"],
        url=URL,
        pagina=entrada["pagina"],
    )
    marcas = unidades(texto)
    vistos: dict[str, int] = {}
    bloque = grupo = 1
    titulo = capitulo = ""
    previo = 0
    sumilla = ""
    for i, (ini, fin, clase, num) in enumerate(marcas):
        cierre = marcas[i + 1][0] if i + 1 < len(marcas) else len(texto)
        titulo, capitulo = contexto(texto[previo:ini], titulo, capitulo)
        previo = ini
        propia, sumilla = sumilla, ""
        tramos = RE_CORTE.split(texto[fin:cierre])
        cuerpo = tramos[0]
        cola = tramos[-1] if len(tramos) > 1 and tramos[-1] else None
        if cola is None:
            cuerpo, sumilla = sumilla_final(cuerpo)
        else:
            _, sumilla = sumilla_final(cola)
        if "DISPOSICI" in sumilla.upper():
            sumilla = ""
        cuerpo, _ = notas_de(cuerpo)
        _, notas_todas = notas_de(texto[fin:cierre])
        if len(cuerpo) < 15:
            continue
        if clase == "art":
            numero = re.sub(r"\s", "", num).replace("–", "-")
            numero = "Único" if numero.lower() in ("único", "unico") else numero
            etiqueta = f"Artículo {numero}"
        else:
            numero = f"D-{num.upper()}"
            etiqueta = f"{num.capitalize()} disposición"
        reinicio = numero in ("1", "Único", "D-PRIMERA", "D-ÚNICA")
        if numero in vistos and not reinicio and norma.articulos:
            norma.articulos[-1].texto += " " + cuerpo
            norma.articulos[-1].notas += notas_todas
            continue
        if clase == "art":
            if numero in vistos:
                bloque += 1
                vistos = {k: v for k, v in vistos.items() if k.startswith("D-")}
        elif numero in vistos:
            grupo += 1
            vistos = {k: v for k, v in vistos.items() if not k.startswith("D-")}
        vistos[numero] = 1
        aid = f"{numero}@{bloque if clase == 'art' else grupo}"
        titulo_art, resto = titulo_de(cuerpo)
        if propia and not titulo_art:
            titulo_art, resto = propia.strip(" .,;").capitalize(), cuerpo
        art = Articulo(
            id=aid, norma_id=nid, numero=numero, etiqueta=etiqueta, titulo_articulo=titulo_art[:160],
            titulo=titulo, capitulo=capitulo, texto=resto if titulo_art else cuerpo, pagina=pagina_de(ini),
            notas=notas_todas,
        )
        norma.articulos.append(art)
    asignar_ids(norma)
    for art in norma.articulos:
        vigencia(art, norma.publicada)
    return norma


def asignar_ids(norma: Norma) -> None:
    def bloque_de(a: Articulo) -> tuple[str, int]:
        numero, b = a.id.rsplit("@", 1)
        return ("disp" if numero.startswith("D-") else "art"), int(b)

    tamanos: dict[tuple[str, int], int] = defaultdict(int)
    for a in norma.articulos:
        tamanos[bloque_de(a)] += 1
    principal = {}
    for clase in ("art", "disp"):
        bloques = [k for k in tamanos if k[0] == clase]
        if bloques:
            principal[clase] = max(bloques, key=lambda k: (tamanos[k], -k[1]))
    usados: set[str] = set()
    for a in norma.articulos:
        clave = bloque_de(a)
        numero = a.id.rsplit("@", 1)[0]
        prefijo = "" if principal.get(clave[0]) == clave else f"b{clave[1]}:"
        aid = f"{norma.id}:{prefijo}{numero}"
        while aid in usados:
            aid += "'"
        usados.add(aid)
        a.id = aid


def construir(origen: Path) -> list[Norma]:
    pags = paginas(origen)
    entradas = indice(pags)
    total = max(pags)
    normas: list[Norma] = []
    usados: set[str] = set()
    for i, entrada in enumerate(entradas):
        desde = entrada["pagina"]
        hasta = entradas[i + 1]["pagina"] if i + 1 < len(entradas) else total + 1
        if hasta < desde:
            continue
        rango = list(range(desde, max(hasta, desde + 1)))
        crudo, cortes = "", []
        for p in rango:
            cortes.append((len(crudo), p))
            crudo += CABECERA.sub("", pags.get(p, "")) + "\n"
        texto = limpio(crudo)
        escala = len(texto) / max(len(crudo), 1)

        def pagina_de(pos: int, cortes=cortes, escala=escala) -> int:
            real = pos / escala
            return max((p for c, p in cortes if c <= real), default=cortes[0][1])

        norma = parsear(entrada, texto, pagina_de)
        if norma.id in usados:
            continue
        usados.add(norma.id)
        if norma.articulos:
            normas.append(norma)
    return normas


def guardar(normas: list[Norma]) -> Path:
    destino = CORPUS_DIR / "normas.json"
    destino.write_text(json.dumps([asdict(n) for n in normas], ensure_ascii=False, indent=1), encoding="utf-8")
    return destino


if __name__ == "__main__":
    normas = construir(Path(sys.argv[1]))
    arts = [a for n in normas for a in n.articulos]
    print(f"{len(normas)} normas, {len(arts)} unidades, {sum(len(a.texto) for a in arts)} caracteres")
    for estado in ("vigente", "modificado", "derogado"):
        print(estado, sum(a.estado == estado for a in arts))
    print(guardar(normas))
