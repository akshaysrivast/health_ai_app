from datetime import timedelta

from temporalio import workflow


@workflow.defn
class HealthWorkflow:
    @workflow.run
    async def run(self, patient_id: str) -> dict[str, str]:
        workflow.logger.info("Running health workflow for patient_id=%s", patient_id)
        await workflow.sleep(timedelta(seconds=1))
        return {"patient_id": patient_id, "workflow_status": "completed"}
