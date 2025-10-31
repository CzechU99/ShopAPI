import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from opentelemetry import trace


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration = time.perf_counter() - start
            span = trace.get_current_span()
            ctx = span.get_span_context() if span else None
            trace_id = None
            span_id = None
            if ctx and ctx.is_valid:
                trace_id = format(ctx.trace_id, "032x")
                span_id = format(ctx.span_id, "016x")

            correlation_id = getattr(request.state, "correlation_id", None)
            http_status = response.status_code if response is not None else 500

            logging.getLogger("external.request").info(
                f"{request.method} {request.url.path} -> {http_status} in {duration:.3f}s",
                extra={
                    "trace_id": trace_id,
                    "span_id": span_id,
                    "correlation_id": correlation_id,
                    "http_method": request.method,
                    "http_route": request.url.path,
                    "http_status": http_status,
                },
            )

