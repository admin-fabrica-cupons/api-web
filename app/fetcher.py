from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import httpx
from fastapi import HTTPException
from playwright.async_api import Browser, BrowserContext, Playwright, Route, async_playwright

from .config import get_settings
from .models import ProxyConfig, ScrapeRequest
from .security import ensure_public_url


DESKTOP_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
]

DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.7,en;q=0.6",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
}

BLOCK_HINTS = (
    "access denied",
    "request blocked",
    "temporarily blocked",
    "captcha",
    "verify you are human",
    "cf-chl-",
    "cloudflare ray id",
)

JS_HINTS = (
    "enable javascript",
    "please enable javascript",
    "__next_data__",
    "id=\"__next\"",
    'id="root"></div>',
)


@dataclass
class RawFetch:
    html: str
    final_url: str
    status_code: int
    content_type: str | None
    elapsed_ms: int
    warnings: list[str]


class BrowserManager:
    def __init__(self) -> None:
        self._pw: Playwright | None = None
        self._browser: Browser | None = None
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(get_settings().max_browser_concurrency)

    async def start(self) -> None:
        async with self._lock:
            if self._browser is not None:
                return
            self._pw = await async_playwright().start()
            self._browser = await self._pw.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--no-sandbox"])

    async def stop(self) -> None:
        async with self._lock:
            if self._browser:
                await self._browser.close()
                self._browser = None
            if self._pw:
                await self._pw.stop()
                self._pw = None

    async def context(self, req: ScrapeRequest) -> tuple[BrowserContext, Browser | None]:
        await self.start()
        assert self._browser is not None

        proxy = _playwright_proxy(req.proxy)
        if proxy:
            # Para proxy por requisição, abrimos um Chromium temporário com o proxy selecionado.
            assert self._pw is not None
            browser = await self._pw.chromium.launch(
                headless=True,
                proxy=proxy,
                args=["--disable-dev-shm-usage", "--no-sandbox"],
            )
            context = await browser.new_context(
                locale=req.locale,
                timezone_id=req.timezone_id,
                user_agent=req.user_agent or random.choice(DESKTOP_UAS),
                viewport={"width": 1366, "height": 768},
                extra_http_headers={**DEFAULT_HEADERS, **req.headers},
                service_workers="block",
            )
            return context, browser

        context = await self._browser.new_context(
            locale=req.locale,
            timezone_id=req.timezone_id,
            user_agent=req.user_agent or random.choice(DESKTOP_UAS),
            viewport={"width": 1366, "height": 768},
            extra_http_headers={**DEFAULT_HEADERS, **req.headers},
            service_workers="block",
        )
        return context, None

    @property
    def semaphore(self) -> asyncio.Semaphore:
        return self._semaphore


browser_manager = BrowserManager()


def _proxy_url(proxy: ProxyConfig | None) -> str | None:
    settings = get_settings()
    if proxy is None:
        return settings.default_proxy_url
    parsed = urlparse(proxy.server)
    if proxy.username and proxy.password and "@" not in proxy.server:
        port = f":{parsed.port}" if parsed.port else ""
        return f"{parsed.scheme}://{proxy.username}:{proxy.password}@{parsed.hostname}{port}"
    return proxy.server


def _playwright_proxy(proxy: ProxyConfig | None) -> dict | None:
    settings = get_settings()
    if proxy is None and not settings.default_proxy_url:
        return None
    if proxy is None:
        return {"server": settings.default_proxy_url}
    data = {"server": proxy.server}
    if proxy.username:
        data["username"] = proxy.username
    if proxy.password:
        data["password"] = proxy.password
    if proxy.bypass:
        data["bypass"] = proxy.bypass
    return data


def looks_blocked(status_code: int, html: str) -> bool:
    text = html[:250_000].lower()
    return status_code in {401, 403, 407, 429, 503} or any(hint in text for hint in BLOCK_HINTS)


def likely_needs_browser(html: str) -> bool:
    stripped = html.strip()
    lower = stripped.lower()
    if len(stripped) < 2_500:
        return True
    return any(hint in lower for hint in JS_HINTS)


