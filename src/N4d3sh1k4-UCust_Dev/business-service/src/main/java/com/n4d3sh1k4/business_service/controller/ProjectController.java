package com.n4d3sh1k4.business_service.controller;

import com.n4d3sh1k4.business_service.dto.ProjectRequest;
import com.n4d3sh1k4.business_service.dto.ProjectResponse;
import com.n4d3sh1k4.business_service.dto.UpdateProjectRequest;
import com.n4d3sh1k4.business_service.dto.UserPrincipal;
import com.n4d3sh1k4.business_service.service.ProjectService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.UUID;

@Tag(name = "Проекты", description = "Управление проектами пользователя")
@RestController
@RequestMapping("/projects")
@RequiredArgsConstructor
public class ProjectController {
    private final ProjectService projectService;

    @Operation(summary = "Создать проект",
               description = "Создаёт новый проект для текущего пользователя.")
    @PostMapping
    public ProjectResponse create(@RequestBody @Valid ProjectRequest request,
                                  @AuthenticationPrincipal UserPrincipal user) {
        return projectService.create(request, user.id());
    }

    @Operation(summary = "Получить проект по ID")
    @GetMapping("/{id}")
    public ProjectResponse getById(@PathVariable UUID id, @AuthenticationPrincipal UserPrincipal user) {
        return projectService.getById(id, user.id());
    }

    @Operation(summary = "Получить свои проекты",
               description = "Возвращает список всех проектов текущего пользователя.")
    @GetMapping
    public List<ProjectResponse> getMyProjects(@AuthenticationPrincipal UserPrincipal user) {
        return projectService.getAllByOwner(user.id());
    }

    @Operation(summary = "Обновить проект",
               description = "Частично обновляет данные проекта по его идентификатору.")
    @PatchMapping("/{id}")
    public ProjectResponse update(
            @Parameter(description = "Идентификатор проекта")
            @PathVariable UUID id,
            @RequestBody @Valid UpdateProjectRequest request,
            @AuthenticationPrincipal UserPrincipal user) {
        return projectService.update(id, request, user.id());
    }

    @Operation(summary = "Загрузить логотип",
               description = "Загружает изображение логотипа для проекта. Принимает multipart/form-data.")
    @PostMapping(value = "/{id}/logo", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public String uploadLogo(
            @Parameter(description = "Идентификатор проекта")
            @PathVariable UUID id,
            @Parameter(description = "Файл изображения (JPEG, PNG)")
            @RequestParam("file") MultipartFile file,
            @AuthenticationPrincipal UserPrincipal user) {
        return projectService.uploadLogo(id, file, user.id());
    }

    @Operation(summary = "Удалить проект",
               description = "Удаляет проект и связанные с ним ресурсы.")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(
            @Parameter(description = "Идентификатор проекта")
            @PathVariable UUID id,
            @AuthenticationPrincipal UserPrincipal user) {
        projectService.delete(id, user.id());
        return ResponseEntity.ok().build();
    }
}
