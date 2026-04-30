from __future__ import annotations

import asyncio
import logging
import os

from temporalio.client import Client
from temporalio.worker import Worker
from logging_config import configure_logging

from activities import (
    call_diagnosis_agent,
    call_feature_agent,
    call_report_agent,
    call_risk_agent,
    call_treatment_agent,
)
from workflows import MetabolicPipelineWorkflow


async def main() -> None:
    configure_logging()
    logger = logging.getLogger(__name__)

    temporal_address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    task_queue = os.getenv("TEMPORAL_TASK_QUEUE", "metabolic-ai-task-queue")

    client = await Client.connect(temporal_address)

    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[MetabolicPipelineWorkflow],
        activities=[
            call_feature_agent,
            call_risk_agent,
            call_diagnosis_agent,
            call_treatment_agent,
            call_report_agent,
        ],
    )

    logger.info("Worker started temporal=%s task_queue=%s", temporal_address, task_queue)
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
