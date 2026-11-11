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
    chunk_chars: int = 800
    chunk_overlap: int = 150
    top_k: int = 12
    max_articles: int = 6
    article_chars: int = 3000
    cors_origins: str = "http://localhost:4200"


@lru_cache
def get_settings() -> Settings:
    return Settings()
