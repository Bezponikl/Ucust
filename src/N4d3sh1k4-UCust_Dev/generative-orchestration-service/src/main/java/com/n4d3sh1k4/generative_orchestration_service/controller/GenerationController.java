package com.n4d3sh1k4.generative_orchestration_service.controller;

import com.n4d3sh1k4.generative_orchestration_service.dto.PostResponse;
import com.n4d3sh1k4.generative_orchestration_service.service.GenerationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@Tag(name = "Генерация контента")
@RestController
@RequestMapping("/orchestration")
@RequiredArgsConstructor
public class GenerationController {

    private final GenerationService generationService;

    @Operation(summary = "Подтвердить пост")
    @PostMapping("/posts/{id}/confirm")
    public ResponseEntity<PostResponse> confirmPost(@PathVariable UUID id) {
        return ResponseEntity.ok(generationService.confirmPost(id));
    }

    @Operation(summary = "Опубликовать пост")
    @PostMapping("/posts/{id}/publish")
    public ResponseEntity<PostResponse> publishPost(@PathVariable UUID id) {
        return ResponseEntity.ok(generationService.publishPost(id));
    }

    @Operation(summary = "Получить пост по ID")
    @GetMapping("/posts/{id}")
    public ResponseEntity<PostResponse> getPost(@PathVariable UUID id) {
        return ResponseEntity.ok(generationService.getPostById(id));
    }

    @Operation(summary = "Посты проекта")
    @GetMapping("/projects/{projectId}/posts")
    public ResponseEntity<List<PostResponse>> getPosts(@PathVariable UUID projectId) {
        return ResponseEntity.ok(generationService.getPostsByProject(projectId));
    }
}