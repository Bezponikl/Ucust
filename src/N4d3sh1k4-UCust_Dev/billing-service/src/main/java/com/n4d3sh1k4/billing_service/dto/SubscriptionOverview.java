package com.n4d3sh1k4.billing_service.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.Instant;
import java.util.Map;
import java.util.UUID;

@Schema(description = "Свой тариф и квоты пользователя")
public record SubscriptionOverview(
        @Schema(description = "ID пользователя") UUID userId,
        @Schema(description = "ID тарифа") UUID tariffId,
        @Schema(description = "Название тарифа") String tariffName,
        @Schema(description = "Дата начала периода") Instant startDate,
        @Schema(description = "Дата следующего сброса квот") Instant nextResetDate,
        @Schema(description = "Квоты по фичам: project, post, generation") Map<String, QuotaInfo> quotas
) {
    @Schema(description = "Квота по фиче")
    public record QuotaInfo(
            @Schema(description = "Лимит (0 — фича не доступна, -1 — без лимита)") int limit,
            @Schema(description = "Использовано") int used
    ) {
    }
}