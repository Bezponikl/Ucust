package com.n4d3sh1k4.billing_service.domain.repository;

import com.n4d3sh1k4.billing_service.domain.model.billing.UsageCounter;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface UsageCounterRepository extends JpaRepository<UsageCounter, UUID> {
    Optional<UsageCounter> findByUserIdAndFeature(UUID userId, String feature);

    List<UsageCounter> findAllByUserId(UUID userId);
}
