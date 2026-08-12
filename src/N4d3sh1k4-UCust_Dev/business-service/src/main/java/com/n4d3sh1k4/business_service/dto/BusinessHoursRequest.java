package com.n4d3sh1k4.business_service.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.DayOfWeek;
import java.time.LocalTime;
import java.util.List;

@ValidBusinessHours
@Schema(description = "Часы работы")
public record BusinessHoursRequest(
    @Schema(description = "Время открытия", example = "09:00")
    LocalTime openTime,

    @Schema(description = "Время закрытия", example = "18:00")
    LocalTime closeTime,

    @Schema(description = "Выходные дни", example = "[\"SATURDAY\", \"SUNDAY\"]")
    List<DayOfWeek> offDays
) {}