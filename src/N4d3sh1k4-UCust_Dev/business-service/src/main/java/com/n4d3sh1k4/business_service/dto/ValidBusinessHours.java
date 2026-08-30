package com.n4d3sh1k4.business_service.dto;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = BusinessHoursValidator.class)
public @interface ValidBusinessHours {
    String message() default "The closing time must be later than the opening time.";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
