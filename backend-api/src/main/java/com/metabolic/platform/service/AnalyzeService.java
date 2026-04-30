package com.metabolic.platform.service;

import com.metabolic.platform.config.IntegrationProperties;
import com.metabolic.platform.config.OrchestratorProperties;
import com.metabolic.platform.dto.AnalyzeRequest;
import com.metabolic.platform.dto.AnalyzeResponse;
import com.metabolic.platform.dto.OrchestratorRequest;
import com.metabolic.platform.exception.BackendApiException;
import com.metabolic.platform.exception.OrchestratorCommunicationException;
import java.util.Map;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

@Service
public class AnalyzeService {
    private static final Logger logger = LoggerFactory.getLogger(AnalyzeService.class);

    private final RestClient restClient;
    private final OrchestratorProperties orchestratorProperties;
    private final IntegrationProperties integrationProperties;
    private final InputValidationService inputValidationService;

    public AnalyzeService(
            RestClient restClient,
            OrchestratorProperties orchestratorProperties,
            IntegrationProperties integrationProperties,
            InputValidationService inputValidationService
    ) {
        this.restClient = restClient;
        this.orchestratorProperties = orchestratorProperties;
        this.integrationProperties = integrationProperties;
        this.inputValidationService = inputValidationService;
    }

    public AnalyzeResponse analyze(AnalyzeRequest request) {
        String traceId = UUID.randomUUID().toString();
        String patientId = String.valueOf(request.demographics().getOrDefault("patient_id", "unknown"));
        MDC.put("trace_id", traceId);
        MDC.put("patient_id", patientId);
        logger.info("Analyze request received");
        inputValidationService.validate(request);

        logIntegrationReadiness();

        OrchestratorRequest orchestratorRequest = new OrchestratorRequest(request, traceId);
        String url = orchestratorProperties.baseUrl() + orchestratorProperties.analyzePath();

        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> response = restClient.post()
                    .uri(url)
                    .contentType(MediaType.APPLICATION_JSON)
                    .header("x-trace-id", traceId)
                    .body(orchestratorRequest)
                    .retrieve()
                    .body(Map.class);

            if (response == null) {
                throw new BackendApiException("Orchestrator returned empty response");
            }

            @SuppressWarnings("unchecked")
            Map<String, Object> patientContext = (Map<String, Object>) response.getOrDefault("patient_context", Map.of());
            @SuppressWarnings("unchecked")
            Map<String, Object> report = (Map<String, Object>) response.getOrDefault("report", Map.of());
            String provider = String.valueOf(response.getOrDefault("provider", "unknown"));
            String respTraceId = String.valueOf(response.getOrDefault("trace_id", traceId));

            return new AnalyzeResponse(respTraceId, patientContext, report, provider);
        } catch (RestClientException ex) {
            throw new OrchestratorCommunicationException("Failed to invoke orchestrator workflow", ex);
        } finally {
            MDC.remove("trace_id");
            MDC.remove("patient_id");
        }
    }

    private void logIntegrationReadiness() {
        if (integrationProperties.auth() != null && integrationProperties.auth().enabled()) {
            logger.info("Auth integration enabled; issuer={}", integrationProperties.auth().issuer());
        }
        if (integrationProperties.abha() != null && integrationProperties.abha().enabled()) {
            logger.info("ABHA integration enabled; endpoint={}", integrationProperties.abha().baseUrl());
        }
    }
}
