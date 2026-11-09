def friendly_error(exc: Exception) -> str:
    if isinstance(exc, ValueError):
        return str(exc)
    if "API key" in str(exc):
        return "Falta una clave de Gemini válida. Revisa GEMINI_API_KEY en el .env."
    code = getattr(exc, "code", None)
    if code == 402:
        return "Se agotaron los créditos prepago de Gemini. Recarga saldo o usa una clave de un proyecto sin facturación."
    if code == 429:
        return "Se alcanzó el límite de peticiones de Gemini. Espera un minuto e intenta de nuevo."
    if code in (400, 401, 403):
        return "Gemini rechazó la petición. Revisa la clave y los nombres de modelo en el .env."
    if code == 404:
        return "El modelo de Gemini configurado no está disponible. Revisa GEMINI_MODEL y GEMINI_EMBED_MODEL."
    return "No se pudo completar la operación. Intenta de nuevo."
