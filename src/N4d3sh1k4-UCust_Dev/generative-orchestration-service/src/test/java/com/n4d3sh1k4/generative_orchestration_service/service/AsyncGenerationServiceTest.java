package com.n4d3sh1k4.generative_orchestration_service.service;

import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import com.n4d3sh1k4.common.exception.UniversalExeption;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.GenerationMode;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.GenerationTask;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.Post;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.TaskStatus;
import com.n4d3sh1k4.generative_orchestration_service.domain.repository.GenerationTaskRepository;
import com.n4d3sh1k4.generative_orchestration_service.domain.repository.PostRepository;
import com.n4d3sh1k4.generative_orchestration_service.dto.AsyncGenerateResponse;
import com.n4d3sh1k4.generative_orchestration_service.dto.TaskStatusResponse;
import com.n4d3sh1k4.generative_orchestration_service.dto.request_dto.GenerateRequest;
import com.n4d3sh1k4.generative_orchestration_service.service.AIServiceClient.SubmitTaskResponse;
import com.n4d3sh1k4.generative_orchestration_service.service.AIServiceClient.TaskResultResponse;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class AsyncGenerationServiceTest {

    private static final UUID TASK_ID = UUID.fromString("44444444-4444-4444-4444-444444444444");
    private static final UUID PROJECT_ID = UUID.fromString("22222222-2222-2222-2222-222222222222");
    private static final UUID USER_ID = UUID.fromString("33333333-3333-3333-3333-333333333333");
    private static final UUID POST_ID = UUID.fromString("11111111-1111-1111-1111-111111111111");
    private static final Instant CREATED_AT = Instant.parse("2026-01-01T09:00:00Z");

    @Mock
    private GenerationTaskRepository taskRepository;

    @Mock
    private PostRepository postRepository;

    @Mock
    private AIServiceClient aiServiceClient;

    @InjectMocks
    private AsyncGenerationService asyncGenerationService;

    private GenerateRequest request() {
        GenerateRequest request = new GenerateRequest();
        request.setProjectId(PROJECT_ID);
        request.setCount(2);
        request.setMode(GenerationMode.AUTO);
        request.setIndustry("CAFE");
        request.setDescription("Кофейня");
        request.setToneOfVoice("FRIENDLY");
        return request;
    }

    private GenerationTask task(TaskStatus status, String externalTaskId) {
        return GenerationTask.builder()
                .id(TASK_ID)
                .projectId(PROJECT_ID)
                .userId(USER_ID)
                .count(2)
                .status(status)
                .externalTaskId(externalTaskId)
                .createdAt(CREATED_AT)
                .build();
    }

    @Test
    void submitAsync_whenAiSucceeds_marksTaskProcessing() {
        List<TaskStatus> savedStatuses = new ArrayList<>();
        when(aiServiceClient.submitTask(any(), any(GenerateRequest.class), eq(USER_ID)))
                .thenReturn(new SubmitTaskResponse("ext-1"));
        when(taskRepository.save(any(GenerationTask.class))).thenAnswer(inv -> {
            GenerationTask t = inv.getArgument(0);
            savedStatuses.add(t.getStatus());
            if (t.getId() == null) {
                t.setId(TASK_ID);
            }
            return t;
        });

        AsyncGenerateResponse response = asyncGenerationService.submitAsync(request(), USER_ID);

        assertThat(response.taskId()).isEqualTo(TASK_ID);
        assertThat(response.status()).isEqualTo(TaskStatus.PROCESSING);

        ArgumentCaptor<GenerationTask> captor = ArgumentCaptor.forClass(GenerationTask.class);
        verify(taskRepository, times(2)).save(captor.capture());
        GenerationTask lastSaved = captor.getAllValues().get(1);
        assertThat(savedStatuses).containsExactly(TaskStatus.PENDING, TaskStatus.PROCESSING);
        assertThat(lastSaved.getStatus()).isEqualTo(TaskStatus.PROCESSING);
        assertThat(lastSaved.getExternalTaskId()).isEqualTo("ext-1");
        assertThat(lastSaved.getUpdatedAt()).isNotNull();
    }

    @Test
    void submitAsync_whenAiThrows_marksTaskFailed() {
        when(aiServiceClient.submitTask(any(), any(GenerateRequest.class), eq(USER_ID)))
                .thenThrow(new RuntimeException("connection refused"));

        AsyncGenerateResponse response = asyncGenerationService.submitAsync(request(), USER_ID);

        assertThat(response.status()).isEqualTo(TaskStatus.FAILED);

        ArgumentCaptor<GenerationTask> captor = ArgumentCaptor.forClass(GenerationTask.class);
        verify(taskRepository, times(2)).save(captor.capture());
        GenerationTask failed = captor.getAllValues().get(1);
        assertThat(failed.getStatus()).isEqualTo(TaskStatus.FAILED);
        assertThat(failed.getErrorMessage()).contains("connection refused");
    }

    @Test
    void checkTask_whenNotFound_throwsContentNotFound() {
        when(taskRepository.findById(TASK_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> asyncGenerationService.checkTask(TASK_ID))
                .isInstanceOf(ContentNotFoundException.class);
    }

    @Test
    void checkTask_whenCompleted_createsPostsAndMarksCompleted() {
        GenerationTask task = task(TaskStatus.PROCESSING, "ext-1");
        when(taskRepository.findById(TASK_ID)).thenReturn(Optional.of(task));
        when(aiServiceClient.checkTask("ext-1"))
                .thenReturn(new TaskResultResponse("COMPLETED", "Сгенерированный текст", null));
        when(postRepository.save(any(Post.class))).thenAnswer(inv -> {
            Post post = inv.getArgument(0);
            post.setId(POST_ID);
            return post;
        });

        TaskStatusResponse response = asyncGenerationService.checkTask(TASK_ID);

        assertThat(response.status()).isEqualTo(TaskStatus.COMPLETED);
        assertThat(response.externalTaskId()).isEqualTo("ext-1");
        assertThat(response.resultPostId()).isEqualTo(POST_ID);
        assertThat(task.getStatus()).isEqualTo(TaskStatus.COMPLETED);
        verify(postRepository, times(2)).save(any(Post.class));
    }

    @Test
    void checkTask_whenFailed_setsErrorFromMetadata() {
        GenerationTask task = task(TaskStatus.PROCESSING, "ext-1");
        when(taskRepository.findById(TASK_ID)).thenReturn(Optional.of(task));
        when(aiServiceClient.checkTask("ext-1"))
                .thenReturn(new TaskResultResponse("FAILED", null, Map.of("error", "quota exceeded")));

        TaskStatusResponse response = asyncGenerationService.checkTask(TASK_ID);

        assertThat(response.status()).isEqualTo(TaskStatus.FAILED);
        assertThat(response.errorMessage()).isEqualTo("quota exceeded");
        assertThat(task.getStatus()).isEqualTo(TaskStatus.FAILED);
        verify(postRepository, never()).save(any(Post.class));
    }

    @Test
    void checkTask_whenFailed_withoutMetadata_setsDefaultError() {
        GenerationTask task = task(TaskStatus.PROCESSING, "ext-1");
        when(taskRepository.findById(TASK_ID)).thenReturn(Optional.of(task));
        when(aiServiceClient.checkTask("ext-1"))
                .thenReturn(new TaskResultResponse("FAILED", null, null));

        TaskStatusResponse response = asyncGenerationService.checkTask(TASK_ID);

        assertThat(response.status()).isEqualTo(TaskStatus.FAILED);
        assertThat(response.errorMessage()).isEqualTo("AI service reported failure");
        assertThat(task.getStatus()).isEqualTo(TaskStatus.FAILED);
        verify(postRepository, never()).save(any(Post.class));
    }

    @Test
    void checkTask_whenNotProcessing_skipsAiCall() {
        GenerationTask task = task(TaskStatus.PENDING, null);
        when(taskRepository.findById(TASK_ID)).thenReturn(Optional.of(task));

        TaskStatusResponse response = asyncGenerationService.checkTask(TASK_ID);

        assertThat(response.status()).isEqualTo(TaskStatus.PENDING);
        assertThat(response.externalTaskId()).isNull();
        verify(aiServiceClient, never()).checkTask(any());
        verify(postRepository, never()).save(any(Post.class));
    }

    @Test
    void submitAsync_MANUAL_withPrompt_succeeds() {
        GenerateRequest req = new GenerateRequest();
        req.setProjectId(PROJECT_ID);
        req.setMode(GenerationMode.MANUAL);
        req.setPrompt("Тема для поста");
        when(aiServiceClient.submitTask(any(), any(), eq(USER_ID)))
                .thenReturn(new SubmitTaskResponse("ext-1"));
        when(taskRepository.save(any(GenerationTask.class))).thenAnswer(inv -> {
            GenerationTask t = inv.getArgument(0);
            if (t.getId() == null) t.setId(TASK_ID);
            return t;
        });

        AsyncGenerateResponse response = asyncGenerationService.submitAsync(req, USER_ID);

        assertThat(response.status()).isEqualTo(TaskStatus.PROCESSING);
    }

    @Test
    void submitAsync_MANUAL_withoutPrompt_throwsValidation() {
        GenerateRequest req = new GenerateRequest();
        req.setProjectId(PROJECT_ID);
        req.setMode(GenerationMode.MANUAL);

        assertThatThrownBy(() -> asyncGenerationService.submitAsync(req, USER_ID))
                .isInstanceOf(UniversalExeption.class)
                .satisfies(e -> {
                    assertThat(((UniversalExeption) e).getCode()).isEqualTo("VALIDATION_ERROR");
                    assertThat(((UniversalExeption) e).getStatus()).isEqualTo(
                            org.springframework.http.HttpStatus.BAD_REQUEST);
                });
    }

    @Test
    void submitAsync_AUTO_missingFields_throwsValidation() {
        GenerateRequest req = new GenerateRequest();
        req.setProjectId(PROJECT_ID);
        req.setMode(GenerationMode.AUTO);

        assertThatThrownBy(() -> asyncGenerationService.submitAsync(req, USER_ID))
                .isInstanceOf(UniversalExeption.class)
                .satisfies(e -> {
                    assertThat(((UniversalExeption) e).getCode()).isEqualTo("VALIDATION_ERROR");
                    assertThat(((UniversalExeption) e).getMessage()).contains("industry", "description", "toneOfVoice");
                });
    }
}