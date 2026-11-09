from fastapi import Header, HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from .config import get_settings

_request = google_requests.Request()


def current_user(authorization: str = Header(default="")) -> str:
    settings = get_settings()
    if settings.dev_auth_bypass:
        return "dev-user"
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Falta el token de sesión")
    token = authorization.removeprefix("Bearer ")
    try:
        claims = id_token.verify_firebase_token(
            token, _request, audience=settings.firebase_project_id
        )
    except Exception:
        claims = None
    if not claims:
        raise HTTPException(401, "Sesión inválida o vencida")
    return claims["sub"]
