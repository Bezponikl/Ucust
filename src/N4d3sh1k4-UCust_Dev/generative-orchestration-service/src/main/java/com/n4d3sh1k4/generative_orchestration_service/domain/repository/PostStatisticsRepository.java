package com.n4d3sh1k4.generative_orchestration_service.domain.repository;

import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.PostStatistics;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface PostStatisticsRepository extends JpaRepository<PostStatistics, UUID> {
    List<PostStatistics> findByPostId(UUID postId);
}
