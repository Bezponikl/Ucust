package com.n4d3sh1k4.billing_service.dto;

import com.n4d3sh1k4.billing_service.domain.model.tariff.AnalyticsType;
import com.n4d3sh1k4.billing_service.domain.model.tariff.ChatBotType;
import com.n4d3sh1k4.billing_service.domain.model.tariff.SupportType;
import io.swagger.v3.oas.annotations.media.Schema;

import java.math.BigDecimal;
import java.util.UUID;

@Schema(description = "Информация о тарифе")
public record TariffResponse(
        @Schema(description = "ID тарифа") UUID id,
        @Schema(description = "Название") String name,
        @Schema(description = "Стоимость") BigDecimal cost,
        @Schema(description = "Количество проектов") int projects,
        @Schema(description = "Количество постов") int posts,
        @Schema(description = "Тип чат-бота") ChatBotType chatBotType,
        @Schema(description = "Тип поддержки") SupportType supportType,
        @Schema(description = "Тип аналитики") AnalyticsType analyticsType,
        @Schema(description = "Количество AI генераций") int aiGenerations
) {
}
