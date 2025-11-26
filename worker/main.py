from __future__ import annotations

import json
import logging
import os
import signal
import sys
import time
from typing import Any, Callable

from kafka import KafkaConsumer
import pika

from app.core.config import settings
from app.db.session import SessionLocal
from app.schemas.messaging import Broker, Scenario
from app.services.external_result_service import ExternalResultService
from worker.external_client import call_external_service_sync

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("external.worker")

try:
    SCENARIO = Scenario(
        os.getenv("JOB_SCENARIO", Scenario.ASYNC_UPSTREAM.value)
    )
except ValueError as exc:
    raise RuntimeError("Unsupported JOB_SCENARIO value") from exc

try:
    BROKER = Broker(
        os.getenv("MESSAGE_BROKER", settings.MESSAGE_BROKER_DEFAULT).lower()
    )
except ValueError as exc:
    raise RuntimeError("Unsupported MESSAGE_BROKER value") from exc
GROUP_ID = os.getenv("KAFKA_GROUP_ID", f"{SCENARIO.value}-worker")


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
    raise RuntimeError(f"Unsupported scenario {scenario}")


def _extract_remote_latency(payload: Any) -> int | None:
    if not isinstance(payload, dict):
        return None
    latency = payload.get("remote_delay_ms")
    if latency is None:
        latency = payload.get("sleep_seconds")
    return latency


def _process_async_upstream(payload: dict[str, Any]) -> None:
    correlation_id = payload.get("correlation_id")
    db = SessionLocal()
    service = ExternalResultService(db)
    start = time.perf_counter()
    try:
        response = call_external_service_sync(correlation_id=correlation_id)
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        service.record_failure(
            correlation_id=correlation_id,
            response_time_ms=duration_ms,
            error_message=str(exc),
        )
        db.close()
        raise
    else:
        service.record_success(
            correlation_id=correlation_id,
            status_code=response.status_code,
            response_time_ms=response.elapsed_ms,
            payload=response.body,
            remote_latency_ms=_extract_remote_latency(response.body),
        )
        db.close()


def _process_async_downstream(payload: dict[str, Any]) -> None:
    db = SessionLocal()
    service = ExternalResultService(db)
    try:
        service.record_success(
            correlation_id=payload.get("correlation_id"),
            status_code=int(payload.get("status_code", 200)),
            response_time_ms=int(payload.get("response_time_ms", 0)),
            payload=payload.get("payload") or {},
            remote_latency_ms=_extract_remote_latency(payload.get("payload")),
        )
    finally:
        db.close()


HANDLERS: dict[Scenario, Callable[[dict[str, Any]], None]] = {
    Scenario.ASYNC_UPSTREAM: _process_async_upstream,
    Scenario.ASYNC_DOWNSTREAM: _process_async_downstream,
}


def _handle_payload(payload: dict[str, Any]) -> None:
    handler = HANDLERS.get(SCENARIO)
    if not handler:
        raise RuntimeError(f"No handler for scenario {SCENARIO}")
    handler(payload)


def _run_kafka() -> None:
    topic = _destination_for(BROKER, SCENARIO)
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(","),
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        group_id=GROUP_ID,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        max_poll_records=1,
    )
    logger.info(
        "Kafka worker started", extra={"topic": topic, "scenario": SCENARIO.value}
    )
    try:
        for message in consumer:
            try:
                _handle_payload(message.value)
                consumer.commit()
            except Exception:
                logger.exception("Kafka message processing failed")
                time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Kafka worker interrupted")
    finally:
        consumer.close()


def _run_rabbitmq() -> None:
    queue = _destination_for(BROKER, SCENARIO)
    params = pika.URLParameters(settings.RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_qos(prefetch_count=1)

    logger.info(
        "RabbitMQ worker started", extra={"queue": queue, "scenario": SCENARIO.value}
    )

    def callback(ch, method, properties, body):
        try:
            payload = json.loads(body.decode("utf-8"))
            _handle_payload(payload)
        except Exception:
            logger.exception("RabbitMQ message processing failed")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            time.sleep(1)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=False)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("RabbitMQ worker interrupted")
    finally:
        if connection.is_open:
            connection.close()


def main() -> None:
    logger.info(
        "Worker booting",
        extra={"broker": BROKER.value, "scenario": SCENARIO.value},
    )
    if BROKER == Broker.KAFKA:
        _run_kafka()
    else:
        _run_rabbitmq()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    main()
