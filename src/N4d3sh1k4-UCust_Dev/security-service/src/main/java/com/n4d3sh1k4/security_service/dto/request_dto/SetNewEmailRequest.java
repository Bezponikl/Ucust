package com.n4d3sh1k4.security_service.dto.request_dto;

import com.n4d3sh1k4.security_service.dto.validation.RussianEmail;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Schema(description = "Запрос на установку новой почты для смены")
@Data
public class SetNewEmailRequest {

    @Schema(description = "Токен из письма на текущую почту")
    @NotBlank
    private String token;

    @Schema(description = "Новая почта")
    @NotBlank
    @Email
    @RussianEmail
    private String newEmail;
}
