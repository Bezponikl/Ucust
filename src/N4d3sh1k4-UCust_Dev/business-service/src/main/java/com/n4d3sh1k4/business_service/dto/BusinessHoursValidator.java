package com.n4d3sh1k4.business_service.dto;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

import java.time.LocalTime;

public class BusinessHoursValidator implements ConstraintValidator<ValidBusinessHours, Object> {

    @Override
    public boolean isValid(Object value, ConstraintValidatorContext context) {
        try {
            LocalTime open = (LocalTime) value.getClass().getMethod("openTime").invoke(value);
            LocalTime close = (LocalTime) value.getClass().getMethod("closeTime").invoke(value);

            if (open == null || close == null) {
                return true;
            }

            return close.isAfter(open);
        } catch (Exception e) {
            return true;
        }
    }
}
