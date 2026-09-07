package com.n4d3sh1k4.billing_service.domain.repository;

import com.n4d3sh1k4.billing_service.domain.model.billing.UserSubscription;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface UserSubscriptionRepository extends JpaRepository<UserSubscription, UUID> {
    Optional<UserSubscription> findByUserId(UUID userId);
}
