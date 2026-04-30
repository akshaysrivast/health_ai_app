package com.metabolic.platform;

import com.metabolic.platform.config.IntegrationProperties;
import com.metabolic.platform.config.OrchestratorProperties;
import com.metabolic.platform.config.RateLimitProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

@SpringBootApplication
@EnableConfigurationProperties({OrchestratorProperties.class, IntegrationProperties.class, RateLimitProperties.class})
public class BackendApiApplication {
    public static void main(String[] args) {
        SpringApplication.run(BackendApiApplication.class, args);
    }
}
