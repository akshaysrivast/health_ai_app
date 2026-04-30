from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

from app.adapters.llm_ranker import DiagnosisRanker, NoOpDiagnosisRanker, PlaceholderLlmDiagnosisRanker
from app.core.config import get_rule_engine_file_path, get_rules_file_path, is_llm_refinement_enabled
from app.core.logging_config import get_logger, with_context
from app.domain.models import DiagnosisItem, DiagnosisResponse
from shared.events.publisher import publish_event
from shared.schemas.patient_context import PatientContext

logger = get_logger(__name__)


class DiagnosisError(ValueError):
    pass


class DiagnosisService:
    def __init__(self) -> None:
        self._engine = self._build_engine()
        self._ranker: DiagnosisRanker = (
            PlaceholderLlmDiagnosisRanker() if is_llm_refinement_enabled() else NoOpDiagnosisRanker()
        )

    def diagnose(self, patient_context: PatientContext, trace_id: str | None = None) -> DiagnosisResponse:
        eval_context = _build_evaluation_context(patient_context)
        matched_rules = self._engine.evaluate(eval_context)
        deterministic_diagnoses = _derive_diagnoses_from_rules(matched_rules)
        patient_id = str(patient_context.demographics.get("patient_id", "unknown"))
        contextual_logger = with_context(logger, trace_id, patient_id)

        # Deterministic base always runs first; optional AI refinement runs second.
        ranked_diagnoses = self._ranker.refine(deterministic_diagnoses)

        patient_context.diagnosis["items"] = [item.model_dump() for item in ranked_diagnoses]
        patient_context.diagnosis["matched_rule_count"] = len(matched_rules)
        publish_event(
            "diagnosis",
            {
                "event_type": "diagnosis.ready",
                "trace_id": trace_id or "unknown",
                "patient_id": patient_id,
                "payload": patient_context.diagnosis,
            },
        )

        contextual_logger.info(
            "Diagnosis generated. matched_rules=%d diagnoses=%d llm_refinement=%s",
            len(matched_rules),
            len(ranked_diagnoses),
            is_llm_refinement_enabled(),
        )

        return DiagnosisResponse(patient_context=patient_context, diagnoses=ranked_diagnoses)

    def _build_engine(self) -> Any:
        rules_path = get_rules_file_path()
        if not rules_path.exists():
            raise DiagnosisError(f"Diagnosis rules file not found: {rules_path}")

        with rules_path.open("r", encoding="utf-8") as handle:
            raw_rules = json.load(handle)

        if not isinstance(raw_rules, list):
            raise DiagnosisError("Diagnosis rules file must contain a JSON list")

        rule_engine_cls = _load_rule_engine_class(get_rule_engine_file_path())
        logger.info("Loaded %d diagnosis rules from %s", len(raw_rules), rules_path)
        return rule_engine_cls(raw_rules)


def _load_rule_engine_class(rule_engine_path: Path) -> Any:
    if not rule_engine_path.exists():
        raise DiagnosisError(f"Rule engine file not found: {rule_engine_path}")

    spec = importlib.util.spec_from_file_location("shared_rule_engine", rule_engine_path)
    if spec is None or spec.loader is None:
        raise DiagnosisError(f"Failed to load rule engine module: {rule_engine_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    rule_engine_cls = getattr(module, "RuleEngine", None)
    if rule_engine_cls is None:
        raise DiagnosisError("RuleEngine class not found in shared rule engine module")
    return rule_engine_cls


def _derive_diagnoses_from_rules(matched_rules: list[dict[str, Any]]) -> list[DiagnosisItem]:
    diagnoses: list[DiagnosisItem] = []
    for rule in matched_rules:
        output = rule.get("output", {})
        if not isinstance(output, dict):
            continue

        name = output.get("diagnosis")
        if not isinstance(name, str) or not name.strip():
            # Skip rules that are not diagnosis-producing.
            continue

        base_confidence = float(output.get("base_confidence", 0.55))
        risk_weight = float(output.get("risk_weight", 0.0))
        confidence = max(0.0, min(1.0, base_confidence + risk_weight))
        rationale = output.get("rationale")

        diagnoses.append(
            DiagnosisItem(
                name=name,
                confidence=round(confidence, 3),
                rationale=rationale if isinstance(rationale, str) else None,
                metadata={"source_rule": rule.get("name", "unknown")},
            )
        )

    diagnoses.sort(key=lambda item: item.confidence, reverse=True)
    return diagnoses


def _build_evaluation_context(patient_context: PatientContext) -> dict[str, Any]:
    labs = {lab.name: lab.value for lab in patient_context.labs}
    return {
        "demographics": patient_context.demographics,
        "lifestyle": patient_context.lifestyle,
        "history": patient_context.history,
        "features": patient_context.features,
        "risks": patient_context.risks,
        "plan": patient_context.plan,
        "labs": labs,
        "anthropometry": patient_context.anthropometry.model_dump(),
    }
