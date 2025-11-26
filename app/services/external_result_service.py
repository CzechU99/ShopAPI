from __future__ import annotations
from typing import Any, Optional
from sqlalchemy.orm import Session
from app.models.models import ExternalCallResult


class ExternalResultService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _create_record(
        self,
        *,
        correlation_id: Optional[str],
        success: bool,
        response_time_ms: int,
        status_code: Optional[int] = None,
        payload: Optional[dict[str, Any]] = None,
        remote_latency_ms: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> ExternalCallResult:
        record = ExternalCallResult(
            correlation_id=correlation_id,
            status_code=status_code,
            success=success,
            response_time_ms=response_time_ms,
            payload=payload,
            sleep_seconds=remote_latency_ms,
            error_message=error_message,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def record_success(
        self,
        *,
        correlation_id: Optional[str],
        status_code: int,
        response_time_ms: int,
        payload: dict[str, Any],
        remote_latency_ms: Optional[int],
    ) -> ExternalCallResult:
        return self._create_record(
            correlation_id=correlation_id,
            success=True,
            status_code=status_code,
            response_time_ms=response_time_ms,
            payload=payload,
            remote_latency_ms=remote_latency_ms,
        )

    def record_failure(
        self,
        *,
        correlation_id: Optional[str],
        response_time_ms: int,
        error_message: str,
        status_code: Optional[int] = None,
    ) -> ExternalCallResult:
        return self._create_record(
            correlation_id=correlation_id,
            success=False,
            status_code=status_code,
            response_time_ms=response_time_ms,
            payload=None,
            remote_latency_ms=None,
            error_message=error_message[:255],
        )
