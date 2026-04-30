from fastapi import APIRouter, HTTPException, Request

from app.core.logging_config import get_logger, with_context
from app.domain.models import DiagnosisResponse
from app.services.diagnosis_service import DiagnosisError, DiagnosisService
from shared.schemas.patient_context import PatientContext

router = APIRouter()
logger = get_logger(__name__)
diagnosis_service = DiagnosisService()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"service": "diagnosis-agent", "status": "ok"}


@router.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose(request: Request, patient_context: PatientContext) -> DiagnosisResponse:
    trace_id = request.headers.get("x-trace-id")
    patient_id = str(patient_context.demographics.get("patient_id", "unknown"))
    contextual_logger = with_context(logger, trace_id, patient_id)
    try:
        return diagnosis_service.diagnose(patient_context, trace_id=trace_id)
    except DiagnosisError as exc:
        contextual_logger.warning("Diagnosis error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - guardrail
        contextual_logger.exception("Unexpected diagnosis failure")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
