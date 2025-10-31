from fastapi import FastAPI, Request
from telemetry.tracing import setup_tracing
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
from prometheus_fastapi_instrumentator import Instrumentator


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-Id", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-Id"] = correlation_id
        return response


app = FastAPI(title="External Service")

# Init OpenTelemetry tracing
setup_tracing(app)

# Correlation ID propagation
app.add_middleware(CorrelationIdMiddleware)

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
