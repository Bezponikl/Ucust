package com.n4d3sh1k4.billing_service.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotNull;

import java.util.UUID;

@Schema(description = "Запрос на покупку тарифа (заглушка)")
public record PurchaseTariffRequest(
        @NotNull(message = "tariffId is required")
        @Schema(description = "ID тарифа")
        UUID tariffId
) {
}