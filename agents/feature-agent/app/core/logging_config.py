from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

SERVICE_NAME = "feature-agent"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": SERVICE_NAME,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", "unknown"),
            "patient_id": getattr(record, "patient_id", "unknown"),
        }
        return json.dumps(payload, default=str)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.INFO)
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def with_context(logger: logging.Logger, trace_id: str | None, patient_id: str | None) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(
        logger,
        {"trace_id": trace_id or "unknown", "patient_id": patient_id or "unknown"},
    )
