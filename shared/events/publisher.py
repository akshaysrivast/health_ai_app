from __future__ import annotations

import json
import logging
import os
from typing import Any

from kafka import KafkaProducer

logger = logging.getLogger(__name__)


def publish_event(topic: str, payload: dict[str, Any]) -> None:
    """
    Optionally publish events to Kafka.
    Controlled by env var `ENABLE_EVENT_PUBLISHING` (default false).
    """
    if os.getenv("ENABLE_EVENT_PUBLISHING", "false").lower() not in {"1", "true", "yes"}:
        return

    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers.split(","),
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )
    try:
        producer.send(topic, payload)
        producer.flush(timeout=5)
        logger.info("Published event to topic=%s", topic)
    finally:
        producer.close()
