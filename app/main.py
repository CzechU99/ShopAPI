from fastapi import FastAPI
from app.db.session import engine
from app.models.models import Base
from app.api.v1.routers import users, products
from app.core.telemetry import init_tracing

app = FastAPI(title="Shop API (dev)", version="0.1.0")

# create tables automatically on startup (dev convenience)
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    # init OpenTelemetry (console exporter for dev)
    try:
        init_tracing(app)
    except Exception:
        pass

# include routers
app.include_router(users.router)
app.include_router(products.router)

@app.get("/")
def root():
    return {"message": "Shop API — running. Try /docs"}
