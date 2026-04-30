from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LabResult(BaseModel):
    name: str
    value: float | int | str | bool
    unit: str | None = None
    reference_range: str | None = None
    measured_at: str | None = None


class Anthropometry(BaseModel):
    height_cm: float | None = None
    weight_kg: float | None = None
    bmi: float | None = None
    waist_cm: float | None = None
    hip_cm: float | None = None
    body_fat_percent: float | None = None


class PatientContext(BaseModel):
    demographics: dict[str, Any] = Field(default_factory=dict)
    labs: list[LabResult] = Field(default_factory=list)
    anthropometry: Anthropometry = Field(default_factory=Anthropometry)
    lifestyle: dict[str, Any] = Field(default_factory=dict)
    history: dict[str, Any] = Field(default_factory=dict)
    features: dict[str, Any] = Field(default_factory=dict)
    risks: dict[str, Any] = Field(default_factory=dict)
    diagnosis: dict[str, Any] = Field(default_factory=dict)
    plan: dict[str, Any] = Field(default_factory=dict)
