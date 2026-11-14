import argparse
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

from common import DATA, RUNS, agregar_jsonl, articulos, cita, extraer_json, leer_jsonl, redactar
from metricas import particion

SISTEMA = """Eres evaluador experto en derecho laboral peruano. Recibes varias respuestas generadas por sistemas de pregunta-respuesta.
Para cada una calificas dos cosas:
- "correccion": 2 si la respuesta coincide en lo sustancial con la respuesta de referencia, 1 si es parcialmente correcta o incompleta, 0 si es incorrecta, contradice la referencia o se abstiene cuando debía responder. Si la referencia indica que no se debe responder y el sistema se abstiene, vale 2.
- "fidelidad": proporción entre 0 y 1 de las afirmaciones de la respuesta que están respaldadas por los pasajes recuperados. Una abstención vale 1.
Devuelve solo un objeto JSON con la clave \"juicios\": una lista de objetos {"id": ..., "correccion": ..., "fidelidad": ..., "motivo": "una frase"} en el mismo orden."""


def bloque(i: str, q: dict, salida: dict, contexto: list[str]) -> str:
    pasajes = "\n".join(f"- {cita(articulos()[a])}: {articulos()[a].texto[:900]}" for a in contexto if a in articulos())
    fecha = f"\nFecha de referencia: {q['fecha_ref']}" if q.get("fecha_ref") else ""
    return (f"### id {i}\nPregunta: {q['pregunta']}{fecha}\nRespuesta de referencia: {q['respuesta_ref']}\n"
            f"Pasajes recuperados:\n{pasajes or '- ninguno'}\nRespuesta del sistema: {salida['respuesta']}")


def muestra(preguntas: dict, por_tipo: int, semilla: int = 11) -> set[str]:
    rnd = random.Random(semilla)
    grupos = defaultdict(list)
    for qid, q in sorted(preguntas.items()):
        grupos[q["tipo"]].append(qid)
    return {qid for g in grupos.values() for qid in rnd.sample(g, min(por_tipo, len(g)))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corridas", nargs="+")
    ap.add_argument("--por-tipo", type=int, default=20)
    ap.add_argument("--lote", type=int, default=6)
    ap.add_argument("--hilos", type=int, default=3)
    args = ap.parse_args()
    preguntas = {q["qid"]: q for q in leer_jsonl(DATA / "benchmark.jsonl")}
    elegidas = muestra({k: v for k, v in preguntas.items() if particion(k) == "test"}, args.por_tipo)
    salida_ruta = RUNS / "juez" / "juicios.jsonl"
    salida_ruta.parent.mkdir(parents=True, exist_ok=True)
    hechos = {(f["corrida"], f["qid"]) for f in leer_jsonl(salida_ruta)}
    candado = threading.Lock()
    for corrida in args.corridas:
        filas = [f for f in leer_jsonl(RUNS / "generacion" / f"{corrida}.jsonl")
                 if f["qid"] in elegidas and (corrida, f["qid"]) not in hechos]
        print(f"{corrida}: {len(filas)} por juzgar", flush=True)
        lotes = [filas[k : k + args.lote] for k in range(0, len(filas), args.lote)]

        def juzgar(lote, corrida=corrida):
            texto = "\n\n".join(bloque(f["qid"], preguntas[f["qid"]], f, f["contexto_aid"]) for f in lote)
            crudo, juez = redactar(texto, SISTEMA, temperatura=0.0)
            datos = extraer_json(crudo)
            if isinstance(datos, dict):
                datos = next((v for v in datos.values() if isinstance(v, list)), [datos])
            notas = {str(d.get("id")): d for d in datos if isinstance(d, dict)} if isinstance(datos, list) else {}
            for f in lote:
                d = notas.get(f["qid"])
                if not d:
                    continue
                try:
                    correccion = max(0, min(2, int(d.get("correccion", 0))))
                    fidelidad = max(0.0, min(1.0, float(d.get("fidelidad", 0))))
                except (TypeError, ValueError):
                    continue
                with candado:
                    agregar_jsonl(salida_ruta, {"corrida": corrida, "qid": f["qid"], "correccion": correccion,
                                                "fidelidad": fidelidad, "motivo": str(d.get("motivo", "")), "juez": juez})

        with ThreadPoolExecutor(args.hilos) as ex:
            list(ex.map(juzgar, lotes))

if __name__ == "__main__":
    main()
