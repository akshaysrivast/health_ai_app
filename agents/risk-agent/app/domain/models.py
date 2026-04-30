from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from shared.schemas.patient_context import PatientContext


class RiskComputationResponse(BaseModel):
    patient_context: PatientContext
    matched_rules: list[dict[str, Any]] = Field(default_factory=list)
