# przykładowo w app/api/v1/routers/external_proxy.py
from fastapi import APIRouter, Request
from app.services.external_client import call_external_service

router = APIRouter(prefix="/api/v1/external", tags=["external"])

@router.get("/proxy")
def proxy_external(request: Request):
    corr_id = getattr(request.state, "correlation_id", None)
    data = call_external_service(correlation_id=corr_id)
    return {"source": "main_api", "external": data}
