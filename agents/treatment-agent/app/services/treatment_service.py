from __future__ import annotations

import json
from typing import Any

from app.core.config import get_protocols_file_path
from app.core.logging_config import get_logger, with_context
from app.domain.models import (
    MedicationSuggestion,
    TreatmentPlan,
    TreatmentPlanResponse,
    TreatmentSection,
)
from shared.events.publisher import publish_event
from shared.schemas.patient_context import PatientContext

logger = get_logger(__name__)


class TreatmentPlanError(ValueError):
    pass


class TreatmentService:
    def __init__(self) -> None:
        self._protocols = self._load_protocols()

    def build_treatment_plan(self, patient_context: PatientContext, trace_id: str | None = None) -> TreatmentPlanResponse:
        diagnoses = _extract_diagnoses(patient_context)
        if not diagnoses:
            raise TreatmentPlanError("No diagnosis found in patient_context.diagnosis.items")
        patient_id = str(patient_context.demographics.get("patient_id", "unknown"))
        contextual_logger = with_context(logger, trace_id, patient_id)

        selected = [_select_protocol(self._protocols, diagnosis) for diagnosis in diagnoses]
        merged_plan = _merge_protocols(diagnoses, selected)

        patient_context.plan = merged_plan.model_dump()
        publish_event(
            "treatment",
            {
                "event_type": "treatment.ready",
                "trace_id": trace_id or "unknown",
                "patient_id": patient_id,
                "payload": patient_context.plan,
            },
        )

        contextual_logger.info("Built treatment plan for %d diagnosis candidates", len(diagnoses))
        return TreatmentPlanResponse(patient_context=patient_context, treatment_plan=merged_plan)

    def _load_protocols(self) -> dict[str, Any]:
        protocols_path = get_protocols_file_path()
        if not protocols_path.exists():
            raise TreatmentPlanError(f"Treatment protocol config not found: {protocols_path}")

        with protocols_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if not isinstance(payload, dict):
            raise TreatmentPlanError("Treatment protocols JSON must be an object")

        protocols = payload.get("protocols")
        default_protocol = payload.get("default_protocol")
        if not isinstance(protocols, dict) or not isinstance(default_protocol, dict):
            raise TreatmentPlanError("Treatment protocols JSON must contain 'protocols' and 'default_protocol'")

        logger.info("Loaded %d treatment protocols from %s", len(protocols), protocols_path)
        return payload


def _extract_diagnoses(patient_context: PatientContext) -> list[str]:
    diagnosis_items = patient_context.diagnosis.get("items", [])
    if not isinstance(diagnosis_items, list):
        return []

    results: list[str] = []
    for item in diagnosis_items:
        if isinstance(item, dict):
            name = item.get("name")
            if isinstance(name, str) and name.strip():
                results.append(name)
    return results


def _select_protocol(payload: dict[str, Any], diagnosis: str) -> dict[str, Any]:
    protocols = payload["protocols"]
    default_protocol = payload["default_protocol"]
    selected = protocols.get(diagnosis, default_protocol)
    if not isinstance(selected, dict):
        raise TreatmentPlanError(f"Invalid protocol object for diagnosis '{diagnosis}'")
    return selected


def _merge_protocols(diagnoses: list[str], protocol_list: list[dict[str, Any]]) -> TreatmentPlan:
    diet_actions: list[str] = []
    exercise_actions: list[str] = []
    sleep_actions: list[str] = []
    medication_suggestions: list[MedicationSuggestion] = []

    for protocol in protocol_list:
        diet = protocol.get("diet_plan", {})
        exercise = protocol.get("exercise", {})
        sleep = protocol.get("sleep", {})
        meds = protocol.get("medication_suggestions", [])

        diet_actions.extend(_as_actions(diet.get("actions")))
        exercise_actions.extend(_as_actions(exercise.get("actions")))
        sleep_actions.extend(_as_actions(sleep.get("actions")))

        if isinstance(meds, list):
            for med in meds:
                if isinstance(med, dict):
                    name = med.get("name")
                    note = med.get("note")
                    if isinstance(name, str) and isinstance(note, str):
                        medication_suggestions.append(MedicationSuggestion(name=name, note=note))

    return TreatmentPlan(
        diagnoses_considered=diagnoses,
        diet_plan=TreatmentSection(summary="Diet recommendations", actions=_dedupe_keep_order(diet_actions)),
        exercise=TreatmentSection(summary="Exercise recommendations", actions=_dedupe_keep_order(exercise_actions)),
        sleep=TreatmentSection(summary="Sleep recommendations", actions=_dedupe_keep_order(sleep_actions)),
        medication_suggestions=_dedupe_medications(medication_suggestions),
        metadata={"strategy": "rule_based", "protocol_count": len(protocol_list)},
    )


def _as_actions(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def _dedupe_medications(items: list[MedicationSuggestion]) -> list[MedicationSuggestion]:
    seen: set[tuple[str, str]] = set()
    deduped: list[MedicationSuggestion] = []
    for med in items:
        key = (med.name, med.note)
        if key not in seen:
            seen.add(key)
            deduped.append(med)
    return deduped
