import json
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    DATABASE_URL: str

    GEMINI_API_KEY: str | None = None
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"
    GEMINI_EMBEDDING_DIMENSIONS: int = 768

    ALLOWED_ORIGINS: str = "http://localhost:5173"

    @property
    def allowed_origins_list(self) -> list[str]:
        raw = self.ALLOWED_ORIGINS.strip()
        if raw.startswith("[") and raw.endswith("]"):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except Exception:
                pass
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    @property
    def sqlalchemy_database_url(self) -> str:
        url = self.DATABASE_URL.strip()
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg://", 1)
        return url


settings = Settings()

if settings.GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY
