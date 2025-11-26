from __future__ import annotations

import threading
from typing import Optional

import httpx

from app.services.external_client import EXTERNAL_PATH, resolve_base_url, resolve_verify_param
from app.services.external_models import ExternalServiceResponse
from app.core.config import settings

_client_lock = threading.Lock()
_http_client: httpx.Client | None = None


def _build_http_client() -> httpx.Client:
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

    base_url = resolve_base_url()
    verify = resolve_verify_param(base_url)

    return httpx.Client(
        base_url=base_url,
        timeout=timeout,
        limits=limits,
        verify=verify,
        http2=settings.EXT_CLIENT_HTTP2_ENABLED,
    )


def _get_http_client() -> httpx.Client:
    global _http_client
    if _http_client is not None:
        return _http_client

    with _client_lock:
        if _http_client is None:
            _http_client = _build_http_client()
    return _http_client


def call_external_service_sync(
    correlation_id: Optional[str] = None,
) -> ExternalServiceResponse:
    client = _get_http_client()
    headers = {}
    if correlation_id:
        headers["X-Correlation-Id"] = correlation_id

    response = client.get(EXTERNAL_PATH, headers=headers)
    response.raise_for_status()
    elapsed = response.elapsed.total_seconds() if response.elapsed else 0.0
    elapsed_ms = int(elapsed * 1000)
    return ExternalServiceResponse(
        status_code=response.status_code,
        body=response.json(),
        elapsed_ms=elapsed_ms,
    )
