package com.n4d3sh1k4.security_service.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;


@RestController
@RequestMapping("/users")
public class UserController {

    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "Тестовый контроллер - возвращает роль пользователя в системе.")
    @GetMapping("/check-me")
    public String checkMe(Authentication authentication) {
        return "Your authorities: " + authentication.getAuthorities();
    }
}
