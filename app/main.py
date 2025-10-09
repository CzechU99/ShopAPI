from fastapi import FastAPI
from app.db.session import engine
from app.models.models import Base
from app.api.v1.routers import users, products, orders, categories, tags, reviews
from app.core.telemetry import init_tracing

app = FastAPI(title="Shop API", version="1.0.0")

@app.on_event("startup")
def on_startup():
    # convenience for dev: create tables if missing (migrations recommended for prod)
    Base.metadata.create_all(bind=engine)
    try:
        init_tracing(app)
    except Exception:
        pass

# versioned routers
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(categories.router)
app.include_router(tags.router)
app.include_router(reviews.router)

@app.get("/")
def root():
    return {"message": "Shop API — running. Use /api/v1/... or /docs"}
