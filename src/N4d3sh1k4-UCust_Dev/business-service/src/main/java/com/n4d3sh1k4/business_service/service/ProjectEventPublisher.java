package com.n4d3sh1k4.business_service.service;

import com.n4d3sh1k4.common.dto.ProjectCreatedEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class ProjectEventPublisher {

    private final OutboxPublisher outboxPublisher;

    public void projectCreated(ProjectCreatedEvent event) {
        log.info("Storing project.created event for project {}", event.projectId());
        outboxPublisher.publish("project.created", event);
    }
}
