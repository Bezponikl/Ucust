package com.n4d3sh1k4.business_service.service;

import com.n4d3sh1k4.business_service.domain.model.project.Project;
import com.n4d3sh1k4.business_service.domain.model.project.support.Industry;
import com.n4d3sh1k4.business_service.domain.model.project.support.ToneOfVoice;
import com.n4d3sh1k4.business_service.domain.repository.ProjectRepository;
import com.n4d3sh1k4.business_service.dto.ProjectRequest;
import com.n4d3sh1k4.business_service.dto.ProjectResponse;
import com.n4d3sh1k4.business_service.dto.UpdateProjectRequest;
import com.n4d3sh1k4.business_service.mapper.ProjectMapper;
import com.n4d3sh1k4.common.dto.ProjectCreatedEvent;
import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import com.n4d3sh1k4.common.exception.UniversalExeption;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;
import org.springframework.http.HttpStatus;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class ProjectServiceTest {

    private static final UUID PROJECT_ID = UUID.fromString("11111111-1111-1111-1111-111111111111");
    private static final UUID OWNER_ID = UUID.fromString("22222222-2222-2222-2222-222222222222");

    @Mock
    private ProjectRepository repository;

    @Mock
    private ProjectMapper mapper;

    @Mock
    private MinioService minioService;

    @Mock
    private ProjectEventPublisher eventPublisher;

    @InjectMocks
    private ProjectService projectService;

    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(projectService, "defaultPostCount", 5);
    }

    private Project project() {
        Project project = new Project();
        project.setId(PROJECT_ID);
        project.setName("Мой бизнес");
        project.setIndustry(Industry.CAFE_RESTAURANT);
        project.setCity("Москва");
        project.setDescription("Описание деятельности");
        project.setTargetAudience("Молодые специалисты");
        project.setToneOfVoice(ToneOfVoice.FRIENDLY);
        project.setOwnerId(OWNER_ID);
        return project;
    }

    private ProjectResponse response() {
        return new ProjectResponse(
                PROJECT_ID, "Мой бизнес", Industry.CAFE_RESTAURANT, "Москва",
                "Описание деятельности", "Молодые специалисты", ToneOfVoice.FRIENDLY,
                null, null, OWNER_ID, "http://localhost:9020/business-service/logo.png");
    }

    private ProjectRequest request() {
        return new ProjectRequest(
                "Мой бизнес", Industry.CAFE_RESTAURANT, "Москва",
                "Описание деятельности", "Молодые специалисты", ToneOfVoice.FRIENDLY,
                null, null);
    }

    @Test
    void create_persistsProjectAndPublishesEvent() {
        Project project = project();
        when(mapper.toEntity(any(ProjectRequest.class))).thenReturn(project);
        when(repository.save(project)).thenReturn(project);
        when(mapper.toResponse(project)).thenReturn(response());

        ProjectResponse result = projectService.create(request(), OWNER_ID);

        assertThat(result.id()).isEqualTo(PROJECT_ID);
        assertThat(project.getOwnerId()).isEqualTo(OWNER_ID);
        verify(repository).save(project);

        ArgumentCaptor<ProjectCreatedEvent> eventCaptor = ArgumentCaptor.forClass(ProjectCreatedEvent.class);
        verify(eventPublisher).projectCreated(eventCaptor.capture());
        ProjectCreatedEvent event = eventCaptor.getValue();
        assertThat(event.projectId()).isEqualTo(PROJECT_ID);
        assertThat(event.userId()).isEqualTo(OWNER_ID);
        assertThat(event.industry()).isEqualTo("CAFE_RESTAURANT");
        assertThat(event.description()).isEqualTo("Описание деятельности");
        assertThat(event.targetAudience()).isEqualTo("Молодые специалисты");
        assertThat(event.toneOfVoice()).isEqualTo("FRIENDLY");
        assertThat(event.city()).isEqualTo("Москва");
        assertThat(event.postCount()).isEqualTo(5);
    }

    @Test
    void getById_whenFound_returnsResponse() {
        Project project = project();
        when(repository.findByIdAndOwnerId(PROJECT_ID, OWNER_ID)).thenReturn(Optional.of(project));
        when(mapper.toResponse(project)).thenReturn(response());

        ProjectResponse result = projectService.getById(PROJECT_ID, OWNER_ID);

        assertThat(result.id()).isEqualTo(PROJECT_ID);
        assertThat(result.ownerId()).isEqualTo(OWNER_ID);
    }

    @Test
    void getById_whenNotFound_throwsContentNotFound() {
        when(repository.findByIdAndOwnerId(PROJECT_ID, OWNER_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> projectService.getById(PROJECT_ID, OWNER_ID))
                .isInstanceOf(ContentNotFoundException.class);
    }

    @Test
    void getAllByOwner_returnsList() {
        Project project = project();
        when(repository.findAllByOwnerId(OWNER_ID)).thenReturn(List.of(project));
        when(mapper.toResponse(project)).thenReturn(response());

        List<ProjectResponse> result = projectService.getAllByOwner(OWNER_ID);

        assertThat(result).hasSize(1);
        assertThat(result.get(0).id()).isEqualTo(PROJECT_ID);
    }

    @Test
    void update_updatesEntityAndReturnsResponse() {
        Project project = project();
        UpdateProjectRequest updateRequest = new UpdateProjectRequest(
                "Новое имя", null, null, null, null, null, null, null);
        when(repository.findByIdAndOwnerId(PROJECT_ID, OWNER_ID)).thenReturn(Optional.of(project));
        when(mapper.toResponse(project)).thenReturn(response());

        ProjectResponse result = projectService.update(PROJECT_ID, updateRequest, OWNER_ID);

        assertThat(result.id()).isEqualTo(PROJECT_ID);
        verify(mapper).updateEntity(updateRequest, project);
    }

    @Test
    void update_whenNotFound_throwsContentNotFound() {
        when(repository.findByIdAndOwnerId(PROJECT_ID, OWNER_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> projectService.update(
                PROJECT_ID, new UpdateProjectRequest(null, null, null, null, null, null, null, null), OWNER_ID))
                .isInstanceOf(ContentNotFoundException.class);
    }

    @Test
    void uploadLogo_uploadsAndReturnsPath() {
        Project project = project();
        MockMultipartFile file = new MockMultipartFile("file", "logo.png", "image/png", new byte[]{1, 2, 3});
        when(repository.findByIdAndOwnerId(PROJECT_ID, OWNER_ID)).thenReturn(Optional.of(project));
        when(minioService.uploadFile(eq(file), anyString())).thenAnswer(inv -> inv.getArgument(1));

        String path = projectService.uploadLogo(PROJECT_ID, file, OWNER_ID);

        assertThat(path).startsWith("projects/" + PROJECT_ID + "/logo_");
        assertThat(path).endsWith(".png");
        assertThat(project.getLogoUrl()).isEqualTo(path);
        verify(minioService, never()).deleteFile(anyString());
    }

    @Test
    void uploadLogo_whenExistingLogo_deletesOldOne() {
        Project project = project();
        project.setLogoUrl("projects/old/logo_old.png");
        MockMultipartFile file = new MockMultipartFile("file", "logo.png", "image/png", new byte[]{1, 2, 3});
        when(repository.findByIdAndOwnerId(PROJECT_ID, OWNER_ID)).thenReturn(Optional.of(project));
        when(minioService.uploadFile(eq(file), anyString())).thenAnswer(inv -> inv.getArgument(1));

        String path = projectService.uploadLogo(PROJECT_ID, file, OWNER_ID);

        verify(minioService).deleteFile("projects/old/logo_old.png");
        assertThat(project.getLogoUrl()).isEqualTo(path);
    }

    @Test
    void uploadLogo_whenFileTooLarge_throwsFileTooLarge() {
        Project project = project();
        MockMultipartFile file = new MockMultipartFile(
                "file", "big.png", "image/png", new byte[5 * 1024 * 1024 + 1]);
        when(repository.findByIdAndOwnerId(PROJECT_ID, OWNER_ID)).thenReturn(Optional.of(project));

        assertThatThrownBy(() -> projectService.uploadLogo(PROJECT_ID, file, OWNER_ID))
                .isInstanceOf(UniversalExeption.class)
                .satisfies(e -> {
                    assertThat(((UniversalExeption) e).getCode()).isEqualTo("FILE_TOO_LARGE");
                    assertThat(((UniversalExeption) e).getStatus()).isEqualTo(HttpStatus.CONTENT_TOO_LARGE);
                });

        verify(minioService, never()).uploadFile(any(), anyString());
    }

    @Test
    void uploadLogo_whenNotImage_throwsInvalidFileType() {
        Project project = project();
        MockMultipartFile file = new MockMultipartFile("file", "note.txt", "text/plain", new byte[]{1});
        when(repository.findByIdAndOwnerId(PROJECT_ID, OWNER_ID)).thenReturn(Optional.of(project));

        assertThatThrownBy(() -> projectService.uploadLogo(PROJECT_ID, file, OWNER_ID))
                .isInstanceOf(UniversalExeption.class)
                .satisfies(e -> {
                    assertThat(((UniversalExeption) e).getCode()).isEqualTo("INVALID_FILE_TYPE");
                    assertThat(((UniversalExeption) e).getStatus()).isEqualTo(HttpStatus.UNSUPPORTED_MEDIA_TYPE);
                });

        verify(minioService, never()).uploadFile(any(), anyString());
    }

    @Test
    void uploadLogo_whenOctetStreamButRealImage_passesValidation() {
        Project project = project();
        byte[] png = {(byte) 0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 1, 2, 3, 4};
        MockMultipartFile file = new MockMultipartFile("file", "logo.png", "application/octet-stream", png);
        when(repository.findByIdAndOwnerId(PROJECT_ID, OWNER_ID)).thenReturn(Optional.of(project));
        when(minioService.uploadFile(eq(file), anyString())).thenAnswer(inv -> inv.getArgument(1));

        String path = projectService.uploadLogo(PROJECT_ID, file, OWNER_ID);

        assertThat(path).startsWith("projects/" + PROJECT_ID + "/logo_");
    }

    @Test
    void uploadLogo_whenProjectNotFound_throwsContentNotFound() {
        MockMultipartFile file = new MockMultipartFile("file", "logo.png", "image/png", new byte[]{1});
        when(repository.findByIdAndOwnerId(PROJECT_ID, OWNER_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> projectService.uploadLogo(PROJECT_ID, file, OWNER_ID))
                .isInstanceOf(ContentNotFoundException.class);
    }

    @Test
    void delete_whenExists_deletesById() {
        when(repository.existsByIdAndOwnerId(PROJECT_ID, OWNER_ID)).thenReturn(true);

        projectService.delete(PROJECT_ID, OWNER_ID);

        verify(repository).deleteById(PROJECT_ID);
    }

    @Test
    void delete_whenNotFound_throwsContentNotFound() {
        when(repository.existsByIdAndOwnerId(PROJECT_ID, OWNER_ID)).thenReturn(false);

        assertThatThrownBy(() -> projectService.delete(PROJECT_ID, OWNER_ID))
                .isInstanceOf(ContentNotFoundException.class);

        verify(repository, never()).deleteById(PROJECT_ID);
    }
}