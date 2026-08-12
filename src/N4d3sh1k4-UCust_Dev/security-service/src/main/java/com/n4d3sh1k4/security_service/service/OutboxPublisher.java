package com.n4d3sh1k4.security_service.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.n4d3sh1k4.security_service.domain.model.outbox.OutboxEvent;
import com.n4d3sh1k4.security_service.domain.repository.OutboxEventRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;

@Service
@RequiredArgsConstructor
@Slf4j
public class OutboxPublisher {

    private final OutboxEventRepository repository;
    private final ObjectMapper objectMapper;

    @Transactional
    public void publish(String routingKey, Object event) {
        try {
            OutboxEvent record = OutboxEvent.builder()
                    .routingKey(routingKey)
                    .eventType(event.getClass().getName())
                    .payload(objectMapper.writeValueAsString(event))
                    .createdAt(Instant.now())
                    .build();
            repository.save(record);
            log.debug("Outbox event {} stored for routing {}", record.getId(), routingKey);
        } catch (JsonProcessingException e) {
            throw new Error("Failed to serialize outbox event", e);
        }
    }
}