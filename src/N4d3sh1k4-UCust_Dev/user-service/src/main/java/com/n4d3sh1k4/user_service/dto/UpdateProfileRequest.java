package com.n4d3sh1k4.user_service.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

@Schema(description = "Запрос на обновление профиля")
public record UpdateProfileRequest(
    @Schema(description = "Имя (только кириллица, допускается дефис)", example = "Олег")
    @Size(min = 2, max = 50)
    @Pattern(regexp = "^[а-яА-ЯёЁ]+(-[а-яА-ЯёЁ]+)?$",
             message = "The name must be in Cyrillic and may contain a hyphen.")
    String firstName,

    @Schema(description = "Фамилия (только кириллица, допускается дефис)", example = "Иванов")
    @Size(min = 2, max = 50)
    @Pattern(regexp = "^[а-яА-ЯёЁ]+(-[а-яА-ЯёЁ]+)?$",
             message = "The surname must be in Cyrillic and may contain a hyphen.")
    String lastName,

    @Schema(description = "Телефон (11 цифр, начинается с 79)", example = "79991234567")
    @Pattern(regexp = "^79[0-9]{9}$", message = "The phone number must be 11 digits long and start with 79")
    String phone,

    @Schema(description = "Должность", example = "Разработчик")
    @Size(min = 2, max = 50)
    String position
) {}