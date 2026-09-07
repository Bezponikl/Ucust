package com.n4d3sh1k4.security_service.dto.request_dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Schema(description = "Запрос на подтверждение пароля для смены почты")
@Data
public class VerifyPasswordRequest {

    @Schema(description = "Текущий пароль")
    @NotBlank
    private String password;
}
