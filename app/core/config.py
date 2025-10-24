from __future__ import annotations

import secrets
from functools import lru_cache
from typing import Optional

from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    app_name: str = "Novarchism Backend"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: str

    jwt_secret_key: str = secrets.token_urlsafe(32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    cors_origins: list[AnyHttpUrl] | list[str] = []

    supabase_service_role_key: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
