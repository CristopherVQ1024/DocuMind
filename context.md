
# 📌 Documento de Especificación del Proyecto: DocuMind

## 1. Información General
* **Nombre de la Aplicación:** `DocuMind`
* **Título Académico:** *Plataforma Cloud de Gestión Documental Inteligente basada en Arquitectura RAG con Microservicios Contenerizados en GCP*
* **Curso:** Servicios Cloud (100000SI97) - UTP
* **Evaluación Objetivo:** Proyecto Final (**PROY - 40%** de la nota final, entrega Semana 18)

---

## 2. Objetivo del Proyecto
Diseñar, implementar y desplegar una arquitectura desacoplada en la nube que permita a los usuarios subir documentos en formato PDF y realizar consultas en lenguaje natural. El sistema utiliza el patrón **RAG (Retrieval-Augmented Generation)** para extraer fragmentos relevantes, almacenarlos en una base de datos vectorial y generar respuestas precisas mediante un LLM (Google Gemini API), garantizando respuestas contextualizadas y aislamiento mediante contenedores dentro de una instancia de **Compute Engine en Google Cloud**.

---

## 3. Arquitectura y Stack Tecnológico

| Capa / Módulo | Tecnología Seleccionada | Función en el Sistema |
| :--- | :--- | :--- |
| **Frontend** | **Angular** | Interfaz web SPA interactiva para carga de documentos, gestión y chat en tiempo real. |
| **Backend API** | **FastAPI (Python)** | API REST asíncrona que gestiona la ingesta de archivos, segmentación de texto (*chunking*) y orquestación RAG. |
| **Vector DB** | **Qdrant** | Base de datos vectorial para almacenar y ejecutar búsquedas por similitud semántica de los *embeddings*. |
| **Motor de IA** | **Google Gemini API** | Modelos `gemini-2.5-flash` (generación de respuestas) y `text-embedding-004` (vectorización). |
| **Infraestructura** | **Compute Engine (GCP)** | Instancia de Máquina Virtual Linux que aloja la solución. |
| **Orquestación** | **Docker & Docker Compose** | Despliegue desacoplado en contenedores aislados (red interna, volumen persistente). |
| **Enrutamiento** | **Nginx** | *Reverse Proxy* para direccionar el tráfico público hacia Angular y FastAPI sin interferir con otros proyectos de la VM. |

---

## 4. Alineación con el Sílabo del Curso

El proyecto abarca los conceptos centrales de las 3 unidades del sílabo:

1. **Unidad 1 - Introducción a Cloud (Semanas 1–3):**
   * **Virtualización y Máquinas Virtuales:** Operación sobre instancia de Compute Engine.
   * **Almacenamiento en la Nube:** Uso de almacenamiento no estructurado y bases de datos vectoriales.
2. **Unidad 2 - Gestión de los Servicios Cloud (Semanas 4–12):**
   * **Plataformas basadas en Contenedores (Semanas 4–5):** Aislamiento de microservicios (procesamiento, memoria, disco y red) con `docker-compose`.
   * **Infraestructura y Redes (Semanas 7–8):** Configuración de puertos y red interna inter-contenedor.
3. **Unidad 3 - Diseño de Soluciones Cloud (Semanas 13–18):**
   * **Arquitectura de aplicaciones en la nube:** Patrón RAG desacoplado, resiliencia y buenas prácticas de diseño de soluciones.
   * **Evaluación Final (Semana 18):** Sustentación del capstone **PROY (40%)**.

---

## 5. Briefing / Prompt de Contexto Técnico

```text
PROYECTO: DocuMind - Sistema RAG sobre Documentos en Google Cloud (VM + Docker)

CONTEXTO TÉCNICO:
Plataforma de gestión documental inteligente para el curso Servicios Cloud. Desplegada en una VM de Compute Engine (GCP) utilizando Docker Compose y Nginx como Reverse Proxy.

ARQUITECTURA DE CONTENEDORES:
1. Frontend: Angular (Interfaz web SPA para chat y carga de archivos PDF).
2. Backend: FastAPI en Python (Endpoints REST de ingesta PDF, chunking y flujo RAG).
3. Vector DB: Qdrant (Contenedor Docker para búsqueda semántica de embeddings).
4. Reverse Proxy: Nginx (Gestión de dominio/puertos y aislamiento con otras apps del servidor).

FLUJO DE TRABAJO RAG:
1. Ingesta: Carga de PDF -> Extracción de texto -> Chunking (división en bloques).
2. Vectorización: Generación de embeddings con Google text-embedding-004 -> Almacenamiento en Qdrant.
3. Búsqueda: Consulta del usuario -> Similarity Search en Qdrant -> Recuperación de contexto relevante.
4. Generación: Envío de contexto + pregunta a Gemini API -> Respuesta estructurada enviada a la app Angular.
```

