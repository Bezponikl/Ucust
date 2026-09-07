package com.n4d3sh1k4.billing_service.domain.model.billing;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "usage_counters")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UsageCounter {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id")
    private UUID id;

    @Column(name = "user_id", nullable = false)
    private UUID userId;

    @Column(name = "feature", nullable = false)
    private String feature;

    @Column(name = "used", nullable = false)
    private int used;

    @Column(name = "limit_value", nullable = false)
    private int limitValue;

    @Column(name = "period_start", nullable = false)
    private Instant periodStart;
}
