from fastapi import APIRouter, HTTPException, Request

from app.core.logging_config import get_logger, with_context
from app.domain.models import RiskComputationResponse
from app.services.risk_service import RiskComputationError, RiskService
from shared.schemas.patient_context import PatientContext

router = APIRouter()
logger = get_logger(__name__)
risk_service = RiskService()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"service": "risk-agent", "status": "ok"}


@router.post("/compute-risks", response_model=RiskComputationResponse)
async def compute_risks(request: Request, patient_context: PatientContext) -> RiskComputationResponse:
    trace_id = request.headers.get("x-trace-id")
    patient_id = str(patient_context.demographics.get("patient_id", "unknown"))
    contextual_logger = with_context(logger, trace_id, patient_id)
    try:
        return risk_service.compute_risks(patient_context, trace_id=trace_id)
    except RiskComputationError as exc:
        contextual_logger.warning("Risk computation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - guardrail
        contextual_logger.exception("Unexpected risk computation error")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
