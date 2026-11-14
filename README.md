# DocuMind

Asistente RAG sobre derecho laboral peruano del régimen privado. Responde en lenguaje natural, cita la norma y el artículo, y avisa cuando un artículo no regía en la fecha de la pregunta (derogado, todavía no existía o con otra redacción).

- `frontend/` Angular 22 zoneless, SCSS, Tailwind v4 y Spartan UI. Login con Google por Firebase.
- `backend/` FastAPI. Corpus normativo en `backend/corpus`, indexado jerárquico por artículo, embeddings y chat con streaming.
- Qdrant guarda los vectores. Gemini genera embeddings y respuestas.
- `docker-compose.yml` levanta qdrant, backend y web (Nginx). El despliegue en la VM está en `deploy/README.md`.

## Desarrollo local

```bash
cp .env.example .env            # completar claves
docker run -d -p 6333:6333 qdrant/qdrant
cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt
QDRANT_URL=http://localhost:6333 uvicorn app.main:app --reload
cd frontend && npm install && npm start
```

Sin Firebase configurado: `DEV_AUTH_BYPASS=true` en `.env` y `devAuth: true` en `frontend/src/environments/environment.development.ts`.

Pruebas del backend: `cd backend && pytest`.

## Corpus
Las normas están en `backend/corpus/normas.json`: 135 normas y 3 476 artículos del compendio de normas laborales del régimen privado del MTPE (actualizado al 21/10/2024), divididos en título, capítulo y artículo. Cada artículo trae sus notas de modificación, incorporación y derogación con norma y fecha, y de ahí salen `existe_desde`, `version_desde` y `derogado_desde`. El backend las indexa solo al arrancar si la colección de Qdrant no existe, y guarda los vectores en `data/embeddings.jsonl` para no repetir llamadas. Para regenerar el JSON desde el texto por página del compendio: `python backend/scripts/build_corpus.py <paginas.json>`.

## Evaluación
`eval/` tiene el benchmark temporal y los experimentos del artículo: generación de preguntas (`bench_build.py`), sistemas y líneas base (`sistemas.py`), corridas de recuperación y generación, juez, calibración del umbral de abstención, validación humana y reporte con estadística por pregunta (`reporte.py`). Usa su propio entorno con PyTorch y CUDA (`eval/requirements.txt`).
