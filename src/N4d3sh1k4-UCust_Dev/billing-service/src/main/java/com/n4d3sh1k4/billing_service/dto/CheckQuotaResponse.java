package com.n4d3sh1k4.billing_service.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "Результат проверки квоты")
public record CheckQuotaResponse(
        @Schema(description = "Разрешено ли") boolean allowed,
        @Schema(description = "Осталось") int remaining,
        @Schema(description = "Лимит") int limit,
        @Schema(description = "Использовано") int used,
        @Schema(description = "Название тарифа") String tariffName
) {
}
