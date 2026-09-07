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
