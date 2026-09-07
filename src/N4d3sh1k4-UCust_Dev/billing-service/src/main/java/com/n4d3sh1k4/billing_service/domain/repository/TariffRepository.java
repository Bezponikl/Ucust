package com.n4d3sh1k4.billing_service.domain.repository;

import com.n4d3sh1k4.billing_service.domain.model.tariff.Tariff;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.UUID;

import java.util.Optional;

@Repository
public interface TariffRepository extends JpaRepository<Tariff, UUID> {
    Optional<Tariff> findByName(String name);
}
