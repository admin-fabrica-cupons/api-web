from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_key: str | None = None
    default_proxy_url: str | None = None
    request_timeout_ms: int = 30_000
    browser_timeout_ms: int = 35_000
    max_response_bytes: int = 5_000_000
    max_browser_concurrency: int = 2
    rate_limit_per_minute: int = 30
    allow_private_networks: bool = False
    log_level: str = "INFO"


@lru_cache

def get_settings() -> Settings:
    return Settings()
