package com.metabolic.platform.service;

import com.metabolic.platform.dto.AnalyzeRequest;
import com.metabolic.platform.exception.BackendApiException;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class InputValidationService {
    public void validate(AnalyzeRequest request) {
        ensureDemographics(request.demographics());
        ensureLabPayload(request.labs());
    }

    private void ensureDemographics(Map<String, Object> demographics) {
        Object patientId = demographics.get("patient_id");
        if (!(patientId instanceof String id) || id.isBlank() || id.length() > 64) {
            throw new BackendApiException("demographics.patient_id is required and must be <= 64 chars");
        }
    }

    private void ensureLabPayload(Iterable<Map<String, Object>> labs) {
        int count = 0;
        for (Map<String, Object> lab : labs) {
            count++;
            Object name = lab.get("name");
            Object value = lab.get("value");
            if (!(name instanceof String n) || n.isBlank() || n.length() > 64) {
                throw new BackendApiException("Each lab result requires a valid name <= 64 chars");
            }
            if (!(value instanceof Number)) {
                throw new BackendApiException("Each lab result requires numeric value");
            }
            double numeric = ((Number) value).doubleValue();
            if (numeric < -1000 || numeric > 100000) {
                throw new BackendApiException("Lab value out of allowed safety range");
            }
        }
        if (count == 0) {
            throw new BackendApiException("At least one lab result is required");
        }
    }
}
