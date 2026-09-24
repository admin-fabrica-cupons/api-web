from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class ScrapeMode(str, Enum):
    auto = "auto"
    http = "http"
    browser = "browser"


class WaitUntil(str, Enum):
    domcontentloaded = "domcontentloaded"
    load = "load"
    networkidle = "networkidle"
    commit = "commit"


class ProxyConfig(BaseModel):
    server: str = Field(..., examples=["http://user:pass@proxy.example.com:8080"])
    username: str | None = None
    password: str | None = None
    bypass: str | None = None

    @field_validator("server")
    @classmethod
    def validate_proxy_scheme(cls, value: str) -> str:
        allowed = ("http://", "https://", "socks5://", "socks5h://")
        if not value.lower().startswith(allowed):
            raise ValueError("Proxy deve usar http://, https://, socks5:// ou socks5h://")
        return value


class CookieInput(BaseModel):
    name: str
    value: str
    domain: str | None = None
    path: str = "/"


class ScrapeRequest(BaseModel):
    url: HttpUrl
    mode: ScrapeMode = ScrapeMode.auto
    render_js: bool | None = None
    extract: bool = True
    include_html: bool = True
    wait_until: WaitUntil = WaitUntil.domcontentloaded
    wait_for_selector: str | None = None
    delay_ms: int = Field(default=0, ge=0, le=10_000)
    timeout_ms: int | None = Field(default=None, ge=1_000, le=90_000)
    max_retries: int = Field(default=2, ge=0, le=4)
    block_resources: bool = True
    locale: str = "pt-BR"
    timezone_id: str = "America/Sao_Paulo"
    user_agent: str | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    cookies: list[CookieInput] = Field(default_factory=list)
    proxy: ProxyConfig | None = None


class FetchResult(BaseModel):
    requested_url: str
    final_url: str
    status_code: int
    mode_used: Literal["http", "browser"]
    content_type: str | None = None
    elapsed_ms: int
    html: str | None = None
    data: dict[str, Any] | None = None
    warnings: list[str] = Field(default_factory=list)
