package com.n4d3sh1k4.generative_orchestration_service.dto.request_dto;

import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.GenerationMode;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.UUID;

@Schema(description = "Запрос на генерацию контента")
@Data
public class GenerateRequest {

    @Schema(description = "ID проекта")
    @NotNull
    private UUID projectId;

    @Schema(description = "Количество постов", example = "1")
    @Min(1)
    private int count = 1;

    @Schema(description = "Режим: AUTO — из полей проекта, MANUAL — пользователь задаёт параметры")
    @NotNull
    private GenerationMode mode;

    @Schema(description = "Промпт / тема (для MANUAL режима)")
    private String prompt;

    @Schema(description = "Сфера деятельности бизнеса")
    private String industry;

    @Schema(description = "Описание бизнеса")
    private String description;

    @Schema(description = "Целевая аудитория")
    private String targetAudience;

    @Schema(description = "Tone of voice")
    private String toneOfVoice;

    @Schema(description = "Город (для локальных событий)")
    private String city;

    @Schema(description = "Текущий месяц", example = "Январь")
    private String currentMonth;

    @Schema(description = "Текущий год", example = "2026")
    private int currentYear;
}