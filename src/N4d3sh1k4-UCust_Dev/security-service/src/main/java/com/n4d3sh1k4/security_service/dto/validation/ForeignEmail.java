package com.n4d3sh1k4.security_service.dto.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target({ ElementType.FIELD, ElementType.PARAMETER })
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = ForeignEmailValidator.class)
public @interface ForeignEmail {
    String message() default "Only foreign email providers are allowed. Russian email domains (@mail.ru, @yandex.ru, etc.) are not accepted.";

    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
