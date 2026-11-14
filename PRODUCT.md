# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack
Angular 22 zoneless con SCSS, Spartan UI y Tailwind v4. Backend FastAPI, Qdrant y Nginx en Docker Compose sobre una VM de Compute Engine. Decidido por el usuario.

## Users
Persona sin formación legal, estudiante o profesional de sistemas, trabajador o empleador que quiere saber qué dice la normativa laboral peruana del régimen privado y si un artículo regía en cierta fecha. El uso real es una demo académica: el proyecto final del curso Servicios Cloud (UTP), evaluado por un docente en la sustentación.

## Product Purpose
RAG sobre un corpus fijo de normas laborales peruanas con metadatos de vigencia. El texto se divide por título, capítulo y artículo, se vectoriza y un modelo de Google Gemini responde citando norma y artículo. Éxito: una respuesta correcta con su fuente visible, y una arquitectura de contenedores demostrable.

## Positioning
Cada respuesta muestra de qué norma y artículo salió, con enlace a la fuente oficial, así que se puede verificar. No es un chat genérico.

## Operating Context
Login con Google (Firebase). El corpus es el mismo para todos y la conversación es de cada usuario. La indexación corre en segundo plano al arrancar y la interfaz consulta el estado. Convive en una VM de 4 GB con MoviFi, detrás del mismo Caddy.

## Capabilities and Constraints
- Corpus fijo de 135 normas laborales, sin subida de archivos.
- Cada fuente indica si el artículo regía en la fecha de la pregunta.
- Chat con respuesta en streaming y citas por artículo.
- Modelos de Gemini por variable de entorno, pendientes de elegir según disponibilidad.
- Plan gratis de Gemini: límites bajos de peticiones por minuto.

## Product Principles
- La fuente siempre visible junto a la respuesta.
- Estados claros: indexando, listo, error.
- Pocas pantallas y ninguna decoración sin función.

## Accessibility & Inclusion
Contraste AA, foco visible, uso con teclado. Interfaz en español.
