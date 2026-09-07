package com.n4d3sh1k4.business_service.domain.model.project.support;

import jakarta.persistence.Embeddable;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.DayOfWeek;
import java.time.LocalTime;
import java.util.Set;

@Embeddable
@Getter
@Setter
@NoArgsConstructor // Тот самый пустой конструктор, который просит MapStruct
@AllArgsConstructor
public class BusinessHours {
    LocalTime openTime;
    LocalTime closeTime;
    Set<DayOfWeek> offDays;
}
