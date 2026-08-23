package com.n4d3sh1k4.business_service.domain.repository;

import com.n4d3sh1k4.business_service.domain.model.outbox.OutboxEvent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface OutboxEventRepository extends JpaRepository<OutboxEvent, UUID> {

    List<OutboxEvent> findTop100ByPublishedAtIsNullOrderByCreatedAtAsc();
}