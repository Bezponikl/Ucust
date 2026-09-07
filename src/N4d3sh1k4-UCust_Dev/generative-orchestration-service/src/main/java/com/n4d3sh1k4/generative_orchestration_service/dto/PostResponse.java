package com.n4d3sh1k4.generative_orchestration_service.dto;

import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.ContentType;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.GenerationMode;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.PostStatus;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.Instant;
import java.util.UUID;

@Schema(description = "Пост")
public record PostResponse(
        @Schema(description = "ID") UUID id,
        @Schema(description = "ID проекта") UUID projectId,
        @Schema(description = "Текст") String text,
        @Schema(description = "Изображение") String imageUrl,
        @Schema(description = "Хештеги") String hashtags,
        @Schema(description = "Целевые соцсети") String targetPlatforms,
        @Schema(description = "Дата публикации") Instant scheduledAt,
        @Schema(description = "Статус") PostStatus status,
        @Schema(description = "Тип контента") ContentType contentType,
        @Schema(description = "Режим генерации") GenerationMode generationMode,
        @Schema(description = "Создан") Instant createdAt
) {
}
