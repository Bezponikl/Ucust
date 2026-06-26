package com.n4d3sh1k4.business_service.service;

import com.n4d3sh1k4.business_service.domain.model.project.Project;
import com.n4d3sh1k4.business_service.domain.repository.ProjectRepository;
import com.n4d3sh1k4.business_service.dto.ProjectRequest;
import com.n4d3sh1k4.business_service.dto.ProjectResponse;
import com.n4d3sh1k4.business_service.dto.UpdateProjectRequest;
import com.n4d3sh1k4.business_service.mapper.ProjectMapper;
import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import com.n4d3sh1k4.common.exception.UniversalExeption;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class ProjectService {
    private final ProjectRepository repository;
    private final ProjectMapper mapper;
    private final MinioService minioService;

    @Transactional
    public ProjectResponse create(ProjectRequest request, UUID ownerId) {
        Project project = mapper.toEntity(request);
        project.setOwnerId(ownerId);
        return mapper.toResponse(repository.save(project));
    }

    @Transactional()
    public List<ProjectResponse> getAllByOwner(UUID ownerId) {
        return repository.findAllByOwnerId(ownerId).stream()
                .map(mapper::toResponse).toList();
    }

    @Transactional
    public ProjectResponse update(UUID id, UpdateProjectRequest request, UUID ownerId) {
        Project project = repository.findByIdAndOwnerId(id, ownerId)
                .orElseThrow(() -> new ContentNotFoundException("Project not found."));
        mapper.updateEntity(request, project);
        return mapper.toResponse(project);
    }

    @Transactional
    public String uploadLogo(UUID projectId, MultipartFile file, UUID ownerId) {
        Project project = repository.findByIdAndOwnerId(projectId, ownerId)
                .orElseThrow(() -> new ContentNotFoundException("Project not found."));

        validateImage(file);

        String extension = StringUtils.getFilenameExtension(file.getOriginalFilename());
        String newPath = String.format("projects/%s/logo_%s.%s",
                projectId, UUID.randomUUID().toString().substring(0, 8), extension);

        if (project.getLogoUrl() != null) {
            try {
                minioService.deleteFile(project.getLogoUrl());
            } catch (Exception e) {
                log.warn("Не удалось удалить старый логотип: {}", project.getLogoUrl());
            }
        }

        minioService.uploadFile(file, newPath);
        project.setLogoUrl(newPath);

        return newPath;
    }

    @Transactional
    public void delete(UUID id, UUID ownerId) {
        if (!repository.existsByIdAndOwnerId(id, ownerId)) {
            throw new ContentNotFoundException("Project not found.");
        }
        repository.deleteById(id);
    }

    private void validateImage(MultipartFile file) {
        if (file.getSize() > 5 * 1024 * 1024) {
            throw new UniversalExeption("File to large (max 5MB).", "FILE_TOO_LARGE", HttpStatus.CONTENT_TOO_LARGE);
        }
        String contentType = file.getContentType();
        if (contentType == null || !contentType.startsWith("image/")) {
            throw new UniversalExeption("Only images are allowed.", "INVALID_FILE_TYPE", HttpStatus.UNSUPPORTED_MEDIA_TYPE);
        }
    }

//    private ProjectResponse mapToResponse(Project project) {
//        String fullAvatarUrl = null;
//        if (project.getLogoUrl() != null) {
//            fullAvatarUrl = bucketPath + project.getLogoUrl();
//        } else {
//            fullAvatarUrl = bucketPath + "b84e7c4a19b762c769541cd557e97f7f.png";
//        }
//
//        return new ProjectResponse(
//                project.getId(),
//                project.getName(),
//                project.getIndustry(),
//                project.getCity(),
//                project.getDescription(),
//                project.getTargetAudience(),
//                project.getToneOfVoice(),
//                project.getSocialLinks(),
//                project.getBusinessHours(),
//                project.getOwnerId(),
//                fullAvatarUrl
//        );
//    }
}
