from fastapi import APIRouter, HTTPException, Request

from app.core.logging_config import get_logger, with_context
from app.domain.models import ReportResponse
from app.services.report_service import ReportGenerationError, ReportService
from shared.schemas.patient_context import PatientContext

router = APIRouter()
logger = get_logger(__name__)
report_service = ReportService()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"service": "report-agent", "status": "ok"}


@router.post("/generate-report", response_model=ReportResponse)
async def generate_report(request: Request, patient_context: PatientContext) -> ReportResponse:
    trace_id = request.headers.get("x-trace-id")
    patient_id = str(patient_context.demographics.get("patient_id", "unknown"))
    contextual_logger = with_context(logger, trace_id, patient_id)
    try:
        return report_service.generate(patient_context, trace_id=trace_id)
    except ReportGenerationError as exc:
        contextual_logger.warning("Report generation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - guardrail
        contextual_logger.exception("Unexpected report generation error")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
