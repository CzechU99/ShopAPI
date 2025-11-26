# przykładowo w app/api/v1/routers/external_proxy.py
import time

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.services.external_client import call_external_service
from app.services.external_result_service import ExternalResultService

router = APIRouter(prefix="/api/v1/external", tags=["external"])


@router.get("/proxy")
async def proxy_external(request: Request, db: Session = Depends(get_db)):
    corr_id = getattr(request.state, "correlation_id", None)
    result_service = ExternalResultService(db)
    start = time.perf_counter()
    try:
        data = await call_external_service(correlation_id=corr_id)
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        result_service.record_failure(
            correlation_id=corr_id,
            response_time_ms=duration_ms,
            error_message=str(exc),
        )
        raise

    sleep_seconds = None
    if isinstance(data.body, dict):
        sleep_seconds = data.body.get("sleep_seconds")

    result_service.record_success(
        correlation_id=corr_id,
        status_code=data.status_code,
        response_time_ms=data.elapsed_ms,
        payload=data.body,
        sleep_seconds=sleep_seconds,
    )
    return {"source": "main_api", "external": data.body}
