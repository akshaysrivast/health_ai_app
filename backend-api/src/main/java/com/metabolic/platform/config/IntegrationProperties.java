package com.metabolic.platform.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "integrations")
public record IntegrationProperties(
        Auth auth,
        Abha abha
) {
    public record Auth(
            boolean enabled,
            String issuer,
            String audience
    ) {
    }

    public record Abha(
            boolean enabled,
            String baseUrl
    ) {
    }
}
