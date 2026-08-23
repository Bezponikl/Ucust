package com.n4d3sh1k4.security_service.dto.request_dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.time.Instant;
import java.util.UUID;

@Schema(description = "Запрос на создание бана")
@Data
public class CreateBanRequest {

    @Schema(description = "ID пользователя", example = "550e8400-e29b-41d4-a716-446655440000")
    @NotNull
    private UUID userId;

    @Schema(description = "Причина бана", example = "Нарушение правил платформы")
    @NotBlank
    private String reason;

    @Schema(description = "Дата окончания бана (null = навсегда)", example = "2026-08-01T00:00:00Z")
    private Instant expiresAt;
}
