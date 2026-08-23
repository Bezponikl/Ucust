package com.n4d3sh1k4.security_service.dto;

import com.n4d3sh1k4.security_service.domain.model.ban.BanType;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.Instant;
import java.util.UUID;

@Schema(description = "Информация о бане")
public record BanResponse(
        @Schema(description = "ID бана") UUID id,
        @Schema(description = "ID пользователя") UUID userId,
        @Schema(description = "Email пользователя") String email,
        @Schema(description = "Тип бана") BanType type,
        @Schema(description = "Причина") String reason,
        @Schema(description = "ID администратора") UUID bannedBy,
        @Schema(description = "Дата создания") Instant createdAt,
        @Schema(description = "Дата окончания (null = навсегда)") Instant expiresAt,
        @Schema(description = "Активен ли бан") boolean active
) {
}
