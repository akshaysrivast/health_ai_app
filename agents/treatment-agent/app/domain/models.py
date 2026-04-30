from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from shared.schemas.patient_context import PatientContext


class TreatmentSection(BaseModel):
    summary: str
    actions: list[str] = Field(default_factory=list)


class MedicationSuggestion(BaseModel):
    name: str
    note: str


class TreatmentPlan(BaseModel):
    diagnoses_considered: list[str] = Field(default_factory=list)
    diet_plan: TreatmentSection
    exercise: TreatmentSection
    sleep: TreatmentSection
    medication_suggestions: list[MedicationSuggestion] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TreatmentPlanResponse(BaseModel):
    patient_context: PatientContext
    treatment_plan: TreatmentPlan
