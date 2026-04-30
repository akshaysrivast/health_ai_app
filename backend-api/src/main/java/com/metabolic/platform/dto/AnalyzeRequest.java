package com.metabolic.platform.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.util.List;
import java.util.Map;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record AnalyzeRequest(
        @NotNull @Size(min = 1, max = 50) Map<String, Object> demographics,
        @NotNull @Size(min = 1, max = 200) List<Map<String, Object>> labs,
        @NotNull @Size(max = 100) Map<String, Object> anthropometry,
        @NotNull @Size(max = 100) Map<String, Object> lifestyle,
        @NotNull @Size(max = 200) Map<String, Object> history,
        Map<String, Object> features,
        Map<String, Object> risks,
        Map<String, Object> diagnosis,
        Map<String, Object> plan
) {
}
