package com.metabolic.platform.dto;

import java.util.Map;

public record AnalyzeResponse(
        String traceId,
        Map<String, Object> patientContext,
        Map<String, Object> report,
        String provider
) {
}
