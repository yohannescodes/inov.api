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
    database_url: str = ""  # Optional database URL, default empty string
    sanity_project_id: str = "4bbukn54"
    sanity_dataset: str = "production"
    sanity_api_version: str = "2023-05-03"
    sanity_token: Optional[str] = None
    sanity_use_cdn: bool = True
    jwt_secret_key: str = secrets.token_urlsafe(32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
