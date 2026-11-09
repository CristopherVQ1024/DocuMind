# DocuMind

Plataforma de gestión documental con RAG. Sube PDF, pregúntales en lenguaje natural y cada respuesta cita el documento y la página.

- `frontend/` Angular 22 zoneless, SCSS, Tailwind v4 y Spartan UI. Login con Google por Firebase.
- `backend/` FastAPI. Ingesta de PDF, chunking, embeddings y chat con streaming.
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
