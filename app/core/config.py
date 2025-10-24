from __future__ import annotations

import secrets
from functools import lru_cache
from typing import Optional

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Novarchism Backend"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: str

    sanity_project_id: str = "4bbukn54"
    sanity_dataset: str = "production"
    sanity_api_version: str = "2023-05-03"
    sanity_token: Optional[str] = None
    sanity_use_cdn: bool = True

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

    @property
    def sanity_dataset_url(self) -> str:
        host = "apicdn" if self.sanity_use_cdn else "api"
        base = f"https://{self.sanity_project_id}.{host}.sanity.io/{self.sanity_api_version}"
        return f"{base}/data/query/{self.sanity_dataset}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
