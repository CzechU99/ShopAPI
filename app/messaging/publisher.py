from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from kafka import KafkaProducer
import pika
from pika.adapters.blocking_connection import BlockingChannel

from app.core.config import settings
from app.schemas.messaging import Broker


def _create_kafka_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(","),
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        linger_ms=5,
        retries=5,
    )


class MessagePublisher:
    def __init__(self) -> None:
        self._kafka_producer: KafkaProducer | None = None
        self._rabbit_connection: pika.BlockingConnection | None = None
        self._rabbit_channel: BlockingChannel | None = (
            None
        )

    def _ensure_kafka(self) -> KafkaProducer:
        if self._kafka_producer is None:
            self._kafka_producer = _create_kafka_producer()
        return self._kafka_producer

    def _ensure_rabbit(self) -> BlockingChannel:
        if (
            self._rabbit_connection is None
            or self._rabbit_connection.is_closed
            or self._rabbit_channel is None
            or self._rabbit_channel.is_closed
        ):
            params = pika.URLParameters(settings.RABBITMQ_URL)
            self._rabbit_connection = pika.BlockingConnection(params)
            self._rabbit_channel = self._rabbit_connection.channel()
        return self._rabbit_channel

    def publish(self, broker: Broker, destination: str, payload: dict[str, Any]):
        if broker == Broker.KAFKA:
            producer = self._ensure_kafka()
            future = producer.send(destination, payload)
            future.get(timeout=10)
        else:
            channel = self._ensure_rabbit()
            channel.queue_declare(queue=destination, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=destination,
                body=json.dumps(payload).encode("utf-8"),
                properties=pika.BasicProperties(delivery_mode=2),
            )


@lru_cache(maxsize=1)
def get_publisher() -> MessagePublisher:
    return MessagePublisher()
