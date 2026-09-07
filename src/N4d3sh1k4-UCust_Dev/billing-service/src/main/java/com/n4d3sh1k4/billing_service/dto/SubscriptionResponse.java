package com.n4d3sh1k4.billing_service.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.Instant;
import java.util.UUID;

@Schema(description = "Подписка пользователя")
public record SubscriptionResponse(
        @Schema(description = "ID пользователя") UUID userId,
        @Schema(description = "ID тарифа") UUID tariffId,
        @Schema(description = "Название тарифа") String tariffName,
        @Schema(description = "Дата начала периода") Instant startDate,
        @Schema(description = "Дата следующего сброса квот") Instant nextResetDate
) {
}