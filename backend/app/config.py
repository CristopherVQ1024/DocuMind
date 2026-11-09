from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_embed_model: str = "gemini-embedding-001"
    embed_dim: int = 768

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "documind"

    firebase_project_id: str = ""
    dev_auth_bypass: bool = False

    data_dir: str = "./data"
    max_upload_mb: int = 20
    max_pages: int = 300
    chunk_chars: int = 1200
    chunk_overlap: int = 200
    top_k: int = 6
    cors_origins: str = "http://localhost:4200"


@lru_cache
def get_settings() -> Settings:
    return Settings()
