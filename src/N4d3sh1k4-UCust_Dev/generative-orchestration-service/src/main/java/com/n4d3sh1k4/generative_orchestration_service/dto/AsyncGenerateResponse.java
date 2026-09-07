package com.n4d3sh1k4.generative_orchestration_service.dto;

import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.TaskStatus;
import io.swagger.v3.oas.annotations.media.Schema;

import java.util.UUID;

@Schema(description = "Ответ на асинхронный запрос генерации")
public record AsyncGenerateResponse(
        @Schema(description = "ID задачи") UUID taskId,
        @Schema(description = "Статус") TaskStatus status
) {
}
