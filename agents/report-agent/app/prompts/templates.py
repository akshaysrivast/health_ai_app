from __future__ import annotations

import json

from shared.schemas.patient_context import PatientContext

PROMPT_TEMPLATE_VERSION = "v1"


def build_structured_prompt(patient_context: PatientContext) -> str:
    """
    Strict prompt that constrains generation to provided context only.
    """
    context_json = json.dumps(patient_context.model_dump(), indent=2, default=str)

    return (
        "You are a clinical report assistant.\n"
        "You must use ONLY facts present in the provided JSON.\n"
        "Do not infer unseen values, do not hallucinate, do not add external medical claims.\n"
        "If data is missing, explicitly state it as 'Not provided in data'.\n\n"
        "Output strictly valid JSON with this schema:\n"
        "{\n"
        '  "doctor_summary": "string",\n'
        '  "patient_friendly_explanation": "string"\n'
        "}\n\n"
        "PatientContext JSON:\n"
        f"{context_json}\n"
    )
