package com.n4d3sh1k4.billing_service.domain.model.tariff;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.UUID;

@Entity
@Table(name = "tariffs")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Tariff {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id")
    private UUID id;

    @Column(name = "name", nullable = false, unique = true)
    private String name;

    @Column(name = "cost", nullable = false, precision = 10, scale = 2)
    private BigDecimal cost;

    @Column(name = "projects")
    private int projects;

    @Column(name = "posts")
    private int posts;

    @Enumerated(EnumType.STRING)
    @Column(name = "chat_bot_type", nullable = false)
    private ChatBotType chatBotType;

    @Enumerated(EnumType.STRING)
    @Column(name = "support_type", nullable = false)
    private SupportType supportType;

    @Enumerated(EnumType.STRING)
    @Column(name = "analytics_type", nullable = false)
    private AnalyticsType analyticsType;

    @Column(name = "ai_generations")
    private int aiGenerations;
}