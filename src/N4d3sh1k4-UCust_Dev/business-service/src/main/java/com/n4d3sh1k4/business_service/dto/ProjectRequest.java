package com.n4d3sh1k4.business_service.dto;

import com.n4d3sh1k4.business_service.domain.model.project.support.Industry;
import com.n4d3sh1k4.business_service.domain.model.project.support.ToneOfVoice;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

@Schema(description = "Запрос на создание проекта")
public record ProjectRequest(
    @Schema(description = "Название проекта", example = "Мой бизнес")
    @NotBlank
    @Size(min = 2, max = 100)
    String name,

    @Schema(description = "Сфера деятельности")
    @NotNull
    Industry industry,

    @Schema(description = "Город", example = "Москва")
    @NotBlank
    @Size(max = 50)
    String city,

    @Schema(description = "Описание проекта", example = "Описание деятельности компании")
    @Size(max = 2000)
    String description,

    @Schema(description = "Целевая аудитория", example = "Молодые специалисты от 25 до 40 лет")
    @Size(max = 500)
    String targetAudience,

    @Schema(description = "Тон общения")
    @NotNull
    ToneOfVoice toneOfVoice,

    @Schema(description = "Ссылки на соцсети")
    @Valid
    SocialLinksRequest socialLinks,

    @Schema(description = "Часы работы")
    @Valid
    BusinessHoursRequest businessHours
) {}