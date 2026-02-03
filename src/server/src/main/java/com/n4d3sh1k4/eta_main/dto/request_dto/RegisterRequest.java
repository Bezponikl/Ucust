package com.n4d3sh1k4.eta_main.dto.request_dto;

import lombok.Data;

@Data
public class RegisterRequest {

    private String username;


    private String email;

    private String password;

    private String confirmPassword;
}
