package com.n4d3sh1k4.generative_orchestration_service.listener;

import com.n4d3sh1k4.common.dto.ProjectCreatedEvent;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.GenerationMode;
import com.n4d3sh1k4.generative_orchestration_service.dto.request_dto.GenerateRequest;
import com.n4d3sh1k4.generative_orchestration_service.service.AsyncGenerationService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;

import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class ProjectEventHandlerTest {

    private static final UUID PROJECT_ID = UUID.fromString("22222222-2222-2222-2222-222222222222");
    private static final UUID USER_ID = UUID.fromString("33333333-3333-3333-3333-333333333333");

    @Mock
    private AsyncGenerationService asyncGenerationService;

    @InjectMocks
    private ProjectEventHandler projectEventHandler;

    private ProjectCreatedEvent event(int postCount) {
        return new ProjectCreatedEvent(
                PROJECT_ID, USER_ID, "IT", "Описание бизнеса",
                "Бизнес-аудитория", "Дружелюбный", "Москва", postCount);
    }

    @Test
    void handleProjectCreated_buildsRequestAndSubmits() {
        projectEventHandler.handleProjectCreated(event(5));

        ArgumentCaptor<GenerateRequest> captor = ArgumentCaptor.forClass(GenerateRequest.class);
        verify(asyncGenerationService).submitAsync(captor.capture(), eq(USER_ID));

        GenerateRequest request = captor.getValue();
        assertThat(request.getProjectId()).isEqualTo(PROJECT_ID);
        assertThat(request.getCount()).isEqualTo(5);
        assertThat(request.getMode()).isEqualTo(GenerationMode.AUTO);
        assertThat(request.getIndustry()).isEqualTo("IT");
        assertThat(request.getDescription()).isEqualTo("Описание бизнеса");
        assertThat(request.getTargetAudience()).isEqualTo("Бизнес-аудитория");
        assertThat(request.getToneOfVoice()).isEqualTo("Дружелюбный");
        assertThat(request.getCity()).isEqualTo("Москва");
    }

    @Test
    void handleProjectCreated_whenPostCountZero_usesDefaultFive() {
        projectEventHandler.handleProjectCreated(event(0));

        ArgumentCaptor<GenerateRequest> captor = ArgumentCaptor.forClass(GenerateRequest.class);
        verify(asyncGenerationService).submitAsync(captor.capture(), eq(USER_ID));
        assertThat(captor.getValue().getCount()).isEqualTo(5);
    }

    @Test
    void handleProjectCreated_whenPostCountNegative_usesDefaultFive() {
        projectEventHandler.handleProjectCreated(event(-3));

        ArgumentCaptor<GenerateRequest> captor = ArgumentCaptor.forClass(GenerateRequest.class);
        verify(asyncGenerationService).submitAsync(captor.capture(), eq(USER_ID));
        assertThat(captor.getValue().getCount()).isEqualTo(5);
    }
}