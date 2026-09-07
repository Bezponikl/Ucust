package com.n4d3sh1k4.billing_service.dto.request_dto;

import com.n4d3sh1k4.billing_service.domain.model.tariff.AnalyticsType;
import com.n4d3sh1k4.billing_service.domain.model.tariff.ChatBotType;
import com.n4d3sh1k4.billing_service.domain.model.tariff.SupportType;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.PositiveOrZero;
import lombok.Data;

import java.math.BigDecimal;

@Schema(description = "Запрос на обновление тарифа")
@Data
public class UpdateTariffRequest {

    @Schema(example = "PRO")
    private String name;

    @Schema(example = "29.99")
    @PositiveOrZero
    private BigDecimal cost;

    @Schema(example = "10")
    @PositiveOrZero
    private Integer projects;

    @Schema(example = "100")
    @PositiveOrZero
    private Integer posts;

    @Schema(example = "BASIC")
    private ChatBotType chatBotType;

    @Schema(example = "CHAT")
    private SupportType supportType;

    @Schema(example = "PRO")
    private AnalyticsType analyticsType;

    @Schema(example = "500")
    @PositiveOrZero
    private Integer aiGenerations;
}
