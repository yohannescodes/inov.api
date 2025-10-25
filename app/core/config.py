from __future__ import annotations

import secrets
from functools import lru_cache
from typing import Optional, List

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Novarchism Backend"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: Optional[str] = None

    sanity_project_id: str = "4bbukn54"
    sanity_dataset: str = "production"
    sanity_api_version: str = "2023-05-03"
    sanity_token: Optional[str] = None
    sanity_use_cdn: bool = True

    jwt_secret_key: str = secrets.token_urlsafe(32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    cors_origins: List[AnyHttpUrl] | List[str] = []
    supabase_service_role_key: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def has_database(self) -> bool:
        """
        Returns True if a database URL is provided, otherwise False.
        """
        return bool(self.database_url and self.database_url.strip())

    @property
    def sanity_dataset_url(self) -> Optional[str]:
        """
        Construct the Sanity API endpoint for dataset queries or return None if config is incomplete.
        """
        if not self.sanity_project_id or not self.sanity_dataset:
            return None
        return f"https://{self.sanity_project_id}.api.sanity.io/{self.sanity_api_version}/data/query/{self.sanity_dataset}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
