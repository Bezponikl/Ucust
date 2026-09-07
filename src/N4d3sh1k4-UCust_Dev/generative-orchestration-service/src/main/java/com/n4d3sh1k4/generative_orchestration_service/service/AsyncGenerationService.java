package com.n4d3sh1k4.generative_orchestration_service.service;

import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import com.n4d3sh1k4.common.exception.UniversalExeption;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.*;
import com.n4d3sh1k4.generative_orchestration_service.domain.repository.GenerationTaskRepository;
import com.n4d3sh1k4.generative_orchestration_service.domain.repository.PostRepository;
import com.n4d3sh1k4.generative_orchestration_service.dto.AsyncGenerateResponse;
import com.n4d3sh1k4.generative_orchestration_service.dto.TaskStatusResponse;
import com.n4d3sh1k4.generative_orchestration_service.dto.request_dto.GenerateRequest;
import com.n4d3sh1k4.generative_orchestration_service.service.AIServiceClient.SubmitTaskResponse;
import com.n4d3sh1k4.generative_orchestration_service.service.AIServiceClient.TaskResultResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.Set;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class AsyncGenerationService {

    private final GenerationTaskRepository taskRepository;
    private final PostRepository postRepository;
    private final AIServiceClient aiServiceClient;

    @Transactional
    public AsyncGenerateResponse submitAsync(GenerateRequest request, UUID userId) {
        validateRequest(request);

        GenerationTask task = GenerationTask.builder()
                .projectId(request.getProjectId())
                .userId(userId)
                .prompt(request.getPrompt())
                .generationMode(request.getMode())
                .count(request.getCount())
                .status(TaskStatus.PENDING)
                .createdAt(Instant.now())
                .build();
        taskRepository.save(task);

        try {
            SubmitTaskResponse aiResponse = aiServiceClient.submitTask(
                    task.getId(),
                    request,
                    userId
            );
            task.setExternalTaskId(aiResponse.externalTaskId());
            task.setStatus(TaskStatus.PROCESSING);
            task.setUpdatedAt(Instant.now());
            taskRepository.save(task);
        } catch (Exception e) {
            task.setStatus(TaskStatus.FAILED);
            task.setErrorMessage("Failed to submit to AI service: " + e.getMessage());
            task.setUpdatedAt(Instant.now());
            taskRepository.save(task);
        }

        return new AsyncGenerateResponse(task.getId(), task.getStatus());
    }

    @Transactional
    public TaskStatusResponse checkTask(UUID taskId) {
        GenerationTask task = taskRepository.findById(taskId)
                .orElseThrow(() -> new ContentNotFoundException("Task not found"));

        if (task.getExternalTaskId() != null && task.getStatus() == TaskStatus.PROCESSING) {
            TaskResultResponse result = aiServiceClient.checkTask(task.getExternalTaskId());
            switch (result.status()) {
                case "COMPLETED" -> {
                    for (int i = 0; i < task.getCount(); i++) {
                        Post post = Post.builder()
                                .projectId(task.getProjectId())
                                .userId(task.getUserId())
                                .text(result.generatedText())
                                .status(PostStatus.DRAFT)
                                .generationMode(task.getGenerationMode())
                                .createdAt(Instant.now())
                                .build();
                        postRepository.save(post);
                        task.setResultPostId(post.getId());
                    }
                    task.setStatus(TaskStatus.COMPLETED);
                    task.setUpdatedAt(Instant.now());
                    taskRepository.save(task);
                }
                case "FAILED" -> {
                    task.setStatus(TaskStatus.FAILED);
                    task.setErrorMessage(result.metadata() != null
                            ? String.valueOf(result.metadata().get("error"))
                            : "AI service reported failure");
                    task.setUpdatedAt(Instant.now());
                    taskRepository.save(task);
                }
            }
        }

        return new TaskStatusResponse(
                task.getId(),
                task.getExternalTaskId(),
                task.getStatus(),
                task.getResultPostId(),
                task.getErrorMessage(),
                task.getCreatedAt(),
                task.getUpdatedAt()
        );
    }

    private void validateRequest(GenerateRequest request) {
        switch (request.getMode()) {
            case MANUAL -> {
                if (request.getPrompt() == null || request.getPrompt().isBlank()) {
                    throw new UniversalExeption(
                            "prompt is required in MANUAL mode",
                            "VALIDATION_ERROR",
                            HttpStatus.BAD_REQUEST);
                }
            }
            case AUTO -> {
                var missing = new java.util.ArrayList<String>();
                if (request.getIndustry() == null || request.getIndustry().isBlank()) missing.add("industry");
                if (request.getDescription() == null || request.getDescription().isBlank()) missing.add("description");
                if (request.getToneOfVoice() == null || request.getToneOfVoice().isBlank()) missing.add("toneOfVoice");
                if (!missing.isEmpty()) {
                    throw new UniversalExeption(
                            "Missing required fields for AUTO mode: " + String.join(", ", missing),
                            "VALIDATION_ERROR",
                            HttpStatus.BAD_REQUEST);
                }
            }
        }
    }
}
