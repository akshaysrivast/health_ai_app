from __future__ import annotations

from pydantic import BaseModel, Field

from shared.schemas.patient_context import PatientContext


class GeneratedReport(BaseModel):
    doctor_summary: str = Field(min_length=20, max_length=4000)
    patient_friendly_explanation: str = Field(min_length=20, max_length=4000)


class ReportResponse(BaseModel):
    report: GeneratedReport
    provider: str
    prompt_template_version: str
