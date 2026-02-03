package com.n4d3sh1k4.eta_main.dto.request_dto;

import lombok.Data;

@Data
public class LoginRequest {
    private String email;
    private String password;
}
