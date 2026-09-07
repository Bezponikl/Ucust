package com.n4d3sh1k4.business_service.service;

import com.n4d3sh1k4.common.dto.ProjectCreatedEvent;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;
import org.springframework.amqp.rabbit.core.RabbitTemplate;

import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThatCode;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class ProjectEventPublisherTest {

    private static final UUID PROJECT_ID = UUID.fromString("11111111-1111-1111-1111-111111111111");
    private static final UUID USER_ID = UUID.fromString("22222222-2222-2222-2222-222222222222");

    @Mock
    private RabbitTemplate rabbitTemplate;

    @InjectMocks
    private ProjectEventPublisher projectEventPublisher;

    private ProjectCreatedEvent event() {
        return new ProjectCreatedEvent(
                PROJECT_ID, USER_ID, "CAFE_RESTAURANT", "Описание",
                "Аудитория", "FRIENDLY", "Москва", 5);
    }

    @Test
    void projectCreated_publishesEvent() {
        ProjectCreatedEvent event = event();

        projectEventPublisher.projectCreated(event);

        verify(rabbitTemplate).convertAndSend("user-exchange", "project.created", event);
    }

    @Test
    void projectCreated_whenRabbitFails_swallowsException() {
        doThrow(new RuntimeException("connection refused"))
                .when(rabbitTemplate).convertAndSend(anyString(), anyString(), any(Object.class));

        assertThatCode(() -> projectEventPublisher.projectCreated(event()))
                .doesNotThrowAnyException();
    }
}