package com.n4d3sh1k4.security_service.domain.repository;

import com.n4d3sh1k4.security_service.domain.model.ban.Ban;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface BanRepository extends JpaRepository<Ban, UUID> {

    Optional<Ban> findByUserIdAndActiveTrue(UUID userId);

    List<Ban> findByUserIdOrderByCreatedAtDesc(UUID userId);

    @Query("SELECT b FROM Ban b WHERE b.active = true")
    List<Ban> findAllActive();

    @Modifying
    @Query("UPDATE Ban b SET b.active = false WHERE b.user.id = :userId AND b.active = true")
    void deactivateAllActiveByUserId(@Param("userId") UUID userId);
}
