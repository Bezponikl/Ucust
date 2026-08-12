package com.n4d3sh1k4.billing_service.dto.request_dto;

import com.n4d3sh1k4.billing_service.domain.model.tariff.AnalyticsType;
import com.n4d3sh1k4.billing_service.domain.model.tariff.ChatBotType;
import com.n4d3sh1k4.billing_service.domain.model.tariff.SupportType;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;
import lombok.Data;

import java.math.BigDecimal;

@Schema(description = "Запрос на создание тарифа")
@Data
public class CreateTariffRequest {

    @Schema(example = "PRO")
    @NotBlank
    private String name;

    @Schema(example = "29.99")
    @NotNull
    @PositiveOrZero
    private BigDecimal cost;

    @Schema(example = "10")
    @PositiveOrZero
    private int projects;

    @Schema(example = "100")
    @PositiveOrZero
    private int posts;

    @Schema(example = "BASIC")
    @NotNull
    private ChatBotType chatBotType;

    @Schema(example = "CHAT")
    @NotNull
    private SupportType supportType;

    @Schema(example = "PRO")
    @NotNull
    private AnalyticsType analyticsType;

    @Schema(example = "500")
    @PositiveOrZero
    private int aiGenerations;
}
