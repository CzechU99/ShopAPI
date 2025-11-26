from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.core.config import settings
from app.messaging.publisher import get_publisher
from app.schemas.messaging import (
    AsyncDownstreamMessage,
    AsyncUpstreamMessage,
    Broker,
    Scenario,
)
from app.services.external_client import call_external_service
from app.services.external_result_service import ExternalResultService

router = APIRouter(prefix="/api/v1/external", tags=["external"])


def _resolve_broker(broker_param: str | None) -> Broker:
    broker_value = (
        broker_param.lower()
        if broker_param
        else settings.MESSAGE_BROKER_DEFAULT.lower()
    )
    try:
        return Broker(broker_value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported broker '{broker_value}'",
        ) from exc


def _destination_for(broker: Broker, scenario: Scenario) -> str:
    if scenario == Scenario.ASYNC_UPSTREAM:
        return (
            settings.KAFKA_ASYNC_UPSTREAM_TOPIC
            if broker == Broker.KAFKA
            else settings.RABBITMQ_ASYNC_UPSTREAM_QUEUE
        )
    if scenario == Scenario.ASYNC_DOWNSTREAM:
        return (
            settings.KAFKA_ASYNC_DOWNSTREAM_TOPIC
            if broker == Broker.KAFKA
            else settings.RABBITMQ_ASYNC_DOWNSTREAM_QUEUE
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported messaging scenario",
    )


async def _publish_message(broker: Broker, scenario: Scenario, payload: dict[str, Any]):
    publisher = get_publisher()
    destination = _destination_for(broker, scenario)
    await run_in_threadpool(publisher.publish, broker, destination, payload)


def _extract_remote_latency(payload: Any) -> int | None:
    if not isinstance(payload, dict):
        return None
    latency = payload.get("remote_delay_ms")
    if latency is None:
        latency = payload.get("sleep_seconds")
    return latency


@router.get("/proxy")
async def proxy_external(
    request: Request,
    db: Session = Depends(get_db),
):
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

    result_service.record_success(
        correlation_id=corr_id,
        status_code=data.status_code,
        response_time_ms=data.elapsed_ms,
        payload=data.body,
        remote_latency_ms=_extract_remote_latency(data.body),
    )
    return {
        "source": "main_api",
        "scenario": Scenario.BASELINE.value,
        "correlation_id": corr_id,
        "external": data.body,
    }


@router.post(
    "/fetch/async-upstream",
    status_code=status.HTTP_202_ACCEPTED,
)
async def fetch_async_upstream(
    request: Request,
    broker: str | None = Query(None, description="kafka or rabbitmq"),
    case_tag: str | None = Query(None),
):
    corr_id = getattr(request.state, "correlation_id", None)
    resolved_broker = _resolve_broker(broker)
    message = AsyncUpstreamMessage(
        broker=resolved_broker,
        correlation_id=corr_id or "",
        case_tag=case_tag or request.headers.get("X-K6-TestCase"),
    )
    await _publish_message(
        resolved_broker,
        Scenario.ASYNC_UPSTREAM,
        message.model_dump(mode="json"),
    )
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "status": "accepted",
            "scenario": Scenario.ASYNC_UPSTREAM.value,
            "broker": resolved_broker.value,
            "correlation_id": corr_id,
        },
    )


@router.post("/fetch/async-downstream")
async def fetch_async_downstream(
    request: Request,
    db: Session = Depends(get_db),
    broker: str | None = Query(None),
    case_tag: str | None = Query(None),
):
    corr_id = getattr(request.state, "correlation_id", None)
    resolved_broker = _resolve_broker(broker)
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

    message = AsyncDownstreamMessage(
        broker=resolved_broker,
        correlation_id=corr_id or "",
        status_code=data.status_code,
        response_time_ms=data.elapsed_ms,
        payload=data.body,
        remote_latency_ms=_extract_remote_latency(data.body),
        case_tag=case_tag or request.headers.get("X-K6-TestCase"),
    )
    await _publish_message(
        resolved_broker,
        Scenario.ASYNC_DOWNSTREAM,
        message.model_dump(mode="json"),
    )
    return {
        "source": "main_api",
        "scenario": Scenario.ASYNC_DOWNSTREAM.value,
        "broker": resolved_broker.value,
        "correlation_id": corr_id,
        "external": data.body,
    }
