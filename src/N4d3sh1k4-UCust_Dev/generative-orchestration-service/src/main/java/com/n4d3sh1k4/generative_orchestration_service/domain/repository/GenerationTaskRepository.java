package com.n4d3sh1k4.generative_orchestration_service.domain.repository;

import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.GenerationTask;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.TaskStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

public interface GenerationTaskRepository extends JpaRepository<GenerationTask, UUID> {

    List<GenerationTask> findByUserIdOrderByCreatedAtDesc(UUID userId);

    List<GenerationTask> findByProjectIdOrderByCreatedAtDesc(UUID projectId);

    List<GenerationTask> findByStatus(TaskStatus status);
}
