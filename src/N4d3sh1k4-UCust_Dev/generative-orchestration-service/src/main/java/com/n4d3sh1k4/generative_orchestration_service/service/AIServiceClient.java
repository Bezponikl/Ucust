package com.n4d3sh1k4.generative_orchestration_service.service;

import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.GenerationMode;
import com.n4d3sh1k4.generative_orchestration_service.dto.request_dto.GenerateRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.util.Map;
import java.util.UUID;

@Service
@Slf4j
public class AIServiceClient {

    private final RestClient restClient;

    public AIServiceClient(@Value("${services.ai-service.uri}") String aiServiceUri) {
        this.restClient = RestClient.create(aiServiceUri);
    }

    public SubmitTaskResponse submitTask(UUID taskId, GenerateRequest request, UUID userId) {
        try {
            // First try unified task endpoint
            Map<String, Object> payload = Map.of(
                    "prompt", request.getPrompt() != null ? request.getPrompt() : "",
                    "city", request.getCity() != null ? request.getCity() : "Москва",
                    "niche", request.getIndustry() != null ? request.getIndustry() : "Бизнес",
                    "company_name", request.getDescription() != null ? request.getDescription() : "UCust"
            );

            UnifiedTaskRequest unifiedReq = new UnifiedTaskRequest(
                    userId.toString(),
                    taskId.toString(),
                    "generate_post",
                    payload
            );

            UnifiedTaskResponse resp = restClient.post()
                    .uri("/api/v1/ai/task")
                    .body(unifiedReq)
                    .retrieve()
                    .body(UnifiedTaskResponse.class);

            if (resp != null && resp.data() != null) {
                return new SubmitTaskResponse(taskId.toString());
            }

            return restClient.post()
                    .uri("/ai/generate")
                    .body(new SubmitTaskRequest(taskId, request, userId))
                    .retrieve()
                    .body(SubmitTaskResponse.class);
        } catch (Exception e) {
            log.error("Failed to submit task to AI service: {}", e.getMessage());
            throw e;
        }
    }

    public UnifiedTaskResponse executeUnifiedTask(String userId, String sessionId, String taskType, Map<String, Object> payload) {
        try {
            return restClient.post()
                    .uri("/api/v1/ai/task")
                    .body(new UnifiedTaskRequest(userId, sessionId, taskType, payload))
                    .retrieve()
                    .body(UnifiedTaskResponse.class);
        } catch (Exception e) {
            log.error("Failed to execute unified task: {}", e.getMessage());
            throw e;
        }
    }

    public Map<String, Object> getTrends(String niche) {
        try {
            return restClient.get()
                    .uri(uriBuilder -> uriBuilder.path("/api/v1/ai/trends").queryParam("niche", niche).build())
                    .retrieve()
                    .body(Map.class);
        } catch (Exception e) {
            log.error("Failed to fetch trends for niche {}: {}", niche, e.getMessage());
            return Map.of("status", "fallback", "niche", niche, "trends", java.util.List.of());
        }
    }

    public Map<String, Object> getAnalyticsGraphs() {
        try {
            return restClient.get()
                    .uri("/api/v1/ai/analytics/graphs")
                    .retrieve()
                    .body(Map.class);
        } catch (Exception e) {
            log.error("Failed to fetch analytics graphs: {}", e.getMessage());
            return Map.of("status", "fallback");
        }
    }

    public TaskResultResponse checkTask(String externalTaskId) {
        try {
            return restClient.get()
                    .uri("/ai/tasks/{externalTaskId}", externalTaskId)
                    .retrieve()
                    .body(TaskResultResponse.class);
        } catch (Exception e) {
            log.error("Failed to check task {} status: {}", externalTaskId, e.getMessage());
            return new TaskResultResponse("UNKNOWN", null, null);
        }
    }

    public record UnifiedTaskRequest(
            String user_id,
            String session_id,
            String task_type,
            Map<String, Object> payload
    ) {}

    public record UnifiedTaskResponse(
            String status,
            Map<String, Object> data
    ) {}

    public record SubmitTaskRequest(
            UUID taskId,
            UUID projectId,
            UUID userId,
            GenerationMode mode,
            String prompt,
            int count,
            String industry,
            String description,
            String targetAudience,
            String toneOfVoice,
            String city,
            String currentMonth,
            int currentYear
    ) {
        SubmitTaskRequest(UUID taskId, GenerateRequest request, UUID userId) {
            this(
                    taskId,
                    request.getProjectId(),
                    userId,
                    request.getMode(),
                    request.getPrompt(),
                    request.getCount(),
                    request.getIndustry(),
                    request.getDescription(),
                    request.getTargetAudience(),
                    request.getToneOfVoice(),
                    request.getCity(),
                    request.getCurrentMonth(),
                    request.getCurrentYear()
            );
        }
    }

    public record SubmitTaskResponse(String externalTaskId) {}

    public record TaskResultResponse(
            String status,
            String generatedText,
            Map<String, Object> metadata
    ) {}
}
