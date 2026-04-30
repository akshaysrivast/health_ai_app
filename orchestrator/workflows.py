from __future__ import annotations

from datetime import timedelta
from typing import Any

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import (
        call_diagnosis_agent,
        call_feature_agent,
        call_report_agent,
        call_risk_agent,
        call_treatment_agent,
    )


@workflow.defn
class MetabolicPipelineWorkflow:
    @workflow.run
    async def run(self, patient_context: dict[str, Any], trace_id: str) -> dict[str, Any]:
        workflow.logger.info("Workflow started trace_id=%s", trace_id)

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            backoff_coefficient=2.0,
            maximum_interval=timedelta(seconds=10),
            maximum_attempts=3,
        )

        step_timeout = timedelta(seconds=30)

        feature_response = await workflow.execute_activity(
            call_feature_agent,
            args=[patient_context, trace_id],
            start_to_close_timeout=step_timeout,
            retry_policy=retry_policy,
        )
        ctx = feature_response["patient_context"]

        risk_response = await workflow.execute_activity(
            call_risk_agent,
            args=[ctx, trace_id],
            start_to_close_timeout=step_timeout,
            retry_policy=retry_policy,
        )
        ctx = risk_response["patient_context"]

        diagnosis_response = await workflow.execute_activity(
            call_diagnosis_agent,
            args=[ctx, trace_id],
            start_to_close_timeout=step_timeout,
            retry_policy=retry_policy,
        )
        ctx = diagnosis_response["patient_context"]

        treatment_response = await workflow.execute_activity(
            call_treatment_agent,
            args=[ctx, trace_id],
            start_to_close_timeout=step_timeout,
            retry_policy=retry_policy,
        )
        ctx = treatment_response["patient_context"]

        report_response = await workflow.execute_activity(
            call_report_agent,
            args=[ctx, trace_id],
            start_to_close_timeout=step_timeout,
            retry_policy=retry_policy,
        )

        workflow.logger.info("Workflow completed trace_id=%s", trace_id)
        return {
            "trace_id": trace_id,
            "patient_context": ctx,
            "report": report_response.get("report"),
            "provider": report_response.get("provider"),
        }
