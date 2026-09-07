package com.n4d3sh1k4.business_service.service;

import com.n4d3sh1k4.common.dto.ProjectCreatedEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
public class ProjectEventPublisher {

    private static final String EXCHANGE = "user-exchange";
    private static final String ROUTING_KEY = "project.created";

    private final RabbitTemplate rabbitTemplate;

    public void projectCreated(ProjectCreatedEvent event) {
        try {
            rabbitTemplate.convertAndSend(EXCHANGE, ROUTING_KEY, event);
        } catch (Exception e) {
            log.error("Failed to publish project.created event for project {}: {}",
                    event.projectId(), e.getMessage());
        }
    }
}