from fastapi import FastAPI, Request
from telemetry.tracing import setup_tracing
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
from prometheus_fastapi_instrumentator import Instrumentator
from telemetry.tracing import setup_tracing
from telemetry.logging_config import setup_json_logging
from middlewares.request_logging import RequestLoggingMiddleware


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
    # echo correlation id to demonstrate propagation
    return {
        "status": "ok",
        "data": "Hello from external service!",
        "correlation_id": getattr(request.state, "correlation_id", None),
    }
