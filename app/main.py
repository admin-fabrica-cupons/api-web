from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse

from .config import get_settings
from .extractor import extract_page_data
from .fetcher import browser_manager, fetch
from .models import FetchResult, ScrapeRequest
from .security import require_api_key


settings = get_settings()
_rate_buckets: dict[str, deque[float]] = defaultdict(deque)
_rate_lock = asyncio.Lock()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await browser_manager.stop()


app = FastAPI(
    title="Product Scraper API",
    version="1.0.0",
    description="Fetch HTML with optional JavaScript rendering and generic product metadata extraction.",
    lifespan=lifespan,
)


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if request.url.path in {"/health", "/docs", "/openapi.json", "/redoc"}:
        return await call_next(request)

    key = request.headers.get("x-api-key") or (request.client.host if request.client else "unknown")
    now = time.monotonic()
    cutoff = now - 60
    async with _rate_lock:
        bucket = _rate_buckets[key]
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= settings.rate_limit_per_minute:
            return JSONResponse(status_code=429, content={"detail": "Rate limit excedido"})
        bucket.append(now)

    return await call_next(request)


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/v1/scrape", response_model=FetchResult, dependencies=[Depends(require_api_key)])
async def scrape(payload: ScrapeRequest) -> FetchResult:
    raw, mode_used = await fetch(payload)
    data = extract_page_data(raw.html, raw.final_url) if payload.extract else None
    return FetchResult(
        requested_url=str(payload.url),
        final_url=raw.final_url,
        status_code=raw.status_code,
        mode_used=mode_used,
        content_type=raw.content_type,
        elapsed_ms=raw.elapsed_ms,
        html=raw.html if payload.include_html else None,
        data=data,
        warnings=raw.warnings,
    )


@app.get("/v1/html", response_class=HTMLResponse, dependencies=[Depends(require_api_key)])
async def get_html(
    url: str = Query(..., description="URL HTTP/HTTPS a buscar"),
    render_js: bool = Query(default=False),
    timeout_ms: int | None = Query(default=None, ge=1000, le=90000),
):
    try:
        payload = ScrapeRequest(url=url, render_js=render_js, extract=False, include_html=True, timeout_ms=timeout_ms)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    raw, _ = await fetch(payload)
    return HTMLResponse(content=raw.html, status_code=200, headers={"X-Upstream-Status": str(raw.status_code)})
