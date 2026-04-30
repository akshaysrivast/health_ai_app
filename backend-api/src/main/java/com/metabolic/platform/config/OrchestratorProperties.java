package com.metabolic.platform.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "orchestrator.api")
public record OrchestratorProperties(
        String baseUrl,
        String analyzePath
) {
}
