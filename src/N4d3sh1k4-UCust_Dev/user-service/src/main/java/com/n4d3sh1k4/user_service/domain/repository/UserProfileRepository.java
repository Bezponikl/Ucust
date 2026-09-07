package com.n4d3sh1k4.user_service.domain.repository;

import com.n4d3sh1k4.user_service.domain.model.UserProfile;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface UserProfileRepository extends JpaRepository<UserProfile, UUID> {
    Optional<UserProfile> findById(Long userId);
}
