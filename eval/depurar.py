import json
import shutil

from common import DATA, escribir_jsonl, leer_jsonl
from metricas import particion

MOTIVOS = {
    "texto_roto": "derogada con texto de articulo truncado o sin sujeto reconocible",
    "metadato": "estado oro contradice el texto del articulo",
    "sin_sujeto": "premisa sobre un plazo o requisito sin nombrar el tramite",
    "falso_en_texto": "la cifra supuestamente falsa aparece en el texto del articulo",
    "incoherente": "premisa verdadera, absurda o pregunta incoherente",
    "varias_normas": "el articulo tiene varias normas modificatorias distintas",
    "parcial": "incorporacion o derogacion de un elemento parcial descrita como del articulo entero",
    "ref_fuera_oro": "la respuesta de referencia afirma contenido ausente en los articulos oro",
    "respondible": "el corpus contiene normas generales que responden la pregunta",
}

EXCLUIR = {
    "texto_roto": ["q0417", "q0418", "q0419", "q0420", "q0422"],
    "metadato": ["q0423"],
    "sin_sujeto": ["q0424", "q0430", "q0436", "q0442", "q0448", "q0449", "q0450", "q0451", "q0452", "q0453",
                   "q0455", "q0456", "q0457", "q0462", "q0472", "q0478", "q0490", "q0496", "q0497", "q0502"],
    "falso_en_texto": ["q0432", "q0454", "q0458"],
    "incoherente": ["q0460", "q0468", "q0476", "q0484", "q0495"],
    "varias_normas": ["q0247", "q0269", "q0273", "q0275", "q0293", "q0295", "q0296", "q0300", "q0312", "q0314",
                      "q0320"],
    "parcial": ["q0294", "q0297", "q0299", "q0304", "q0307"],
    "ref_fuera_oro": ["q0364", "q0392"],
    "respondible": ["q0509", "q0513", "q0525", "q0529", "q0531", "q0541", "q0544", "q0550", "q0559", "q0571",
                    "q0579", "q0587", "q0589", "q0591"],
}


def main():
    completo = DATA / "benchmark_completo.jsonl"
    if not completo.exists():
        shutil.copy(DATA / "benchmark.jsonl", completo)
    preguntas = leer_jsonl(completo)
    motivo = {qid: m for m, qids in EXCLUIR.items() for qid in qids}
    quedan = [q for q in preguntas if q["qid"] not in motivo]
    fuera = [{"qid": q["qid"], "tipo": q["tipo"], "particion": particion(q["qid"]), "motivo": motivo[q["qid"]],
              "detalle": MOTIVOS[motivo[q["qid"]]], "pregunta": q["pregunta"]}
             for q in preguntas if q["qid"] in motivo]
    escribir_jsonl(DATA / "benchmark.jsonl", quedan)
    escribir_jsonl(DATA / "excluidas.jsonl", fuera)
    test = [q["qid"] for q in quedan if particion(q["qid"]) == "test"]
    (DATA / "test.json").write_text(json.dumps(test), encoding="utf-8")
    print(f"total {len(preguntas)}, excluidas {len(fuera)}, quedan {len(quedan)}, test {len(test)}")


if __name__ == "__main__":
    main()
