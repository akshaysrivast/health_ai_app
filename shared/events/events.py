from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    event_type: str
    patient_id: str
    trace_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
