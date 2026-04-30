from __future__ import annotations

from app.adapters.llm_provider import LlmProvider, OpenAiCompatibleProvider, TemplateOnlyProvider
from app.core.config import get_llm_provider
from app.core.logging_config import get_logger, with_context
from app.domain.models import ReportResponse
from app.prompts.templates import PROMPT_TEMPLATE_VERSION, build_structured_prompt
from shared.schemas.patient_context import PatientContext

logger = get_logger(__name__)


class ReportGenerationError(ValueError):
    pass


class ReportService:
    def __init__(self) -> None:
        self.provider_name = get_llm_provider()
        self.provider: LlmProvider = self._build_provider(self.provider_name)

    def generate(self, patient_context: PatientContext, trace_id: str | None = None) -> ReportResponse:
        prompt = build_structured_prompt(patient_context)
        patient_id = str(patient_context.demographics.get("patient_id", "unknown"))
        contextual_logger = with_context(logger, trace_id, patient_id)
        try:
            report = self.provider.generate_report(prompt, patient_context)
        except Exception as exc:
            raise ReportGenerationError(f"Report generation failed: {exc}") from exc

        contextual_logger.info("Generated report with provider=%s", self.provider_name)
        return ReportResponse(
            report=report,
            provider=self.provider_name,
            prompt_template_version=PROMPT_TEMPLATE_VERSION,
        )

    @staticmethod
    def _build_provider(provider_name: str) -> LlmProvider:
        if provider_name == "template":
            return TemplateOnlyProvider()
        if provider_name == "openai_compatible":
            return OpenAiCompatibleProvider()
        raise ReportGenerationError(f"Unsupported REPORT_LLM_PROVIDER: {provider_name}")
