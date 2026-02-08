package com.n4d3sh1k4.eta_main.dto.request_dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class ResetPasswordRequest {
    private String token;

    @NotBlank
    @Size(min = 8, max = 50)
    @Pattern(regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)[a-zA-Z\\d]+$",
             message = "Пароль должен содержать латиницу, цифры, заглавные и строчные буквы")
    private String newPassword;
}