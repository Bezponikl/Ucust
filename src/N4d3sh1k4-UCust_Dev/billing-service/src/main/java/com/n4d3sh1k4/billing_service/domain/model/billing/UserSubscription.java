package com.n4d3sh1k4.billing_service.domain.model.billing;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "user_subscriptions")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserSubscription {

    @Id
    @Column(name = "user_id", nullable = false)
    private UUID userId;

    @Column(name = "tariff_id", nullable = false)
    private UUID tariffId;

    @Column(name = "start_date", nullable = false)
    private Instant startDate;

    @Column(name = "next_reset_date", nullable = false)
    private Instant nextResetDate;

    @Column(name = "paid")
    private boolean paid;
}