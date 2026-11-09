# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack
Angular 22 zoneless con SCSS, Spartan UI y Tailwind v4. Backend FastAPI, Qdrant y Nginx en Docker Compose sobre una VM de Compute Engine. Decidido por el usuario.

## Users
Estudiante que sube sus propios PDF y les hace preguntas en lenguaje natural. El uso real es una demo académica: el proyecto final del curso Servicios Cloud (UTP), evaluado por un docente en la sustentación.

## Product Purpose
Gestión documental con RAG: el usuario sube PDF, el sistema los fragmenta, los vectoriza y responde con un modelo de Google Gemini citando documento y página. Éxito: una respuesta correcta con su fuente visible, y una arquitectura de contenedores demostrable.

## Positioning
Cada respuesta muestra de qué documento y página salió, así que se puede verificar. No es un chat genérico.

## Operating Context
Login con Google (Firebase). Los documentos de cada usuario están aislados. La indexación corre en segundo plano y la interfaz consulta el estado. Convive en una VM de 4 GB con MoviFi, detrás del mismo Caddy.

## Capabilities and Constraints
- Subir, listar y borrar PDF con estado de indexado.
- Chat con respuesta en streaming y citas, filtrable por documento.
- Modelos de Gemini por variable de entorno, pendientes de elegir según disponibilidad.
- Plan gratis de Gemini: límites bajos de peticiones por minuto.

## Product Principles
- La fuente siempre visible junto a la respuesta.
- Estados claros: subiendo, indexando, listo, error.
- Pocas pantallas y ninguna decoración sin función.

## Accessibility & Inclusion
Contraste AA, foco visible, uso con teclado. Interfaz en español.
