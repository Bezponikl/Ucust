package com.n4d3sh1k4.security_service.dto.request_dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Schema(description = "Запрос на подтверждение смены почты")
@Data
public class ConfirmEmailChangeRequest {

    @Schema(description = "Токен из письма на новую почту")
    @NotBlank
    private String token;

    @Schema(description = "Код подтверждения из письма на новую почту")
    @NotBlank
    private String code;
}
