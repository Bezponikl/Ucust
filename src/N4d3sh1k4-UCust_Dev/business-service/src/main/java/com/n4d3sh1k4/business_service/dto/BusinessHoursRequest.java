package com.n4d3sh1k4.business_service.dto;

import java.time.DayOfWeek;
import java.time.LocalTime;
import java.util.List;

@ValidBusinessHours
public record BusinessHoursRequest(
    LocalTime openTime,
    LocalTime closeTime,
    List<DayOfWeek> offDays
) {}