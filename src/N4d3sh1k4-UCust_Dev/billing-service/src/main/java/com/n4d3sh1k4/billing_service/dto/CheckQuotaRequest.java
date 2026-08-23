package com.n4d3sh1k4.billing_service.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.UUID;

@Schema(description = "Запрос проверки квоты")
@Data
public class CheckQuotaRequest {

    @Schema(description = "ID пользователя")
    @NotNull
    private UUID userId;

    @Schema(description = "Фича (generation, post, ...)")
    @NotBlank
    private String feature;

    @Schema(description = "Запрашиваемое количество")
    private int requested;
}