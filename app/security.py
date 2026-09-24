from __future__ import annotations

import asyncio
import ipaddress
import socket
from urllib.parse import urlparse

from fastapi import Header, HTTPException, status

from .config import get_settings


BLOCKED_HOSTNAMES = {"localhost", "localhost.localdomain"}


def _is_forbidden_ip(ip: str) -> bool:
    addr = ipaddress.ip_address(ip)
    return any(
        (
            addr.is_private,
            addr.is_loopback,
            addr.is_link_local,
            addr.is_multicast,
            addr.is_reserved,
            addr.is_unspecified,
        )
    )


async def ensure_public_url(url: str) -> None:
    settings = get_settings()
    if settings.allow_private_networks:
        return

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="Somente URLs HTTP/HTTPS são permitidas")

    host = (parsed.hostname or "").rstrip(".").lower()
    if not host:
        raise HTTPException(status_code=400, detail="URL sem hostname válido")

    if host in BLOCKED_HOSTNAMES or host.endswith(".local"):
        raise HTTPException(status_code=400, detail="Destino de rede privada não permitido")

    try:
        ipaddress.ip_address(host)
        ips = {host}
    except ValueError:
        loop = asyncio.get_running_loop()
        try:
            infos = await loop.run_in_executor(
                None,
                lambda: socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM),
            )
        except socket.gaierror as exc:
            raise HTTPException(status_code=400, detail=f"Não foi possível resolver o hostname: {host}") from exc
        ips = {item[4][0] for item in infos}

    if not ips or any(_is_forbidden_ip(ip) for ip in ips):
        raise HTTPException(status_code=400, detail="Destino de rede privada/reservada não permitido")


async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = get_settings().api_key
    if expected and x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key inválida ou ausente")
