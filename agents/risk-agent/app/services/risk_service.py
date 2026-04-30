from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

from app.core.config import get_rule_engine_file_path, get_rules_file_path
from app.core.logging_config import get_logger, with_context
from app.domain.models import RiskComputationResponse
from shared.events.publisher import publish_event
from shared.schemas.patient_context import PatientContext

logger = get_logger(__name__)


class RiskComputationError(ValueError):
    pass


class RiskService:
    def __init__(self) -> None:
        self._engine = self._build_engine()

    def compute_risks(self, patient_context: PatientContext, trace_id: str | None = None) -> RiskComputationResponse:
        evaluation_context = _build_evaluation_context(patient_context)
        matched_rules = self._engine.evaluate(evaluation_context)
        patient_id = str(patient_context.demographics.get("patient_id", "unknown"))
        contextual_logger = with_context(logger, trace_id, patient_id)

        patient_context.risks["matched_rules"] = matched_rules
        patient_context.risks["risk_levels"] = [
            rule["output"].get("risk_level")
            for rule in matched_rules
            if isinstance(rule.get("output"), dict) and rule["output"].get("risk_level")
        ]
        publish_event(
            "risks",
            {
                "event_type": "risks.computed",
                "trace_id": trace_id or "unknown",
                "patient_id": patient_id,
                "payload": {"matched_rules": matched_rules, "risk_levels": patient_context.risks["risk_levels"]},
            },
        )

        contextual_logger.info("Computed risks with %d matched rules", len(matched_rules))
        return RiskComputationResponse(patient_context=patient_context, matched_rules=matched_rules)

    def _build_engine(self) -> Any:
        rules_path = get_rules_file_path()
        if not rules_path.exists():
            raise RiskComputationError(f"Rules file not found: {rules_path}")

        with rules_path.open("r", encoding="utf-8") as handle:
            raw_rules = json.load(handle)

        if not isinstance(raw_rules, list):
            raise RiskComputationError("Rules file must contain a JSON list")

        rule_engine_cls = _load_rule_engine_class(get_rule_engine_file_path())
        logger.info("Loaded %d risk rules from %s", len(raw_rules), rules_path)
        return rule_engine_cls(raw_rules)


def _load_rule_engine_class(rule_engine_path: Path) -> Any:
    if not rule_engine_path.exists():
        raise RiskComputationError(f"Rule engine file not found: {rule_engine_path}")

    spec = importlib.util.spec_from_file_location("shared_rule_engine", rule_engine_path)
    if spec is None or spec.loader is None:
        raise RiskComputationError(f"Failed to load rule engine module: {rule_engine_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    rule_engine_cls = getattr(module, "RuleEngine", None)
    if rule_engine_cls is None:
        raise RiskComputationError("RuleEngine class not found in shared rule engine module")
    return rule_engine_cls


def _build_evaluation_context(patient_context: PatientContext) -> dict[str, Any]:
    lab_map: dict[str, Any] = {}
    for lab in patient_context.labs:
        # Convert lab results list into a flat key-value dictionary for rules.
        lab_map[lab.name] = lab.value

    anthropometry = patient_context.anthropometry.model_dump()

    return {
        "demographics": patient_context.demographics,
        "lifestyle": patient_context.lifestyle,
        "history": patient_context.history,
        "features": patient_context.features,
        "diagnosis": patient_context.diagnosis,
        "plan": patient_context.plan,
        "labs": lab_map,
        "anthropometry": anthropometry,
    }
