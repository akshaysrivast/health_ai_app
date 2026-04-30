from __future__ import annotations

import json
from typing import Protocol

import httpx

from app.core.config import (
    get_openai_compatible_api_key,
    get_openai_compatible_model,
    get_openai_compatible_url,
)
from app.domain.models import GeneratedReport
from shared.schemas.patient_context import PatientContext


class LlmProvider(Protocol):
    def generate_report(self, prompt: str, patient_context: PatientContext) -> GeneratedReport:
        ...


class TemplateOnlyProvider:
    """
    Deterministic fallback provider that uses only provided data.
    Useful for local development and safe default behavior.
    """

    def generate_report(self, prompt: str, patient_context: PatientContext) -> GeneratedReport:
        del prompt
        diagnosis_items = patient_context.diagnosis.get("items", [])
        diagnosis_names = [
            item.get("name")
            for item in diagnosis_items
            if isinstance(item, dict) and isinstance(item.get("name"), str)
        ]
        diagnosis_text = ", ".join(diagnosis_names) if diagnosis_names else "Not provided in data"

        doctor_summary = (
            f"Clinical summary based on provided context: diagnoses={diagnosis_text}. "
            f"Risk data={patient_context.risks if patient_context.risks else 'Not provided in data'}. "
            f"Planned interventions={patient_context.plan if patient_context.plan else 'Not provided in data'}."
        )

        patient_explanation = (
            "Based on the information available, your care team has identified "
            f"{diagnosis_text}. Your plan currently includes: "
            f"{patient_context.plan if patient_context.plan else 'Not provided in data'}."
        )

        return GeneratedReport(
            doctor_summary=doctor_summary,
            patient_friendly_explanation=patient_explanation,
        )


class OpenAiCompatibleProvider:
    """
    Configurable provider for OpenAI-compatible chat completion APIs.
    """

    def generate_report(self, prompt: str, patient_context: PatientContext) -> GeneratedReport:
        del patient_context
        api_key = get_openai_compatible_api_key()
        if not api_key:
            raise ValueError("REPORT_LLM_API_KEY is required for provider 'openai_compatible'")

        payload = {
            "model": get_openai_compatible_model(),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {api_key}"}

        with httpx.Client(timeout=30.0) as client:
            response = client.post(get_openai_compatible_url(), headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        _validate_llm_payload(parsed)

        report = GeneratedReport(
            doctor_summary=str(parsed.get("doctor_summary", "")),
            patient_friendly_explanation=str(parsed.get("patient_friendly_explanation", "")),
        )
        _validate_safety_language(report)
        return report


def _validate_llm_payload(parsed: object) -> None:
    if not isinstance(parsed, dict):
        raise ValueError("LLM response must be a JSON object")
    required = {"doctor_summary", "patient_friendly_explanation"}
    missing = required - set(parsed.keys())
    if missing:
        raise ValueError(f"LLM response missing fields: {sorted(missing)}")


def _validate_safety_language(report: GeneratedReport) -> None:
    text = f"{report.doctor_summary}\n{report.patient_friendly_explanation}".lower()
    blocked_terms = [
        "guaranteed cure",
        "definitive cure",
        "ignore your doctor",
        "stop all medication",
    ]
    for term in blocked_terms:
        if term in text:
            raise ValueError("LLM output failed healthcare safety language validation")
