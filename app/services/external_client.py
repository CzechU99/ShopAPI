# app/services/external_client.py
import asyncio
import logging
from pathlib import Path
from typing import Optional

import httpx
from opentelemetry.propagate import inject
from prometheus_client import Counter

from app.core.config import settings

logger = logging.getLogger("app.external_client")

EXT_SERVICE_FAILURES = Counter(
    "ext_service_failures_total", "Number of external service call failures"
)

_client_lock: Optional[asyncio.Lock] = None
_http_client: Optional[httpx.AsyncClient] = None

EXTERNAL_PATH = "/external/data"


def _resolve_base_url() -> str:
    if settings.EXT_CLIENT_HTTP2_ENABLED:
        return settings.EXTERNAL_SERVICE_HTTP2_URL
    return settings.EXTERNAL_SERVICE_URL


def _resolve_verify_param(base_url: str):
    if not base_url.startswith("https://"):
        return True

    ca_path = settings.EXT_CLIENT_CA_CERT
    if ca_path:
        path = Path(ca_path)
        if path.exists():
            return str(path)
        logger.warning("EXT_CLIENT_CA_CERT=%s does not exist", ca_path)
    return False


def _build_http_client() -> httpx.AsyncClient:
    limits = httpx.Limits(
        max_connections=settings.EXT_CLIENT_MAX_CONNECTIONS,
        max_keepalive_connections=settings.EXT_CLIENT_MAX_KEEPALIVE_CONNECTIONS,
        keepalive_expiry=settings.EXT_CLIENT_KEEPALIVE_EXPIRY,
    )

    timeout = httpx.Timeout(
        connect=settings.EXT_CLIENT_CONNECT_TIMEOUT,
        read=settings.EXT_CLIENT_READ_TIMEOUT,
        write=settings.EXT_CLIENT_WRITE_TIMEOUT,
        pool=settings.EXT_CLIENT_POOL_TIMEOUT,
    )

    base_url = _resolve_base_url()
    verify = _resolve_verify_param(base_url)

    return httpx.AsyncClient(
        base_url=base_url,
        timeout=timeout,
        limits=limits,
        verify=verify,
        http2=settings.EXT_CLIENT_HTTP2_ENABLED,
    )


async def _get_http_client() -> httpx.AsyncClient:
    global _http_client, _client_lock
    if _http_client is not None:
        return _http_client

    if _client_lock is None:
        _client_lock = asyncio.Lock()

    async with _client_lock:
        if _http_client is None:
            _http_client = _build_http_client()
    return _http_client


async def call_external_service(correlation_id: Optional[str] = None) -> dict:
    client = await _get_http_client()
    headers = {}
    if correlation_id:
        headers["X-Correlation-Id"] = correlation_id

    # propagate current trace context for HTTPX
    inject(headers)

    try:
        response = await client.get(EXTERNAL_PATH, headers=headers)
        response.raise_for_status()
        logger.info(
            "external_client: call success",
            extra={
                "http_status": response.status_code,
                "correlation_id": correlation_id,
            },
        )
        return response.json()
    except Exception as exc:
        EXT_SERVICE_FAILURES.inc()
        logger.error(
            "external_client: call failed",
            extra={
                "correlation_id": correlation_id,
                "error_type": exc.__class__.__name__,
            },
        )
        raise
