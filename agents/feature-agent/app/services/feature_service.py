from __future__ import annotations

from uuid import uuid4

from shared.constants import FEATURES_COMPUTED
from shared.events.events import BaseEvent
from shared.events.publisher import publish_event
from shared.schemas.patient_context import Anthropometry, PatientContext

from app.core.logging_config import get_logger, with_context
from app.domain.models import FeatureComputationResponse

logger = get_logger(__name__)


class FeatureComputationError(ValueError):
    pass


class FeatureService:
    @staticmethod
    def compute_features(patient_context: PatientContext, trace_id: str | None = None) -> FeatureComputationResponse:
        anthropometry = patient_context.anthropometry
        bmi = _compute_bmi(anthropometry)
        waist_to_height_ratio = _compute_waist_to_height_ratio(anthropometry)
        metabolic_score = _compute_basic_metabolic_score(
            bmi=bmi,
            waist_to_height_ratio=waist_to_height_ratio,
            patient_context=patient_context,
        )

        patient_context.features.update(
            {
                "bmi": bmi,
                "waist_to_height_ratio": waist_to_height_ratio,
                "basic_metabolic_score": metabolic_score,
            }
        )

        patient_id = _resolve_patient_id(patient_context)
        contextual_logger = with_context(logger, trace_id, patient_id)
        event = BaseEvent(
            event_type=FEATURES_COMPUTED,
            patient_id=patient_id,
            trace_id=trace_id or str(uuid4()),
            payload={
                "features": patient_context.features,
            },
        )

        contextual_logger.info(
            "Features computed for patient_id=%s bmi=%.2f whtr=%.3f score=%.2f",
            patient_id,
            bmi,
            waist_to_height_ratio,
            metabolic_score,
        )
        publish_event("features", event.model_dump())

        return FeatureComputationResponse(patient_context=patient_context, event=event)


def _compute_bmi(anthropometry: Anthropometry) -> float:
    if anthropometry.height_cm is None or anthropometry.weight_kg is None:
        raise FeatureComputationError("height_cm and weight_kg are required to compute BMI")

    if anthropometry.height_cm <= 0 or anthropometry.weight_kg <= 0:
        raise FeatureComputationError("height_cm and weight_kg must be positive")

    height_m = anthropometry.height_cm / 100.0
    return round(anthropometry.weight_kg / (height_m * height_m), 2)


def _compute_waist_to_height_ratio(anthropometry: Anthropometry) -> float:
    if anthropometry.height_cm is None or anthropometry.waist_cm is None:
        raise FeatureComputationError("height_cm and waist_cm are required to compute waist-to-height ratio")

    if anthropometry.height_cm <= 0 or anthropometry.waist_cm <= 0:
        raise FeatureComputationError("height_cm and waist_cm must be positive")

    return round(anthropometry.waist_cm / anthropometry.height_cm, 3)


def _compute_basic_metabolic_score(
    bmi: float,
    waist_to_height_ratio: float,
    patient_context: PatientContext,
) -> float:
    # Placeholder formula for iterative clinical calibration.
    fasting_glucose = _extract_numeric_lab(patient_context, "fasting_glucose", default=95.0)
    hba1c = _extract_numeric_lab(patient_context, "hba1c", default=5.4)
    score = (0.35 * bmi) + (35.0 * waist_to_height_ratio) + (0.05 * fasting_glucose) + (5.0 * hba1c)
    return round(score, 2)


def _extract_numeric_lab(patient_context: PatientContext, name: str, default: float) -> float:
    for lab in patient_context.labs:
        if lab.name.lower() == name.lower() and isinstance(lab.value, (int, float)):
            return float(lab.value)
    return default


def _resolve_patient_id(patient_context: PatientContext) -> str:
    demographics = patient_context.demographics
    for key in ("patient_id", "id", "member_id"):
        value = demographics.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return "unknown-patient"
