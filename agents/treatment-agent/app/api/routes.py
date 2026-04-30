from fastapi import APIRouter, HTTPException, Request

from app.core.logging_config import get_logger, with_context
from app.domain.models import TreatmentPlanResponse
from app.services.treatment_service import TreatmentPlanError, TreatmentService
from shared.schemas.patient_context import PatientContext

router = APIRouter()
logger = get_logger(__name__)
treatment_service = TreatmentService()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"service": "treatment-agent", "status": "ok"}


@router.post("/treatment-plan", response_model=TreatmentPlanResponse)
async def treatment_plan(request: Request, patient_context: PatientContext) -> TreatmentPlanResponse:
    trace_id = request.headers.get("x-trace-id")
    patient_id = str(patient_context.demographics.get("patient_id", "unknown"))
    contextual_logger = with_context(logger, trace_id, patient_id)
    try:
        return treatment_service.build_treatment_plan(patient_context, trace_id=trace_id)
    except TreatmentPlanError as exc:
        contextual_logger.warning("Treatment plan generation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - guardrail
        contextual_logger.exception("Unexpected treatment plan generation error")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
