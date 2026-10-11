import json
import logging
import os
from collections.abc import Callable
from typing import Any

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

logger = logging.getLogger(__name__)


def rabbit_connection_parameters() -> pika.ConnectionParameters:
    host = os.getenv("RABBIT_HOST", "rabbitmq")
    port = int(os.getenv("RABBIT_PORT", "5672"))
    user = os.getenv("RABBIT_USER", "guest")
    password = os.getenv("RABBIT_PASSWORD", "guest")
    vhost = os.getenv("RABBIT_VHOST", "/")

    credentials = pika.PlainCredentials(user, password)
    return pika.ConnectionParameters(
        host=host,
        port=port,
        virtual_host=vhost,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300,
    )


class RabbitMQConnection:
    """Single blocking connection + channel for publish or consume (one thread)."""

    def __init__(self) -> None:
        self._connection = pika.BlockingConnection(rabbit_connection_parameters())
        self._channel: BlockingChannel = self._connection.channel()
        logger.info("RabbitMQ connected host=%s", os.getenv("RABBIT_HOST", "rabbitmq"))

    @property
    def channel(self) -> BlockingChannel:
        return self._channel

    def declare_queue(self, queue_name: str, durable: bool = True) -> None:
        self._channel.queue_declare(queue=queue_name, durable=durable)

    def publish_json(self, queue_name: str, payload: dict[str, Any], durable: bool = True) -> None:
        self.declare_queue(queue_name, durable=durable)
        body = json.dumps(payload).encode("utf-8")
        self._channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=body,
            properties=BasicProperties(
                delivery_mode=2 if durable else 1,
                content_type="application/json",
            ),
        )
        logger.info("Published to queue=%s payload_keys=%s", queue_name, list(payload.keys()))

    def close(self) -> None:
        if self._connection.is_open:
            self._connection.close()
            logger.info("RabbitMQ connection closed")


def consume_queue(
    queue_name: str,
    on_message: Callable[[dict[str, Any]], None],
    durable: bool = True,
) -> None:
    """
    Blocking consume loop — run in a dedicated thread, not on the FastAPI event loop.
    """
    connection = RabbitMQConnection()
    channel = connection.channel
    channel.queue_declare(queue=queue_name, durable=durable)
    channel.basic_qos(prefetch_count=1)

    def _callback(
        ch: BlockingChannel,
        method: Basic.Deliver,
        _properties: BasicProperties,
        body: bytes,
    ) -> None:
        try:
            payload = json.loads(body.decode("utf-8"))
            on_message(payload)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            logger.exception("Failed to process message from queue=%s", queue_name)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_consume(queue=queue_name, on_message_callback=_callback, auto_ack=False)
    logger.info("Consuming queue=%s", queue_name)
    channel.start_consuming()
