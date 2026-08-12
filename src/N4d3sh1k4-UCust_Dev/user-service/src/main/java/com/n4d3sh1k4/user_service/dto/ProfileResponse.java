package com.n4d3sh1k4.user_service.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import java.util.UUID;

@Schema(description = "Ответ с профилем пользователя")
public record ProfileResponse(
    @Schema(description = "Идентификатор пользователя", example = "fda96fb5-5e1f-44b4-a942-3b6c05f41b79")
    UUID id,

    @Schema(description = "Имя", example = "Олег")
    String firstName,

    @Schema(description = "Фамилия", example = "Иванов")
    String lastName,

    @Schema(description = "Email", example = "user@example.com")
    String email,

    @Schema(description = "Телефон", example = "79991234567")
    String phone,

    @Schema(description = "Должность", example = "Разработчик")
    String position,

    @Schema(description = "URL аватара", example = "https://minio.example.com/user-service/avatars/uuid.jpg")
    String fullAvatarUrl) {}
