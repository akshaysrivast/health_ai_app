from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from temporalio import activity
from logging_config import with_context

logger = logging.getLogger(__name__)

FEATURE_AGENT_URL = os.getenv("FEATURE_AGENT_URL", "http://localhost:8001/compute-features")
RISK_AGENT_URL = os.getenv("RISK_AGENT_URL", "http://localhost:8002/compute-risks")
DIAGNOSIS_AGENT_URL = os.getenv("DIAGNOSIS_AGENT_URL", "http://localhost:8003/diagnose")
TREATMENT_AGENT_URL = os.getenv("TREATMENT_AGENT_URL", "http://localhost:8004/treatment-plan")
REPORT_AGENT_URL = os.getenv("REPORT_AGENT_URL", "http://localhost:8005/generate-report")

REQUEST_TIMEOUT_SECONDS = float(os.getenv("AGENT_REQUEST_TIMEOUT_SECONDS", "20"))


@activity.defn
async def call_feature_agent(patient_context: dict[str, Any], trace_id: str) -> dict[str, Any]:
    return await _post_json(FEATURE_AGENT_URL, patient_context, trace_id, "feature-agent")


@activity.defn
async def call_risk_agent(patient_context: dict[str, Any], trace_id: str) -> dict[str, Any]:
    return await _post_json(RISK_AGENT_URL, patient_context, trace_id, "risk-agent")


@activity.defn
async def call_diagnosis_agent(patient_context: dict[str, Any], trace_id: str) -> dict[str, Any]:
    return await _post_json(DIAGNOSIS_AGENT_URL, patient_context, trace_id, "diagnosis-agent")


@activity.defn
async def call_treatment_agent(patient_context: dict[str, Any], trace_id: str) -> dict[str, Any]:
    return await _post_json(TREATMENT_AGENT_URL, patient_context, trace_id, "treatment-agent")


@activity.defn
async def call_report_agent(patient_context: dict[str, Any], trace_id: str) -> dict[str, Any]:
    return await _post_json(REPORT_AGENT_URL, patient_context, trace_id, "report-agent")


async def _post_json(url: str, payload: dict[str, Any], trace_id: str, service_name: str) -> dict[str, Any]:
    headers = {
        "content-type": "application/json",
        "x-trace-id": trace_id,
    }
    patient_id = str(payload.get("demographics", {}).get("patient_id", "unknown"))
    contextual_logger = with_context(logger, trace_id, patient_id)
    contextual_logger.info("Calling %s url=%s", service_name, url)

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    contextual_logger.info("Completed %s", service_name)
    return data
