package com.n4d3sh1k4.generative_orchestration_service.dto;

import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.TaskStatus;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.Instant;
import java.util.UUID;

@Schema(description = "Статус задачи генерации")
public record TaskStatusResponse(
        @Schema(description = "ID задачи") UUID taskId,
        @Schema(description = "Внешний ID в AI-сервисе") String externalTaskId,
        @Schema(description = "Статус") TaskStatus status,
        @Schema(description = "ID созданного поста (если готов)") UUID resultPostId,
        @Schema(description = "Сообщение об ошибке") String errorMessage,
        @Schema(description = "Создан") Instant createdAt,
        @Schema(description = "Обновлён") Instant updatedAt
) {
}
