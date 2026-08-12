package com.n4d3sh1k4.generative_orchestration_service.controller;

import com.n4d3sh1k4.generative_orchestration_service.dto.AsyncGenerateResponse;
import com.n4d3sh1k4.generative_orchestration_service.dto.TaskStatusResponse;
import com.n4d3sh1k4.generative_orchestration_service.dto.request_dto.GenerateRequest;
import com.n4d3sh1k4.generative_orchestration_service.service.AsyncGenerationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@Tag(name = "Асинхронная генерация контента")
@RestController
@RequestMapping("/orchestration")
@RequiredArgsConstructor
public class AsyncGenerationController {

    private final AsyncGenerationService asyncGenerationService;

    @Operation(summary = "Отправить задачу на генерацию в AI-сервис")
    @PostMapping("/generate/async")
    public ResponseEntity<AsyncGenerateResponse> submitAsync(
            @Valid @RequestBody GenerateRequest request,
            Authentication authentication) {
        UUID userId = UUID.fromString(authentication.getName());
        return ResponseEntity.status(HttpStatus.ACCEPTED)
                .body(asyncGenerationService.submitAsync(request, userId));
    }

    @Operation(summary = "Проверить статус выполнения задачи")
    @GetMapping("/tasks/{taskId}")
    public ResponseEntity<TaskStatusResponse> checkTask(@PathVariable UUID taskId) {
        return ResponseEntity.ok(asyncGenerationService.checkTask(taskId));
    }
}
