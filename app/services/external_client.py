# app/services/external_client.py
import logging
from threading import Lock
from typing import Optional

import httpx
from opentelemetry.propagate import inject
from prometheus_client import Counter

from app.core.config import settings

logger = logging.getLogger("app.external_client")

EXT_SERVICE_FAILURES = Counter(
    "ext_service_failures_total", "Number of external service call failures"
)

_client_lock = Lock()
_http_client: Optional[httpx.Client] = None

EXTERNAL_PATH = "/external/data"


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

    return httpx.Client(
        base_url=settings.EXTERNAL_SERVICE_URL,
        timeout=timeout,
        limits=limits,
        http2=settings.EXT_CLIENT_HTTP2_ENABLED,
    )


def _get_http_client() -> httpx.Client:
    global _http_client
    if _http_client is None:
        with _client_lock:
            if _http_client is None:
                _http_client = _build_http_client()
    return _http_client


def call_external_service(correlation_id: Optional[str] = None) -> dict:
    client = _get_http_client()
    headers = {}
    if correlation_id:
        headers["X-Correlation-Id"] = correlation_id

    # propagate current trace context for HTTPX
    inject(headers)

    try:
        response = client.get(EXTERNAL_PATH, headers=headers)
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
