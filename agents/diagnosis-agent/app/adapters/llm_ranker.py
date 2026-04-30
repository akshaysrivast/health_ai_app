from __future__ import annotations

from typing import Protocol

from app.domain.models import DiagnosisItem


class DiagnosisRanker(Protocol):
    def refine(self, diagnoses: list[DiagnosisItem]) -> list[DiagnosisItem]:
        ...


class NoOpDiagnosisRanker:
    def refine(self, diagnoses: list[DiagnosisItem]) -> list[DiagnosisItem]:
        return diagnoses


class PlaceholderLlmDiagnosisRanker:
    """
    Stub adapter for future LLM integration.
    Replace internals with provider-specific call logic when ready.
    """

    def refine(self, diagnoses: list[DiagnosisItem]) -> list[DiagnosisItem]:
        # Deterministic ordering fallback until external LLM is integrated.
        return sorted(diagnoses, key=lambda item: item.confidence, reverse=True)
