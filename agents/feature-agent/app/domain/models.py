from __future__ import annotations

from pydantic import BaseModel

from shared.events.events import BaseEvent
from shared.schemas.patient_context import PatientContext


class FeatureComputationResponse(BaseModel):
    patient_context: PatientContext
    event: BaseEvent
