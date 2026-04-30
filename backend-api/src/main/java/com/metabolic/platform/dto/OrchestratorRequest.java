package com.metabolic.platform.dto;

public record OrchestratorRequest(
        AnalyzeRequest patientContext,
        String traceId
) {
}
