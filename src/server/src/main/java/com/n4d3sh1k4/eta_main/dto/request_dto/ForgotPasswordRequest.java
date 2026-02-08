package com.n4d3sh1k4.eta_main.dto.request_dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class ForgotPasswordRequest {
    @NotBlank
    @Email
    @Size(max = 50)
    private String email;
}