async def _read_limited(response: httpx.Response, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    size = 0
    async for chunk in response.aiter_bytes():
        size += len(chunk)
        if size > max_bytes:
            raise HTTPException(status_code=413, detail=f"Resposta excedeu o limite de {max_bytes} bytes")
        chunks.append(chunk)
    return b"".join(chunks)


async def fetch_http(req: ScrapeRequest) -> RawFetch:
    settings = get_settings()
    timeout_ms = req.timeout_ms or settings.request_timeout_ms
    url = str(req.url)
    headers = {**DEFAULT_HEADERS, "User-Agent": req.user_agent or random.choice(DESKTOP_UAS), **req.headers}
    cookies = {cookie.name: cookie.value for cookie in req.cookies}
    proxy_url = _proxy_url(req.proxy)
    warnings: list[str] = []

    start = time.perf_counter()
    last_error: Exception | None = None

    for attempt in range(req.max_retries + 1):
        current_url = url
        try:
            async with httpx.AsyncClient(
                proxy=proxy_url,
                timeout=httpx.Timeout(timeout_ms / 1000),
                http2=True,
                follow_redirects=False,
                verify=True,
                trust_env=False,
                headers=headers,
                cookies=cookies,
            ) as client:
                for _ in range(6):
                    await ensure_public_url(current_url)
                    async with client.stream("GET", current_url) as response:
                        if response.status_code in {301, 302, 303, 307, 308}:
                            location = response.headers.get("location")
                            if not location:
                                break
                            current_url = urljoin(current_url, location)
                            continue

                        raw = await _read_limited(response, settings.max_response_bytes)
                        encoding = response.encoding or "utf-8"
                        html = raw.decode(encoding, errors="replace")
                        elapsed_ms = int((time.perf_counter() - start) * 1000)
                        return RawFetch(
                            html=html,
                            final_url=str(response.url),
                            status_code=response.status_code,
                            content_type=response.headers.get("content-type"),
                            elapsed_ms=elapsed_ms,
                            warnings=warnings,
                        )

                raise HTTPException(status_code=502, detail="Muitos redirects")
        except HTTPException:
            raise
        except Exception as exc:
            last_error = exc
            if attempt < req.max_retries:
                delay = min(0.6 * (2**attempt) + random.uniform(0.0, 0.35), 3.0)
                await asyncio.sleep(delay)
                warnings.append(f"Tentativa HTTP {attempt + 1} falhou; retry aplicado")

    raise HTTPException(status_code=502, detail=f"Falha no fetch HTTP: {type(last_error).__name__}")


async def _safe_route(route: Route, block_resources: bool) -> None:
    req_url = route.request.url
    resource_type = route.request.resource_type
    parsed = urlparse(req_url)

    if parsed.scheme in {"data", "blob", "about"}:
        await route.continue_()
        return

    if parsed.scheme not in {"http", "https"}:
        await route.abort("blockedbyclient")
        return

    try:
        await ensure_public_url(req_url)
    except HTTPException:
        await route.abort("blockedbyclient")
        return

    if block_resources and resource_type in {"image", "media", "font"}:
        await route.abort("blockedbyclient")
        return

    await route.continue_()


async def fetch_browser(req: ScrapeRequest) -> RawFetch:
    settings = get_settings()
    timeout_ms = req.timeout_ms or settings.browser_timeout_ms
    warnings: list[str] = []
    start = time.perf_counter()

    async with browser_manager.semaphore:
        context, owned_browser = await browser_manager.context(req)
        try:
            if req.cookies:
                target = urlparse(str(req.url))
                cookie_payload = []
                for cookie in req.cookies:
                    item = {"name": cookie.name, "value": cookie.value, "path": cookie.path}
                    if cookie.domain:
                        item["domain"] = cookie.domain
                    else:
                        item["url"] = f"{target.scheme}://{target.netloc}"
                    cookie_payload.append(item)
                await context.add_cookies(cookie_payload)

            async def route_handler(route: Route):
                await _safe_route(route, req.block_resources)

            await context.route("**/*", route_handler)
            page = await context.new_page()
            page.set_default_timeout(timeout_ms)
            page.set_default_navigation_timeout(timeout_ms)

            response = await page.goto(str(req.url), wait_until=req.wait_until.value, timeout=timeout_ms)
            if req.wait_for_selector:
                await page.wait_for_selector(req.wait_for_selector, timeout=timeout_ms)
            if req.delay_ms:
                await page.wait_for_timeout(req.delay_ms)

            html = await page.content()
            if len(html.encode("utf-8")) > settings.max_response_bytes:
                raise HTTPException(status_code=413, detail="HTML renderizado excedeu o limite configurado")

            status_code = response.status if response else 0
            content_type = None
            if response:
                headers = await response.all_headers()
                content_type = headers.get("content-type")

            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return RawFetch(
                html=html,
                final_url=page.url,
                status_code=status_code,
                content_type=content_type,
                elapsed_ms=elapsed_ms,
                warnings=warnings,
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Falha no navegador: {type(exc).__name__}: {exc}") from exc
        finally:
            await context.close()
            if owned_browser:
                await owned_browser.close()


async def fetch(req: ScrapeRequest) -> tuple[RawFetch, str]:
    # Explicit render_js takes precedence over mode.
    if req.render_js is True or req.mode.value == "browser":
        result = await fetch_browser(req)
        return result, "browser"

    if req.render_js is False or req.mode.value == "http":
        result = await fetch_http(req)
        return result, "http"

    http_result = await fetch_http(req)
    if looks_blocked(http_result.status_code, http_result.html):
        http_result.warnings.append("Resposta HTTP parece bloqueada/desafiada; tentando navegador")
        browser_result = await fetch_browser(req)
        browser_result.warnings = http_result.warnings + browser_result.warnings
        return browser_result, "browser"

    if likely_needs_browser(http_result.html):
        http_result.warnings.append("Página parece depender de JavaScript; tentando navegador")
        browser_result = await fetch_browser(req)
        browser_result.warnings = http_result.warnings + browser_result.warnings
        return browser_result, "browser"

    return http_result, "http"
