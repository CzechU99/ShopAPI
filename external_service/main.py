import asyncio
import logging
import os
import random
import time
import uuid

import httpx
from fastapi import FastAPI, Request
from opentelemetry import trace
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.base import BaseHTTPMiddleware

from middlewares.request_logging import RequestLoggingMiddleware
from telemetry.logging_config import setup_json_logging
from telemetry.tracing import setup_tracing


REMOTE_SOURCE = os.getenv(
    "EXTERNAL_REMOTE_SOURCE", "https://jsonplaceholder.typicode.com/posts/{id}"
)
REMOTE_TIMEOUT = float(os.getenv("EXTERNAL_REMOTE_TIMEOUT", "30"))
MIN_DELAY_SECONDS = int(os.getenv("EXTERNAL_DELAY_MIN_SECONDS", "30"))
MAX_DELAY_SECONDS = int(os.getenv("EXTERNAL_DELAY_MAX_SECONDS", "120"))
if MIN_DELAY_SECONDS > MAX_DELAY_SECONDS:
    MIN_DELAY_SECONDS, MAX_DELAY_SECONDS = MAX_DELAY_SECONDS, MIN_DELAY_SECONDS
if MIN_DELAY_SECONDS < 0:
    MIN_DELAY_SECONDS = 0
if MAX_DELAY_SECONDS < 0:
    MAX_DELAY_SECONDS = 0

logger = logging.getLogger("external.handler")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-Id", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-Id"] = correlation_id
        return response


app = FastAPI(title="External Service")

# Init OpenTelemetry tracing & logging
setup_tracing(app)
setup_json_logging("external_service")

# Correlation ID propagation
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Expose Prometheus metrics at /metrics
Instrumentator().instrument(app).expose(app, include_in_schema=False)


@app.get("/external/data")
async def get_external_data(request: Request):
    extra_delay = 0
    if MAX_DELAY_SECONDS > 0:
        extra_delay = random.randint(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
        if extra_delay > 0:
            await asyncio.sleep(extra_delay)

    target_id = random.randint(1, 100)
    target_url = REMOTE_SOURCE.format(id=target_id)
    start = time.perf_counter()
    async with httpx.AsyncClient(timeout=REMOTE_TIMEOUT) as client:
        response = await client.get(target_url)
        response.raise_for_status()
        payload = response.json()
    duration = int((time.perf_counter() - start) * 1000)

    span = trace.get_current_span()
    ctx = span.get_span_context() if span else None
    trace_id = format(ctx.trace_id, "032x") if ctx and ctx.trace_id else None
    span_id = format(ctx.span_id, "016x") if ctx and ctx.span_id else None
    correlation_id = getattr(request.state, "correlation_id", None)

    logger.info(
        "external fetch completed",
        extra={
            "trace_id": trace_id,
            "span_id": span_id,
            "correlation_id": correlation_id,
            "http_route": "/external/data",
            "remote_delay_ms": duration,
            "remote_url": target_url,
            "sleep_seconds": extra_delay,
        },
    )

    return {
        "status": "ok",
        "correlation_id": correlation_id,
        "remote_delay_ms": duration,
        "remote_url": target_url,
         "sleep_seconds": extra_delay,
        "data": payload,
    }
