package com.n4d3sh1k4.business_service.controller;

import com.n4d3sh1k4.business_service.dto.ProjectRequest;
import com.n4d3sh1k4.business_service.dto.ProjectResponse;
import com.n4d3sh1k4.business_service.dto.UpdateProjectRequest;
import com.n4d3sh1k4.business_service.dto.UserPrincipal;
import com.n4d3sh1k4.business_service.service.ProjectService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/projects")
@RequiredArgsConstructor
public class ProjectController {
    private final ProjectService projectService;

    @PostMapping
    public ProjectResponse create(@RequestBody @Valid ProjectRequest request,
                                  @AuthenticationPrincipal UserPrincipal user) {
        return projectService.create(request, user.id());
    }

    @GetMapping
    public List<ProjectResponse> getMyProjects(@AuthenticationPrincipal UserPrincipal user) {
        return projectService.getAllByOwner(user.id());
    }

    @PatchMapping("/{id}") // Логически более корректно для частичного обновления
    public ProjectResponse update(@PathVariable UUID id,
                                  @RequestBody @Valid UpdateProjectRequest request,
                                  @AuthenticationPrincipal UserPrincipal user) {
        return projectService.update(id, request, user.id());
    }

    @PostMapping(value = "/{id}/logo", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public String uploadLogo(@PathVariable UUID id,
                             @RequestParam("file") MultipartFile file,
                             @AuthenticationPrincipal UserPrincipal user) {
        return projectService.uploadLogo(id, file, user.id());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id,
                                       @AuthenticationPrincipal UserPrincipal user) {
        projectService.delete(id, user.id());
        return ResponseEntity.ok().build();
    }
}
