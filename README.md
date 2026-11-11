# DocuMind

Asistente RAG sobre protección de datos personales, delitos informáticos y seguridad digital en el Perú. Responde en lenguaje natural y cada respuesta cita la norma y el artículo.

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
Las normas están en `backend/corpus/normas.json`, ya divididas en título, capítulo y artículo. El backend las indexa solo al arrancar si la colección de Qdrant no existe, y guarda los vectores en `data/embeddings.jsonl` para no repetir llamadas. Para regenerar el JSON a partir de los textos extraídos: `python backend/scripts/build_corpus.py <carpeta con los txt>`. Las fuentes y sus enlaces oficiales están en `backend/corpus/fuentes.json`.
