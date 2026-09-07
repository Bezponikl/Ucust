package com.n4d3sh1k4.generative_orchestration_service.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.util.UUID;

@Service
@Slf4j
public class QuotaClient {

    private final RestClient restClient;

    public QuotaClient(@Value("${services.billing-service.uri}") String billingUri) {
        this.restClient = RestClient.create(billingUri);
    }

    public CheckQuotaResponse checkQuota(UUID userId, String feature, int requested) {
        try {
            return restClient.post()
                    .uri("/internal/quota/check")
                    .body(new CheckQuotaRequest(userId, feature, requested))
                    .retrieve()
                    .body(CheckQuotaResponse.class);
        } catch (Exception e) {
            log.error("Failed to check quota for user {} feature {}: {}", userId, feature, e.getMessage());
            return new CheckQuotaResponse(false, 0, 0, 0, "unknown");
        }
    }

    public void incrementUsage(UUID userId, String feature, int count) {
        try {
            for (int i = 0; i < count; i++) {
                restClient.post()
                        .uri("/internal/quota/use/{userId}/{feature}", userId, feature)
                        .retrieve()
                        .toBodilessEntity();
            }
        } catch (Exception e) {
            log.error("Failed to increment usage for user {} feature {}: {}", userId, feature, e.getMessage());
        }
    }

    public record CheckQuotaRequest(UUID userId, String feature, int requested) {}
    public record CheckQuotaResponse(boolean allowed, int remaining, int limit, int used, String tariffName) {
        public static CheckQuotaResponse unlimited() {
            return new CheckQuotaResponse(true, Integer.MAX_VALUE, -1, 0, "—");
        }
    }
}
