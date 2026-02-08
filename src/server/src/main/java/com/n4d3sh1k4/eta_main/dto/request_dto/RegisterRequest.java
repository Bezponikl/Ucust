package com.n4d3sh1k4.eta_main.dto.request_dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class RegisterRequest {

    @NotBlank
    @Size(min = 2, max = 50)
    @Pattern(regexp = "^[а-яА-ЯёЁ]+(-[а-яА-ЯёЁ]+)?( [а-яА-ЯёЁ]+(-[а-яА-ЯёЁ]+)?){0,2}$",
             message = "Имя должно быть на кириллице (1-3 слова) и может содержать дефис")
    private String username;

    @NotBlank
    @Email
    @Size(max = 50)
    private String email;

    @NotBlank
    @Size(min = 8, max = 50)
    @Pattern(regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)[a-zA-Z\\d]+$",
             message = "Пароль должен содержать латиницу, цифры, заглавные и строчные буквы")
    private String password;

    private String confirmPassword;
}
