from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class Scenario(str, Enum):
    BASELINE = "baseline"
    ASYNC_UPSTREAM = "async_upstream"
    ASYNC_DOWNSTREAM = "async_downstream"


class Broker(str, Enum):
    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"


class MessagingBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class AsyncUpstreamMessage(MessagingBase):
    scenario: Literal[Scenario.ASYNC_UPSTREAM] = Scenario.ASYNC_UPSTREAM
    broker: Broker
    correlation_id: str
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    case_tag: Optional[str] = None
    source: str = "api"


class AsyncDownstreamMessage(MessagingBase):
    scenario: Literal[Scenario.ASYNC_DOWNSTREAM] = Scenario.ASYNC_DOWNSTREAM
    broker: Broker
    correlation_id: str
    status_code: int
    response_time_ms: int
    payload: dict[str, Any]
    remote_latency_ms: Optional[int] = None
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    case_tag: Optional[str] = None
