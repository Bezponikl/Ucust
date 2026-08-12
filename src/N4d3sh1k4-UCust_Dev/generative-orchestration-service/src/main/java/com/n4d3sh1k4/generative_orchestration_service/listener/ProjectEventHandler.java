package com.n4d3sh1k4.generative_orchestration_service.listener;

import com.n4d3sh1k4.common.dto.ProjectCreatedEvent;
import com.n4d3sh1k4.generative_orchestration_service.config.RabbitProjectConfig;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.GenerationMode;
import com.n4d3sh1k4.generative_orchestration_service.dto.request_dto.GenerateRequest;
import com.n4d3sh1k4.generative_orchestration_service.service.AsyncGenerationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitHandler;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
@RabbitListener(queues = RabbitProjectConfig.PROJECT_QUEUE)
public class ProjectEventHandler {

    private final AsyncGenerationService asyncGenerationService;

    @RabbitHandler
    public void handleProjectCreated(ProjectCreatedEvent event) {
        log.info("Received project.created event for project {}", event.projectId());

        GenerateRequest request = new GenerateRequest();
        request.setProjectId(event.projectId());
        request.setCount(event.postCount() > 0 ? event.postCount() : 5);
        request.setMode(GenerationMode.AUTO);
        request.setIndustry(event.industry());
        request.setDescription(event.description());
        request.setTargetAudience(event.targetAudience());
        request.setToneOfVoice(event.toneOfVoice());
        request.setCity(event.city());

        asyncGenerationService.submitAsync(request, event.userId());
    }
}
