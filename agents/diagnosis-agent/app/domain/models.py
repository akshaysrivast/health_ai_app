from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from shared.schemas.patient_context import PatientContext


class DiagnosisItem(BaseModel):
    name: str
    confidence: float
    rationale: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DiagnosisResponse(BaseModel):
    patient_context: PatientContext
    diagnoses: list[DiagnosisItem] = Field(default_factory=list)
