from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.session import engine
from app.models.models import Base
from app.api.v1.routers import users, products, orders, categories, tags, reviews, external_proxy
from app.middlewares.correlation import CorrelationIdMiddleware
from app.telemetry.tracing import setup_tracing
from prometheus_fastapi_instrumentator import Instrumentator


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        setup_tracing(app, "main_api")
    except Exception:
        # Do not break startup if tracing backend is unavailable
        pass
    yield


app = FastAPI(title="Shop API", version="1.0.0", lifespan=lifespan)

app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(categories.router)
app.include_router(tags.router)
app.include_router(reviews.router)
app.include_router(external_proxy.router)

app.add_middleware(CorrelationIdMiddleware)

# Expose Prometheus metrics at /metrics
Instrumentator().instrument(app).expose(app, include_in_schema=False)

@app.get("/")
def root():
    return {"message": "Shop API — running. Use /api/v1/... or /docs"}
