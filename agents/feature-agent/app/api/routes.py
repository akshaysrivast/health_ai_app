from fastapi import APIRouter, HTTPException, Request

from app.core.logging_config import get_logger, with_context
from app.domain.models import FeatureComputationResponse
from app.services.feature_service import FeatureComputationError, FeatureService
from shared.schemas.patient_context import PatientContext

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health")
async def health() -> dict[str, str]:
    return {"service": "feature-agent", "status": "ok"}


@router.post("/compute-features", response_model=FeatureComputationResponse)
async def compute_features(request: Request, patient_context: PatientContext) -> FeatureComputationResponse:
    trace_id = request.headers.get("x-trace-id")
    patient_id = str(patient_context.demographics.get("patient_id", "unknown"))
    contextual_logger = with_context(logger, trace_id, patient_id)
    try:
        return FeatureService.compute_features(patient_context, trace_id=trace_id)
    except FeatureComputationError as exc:
        contextual_logger.warning("Feature computation validation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - guardrail
        contextual_logger.exception("Unexpected feature computation error")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
