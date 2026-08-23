package com.n4d3sh1k4.business_service.dto;

import com.n4d3sh1k4.business_service.domain.model.project.support.BusinessHours;
import com.n4d3sh1k4.business_service.domain.model.project.support.Industry;
import com.n4d3sh1k4.business_service.domain.model.project.support.SocialLinks;
import com.n4d3sh1k4.business_service.domain.model.project.support.ToneOfVoice;
import io.swagger.v3.oas.annotations.media.Schema;

import java.util.UUID;

@Schema(description = "Ответ с данными проекта")
public record ProjectResponse(
    @Schema(description = "Идентификатор проекта", example = "fda96fb5-5e1f-44b4-a942-3b6c05f41b79")
    UUID id,

    @Schema(description = "Название проекта", example = "Мой бизнес")
    String name,

    @Schema(description = "Сфера деятельности")
    Industry industry,

    @Schema(description = "Город", example = "Москва")
    String city,

    @Schema(description = "Описание проекта", example = "Описание деятельности компании")
    String description,

    @Schema(description = "Целевая аудитория", example = "Молодые специалисты от 25 до 40 лет")
    String targetAudience,

    @Schema(description = "Тон общения")
    ToneOfVoice toneOfVoice,

    @Schema(description = "Ссылки на соцсети")
    SocialLinks socialLinks,

    @Schema(description = "Часы работы")
    BusinessHours businessHours,

    @Schema(description = "Идентификатор владельца", example = "fda96fb5-5e1f-44b4-a942-3b6c05f41b79")
    UUID ownerId,

    @Schema(description = "URL логотипа", example = "https://minio.example.com/user-service/logos/uuid.jpg")
    String logoUrl
) {}
