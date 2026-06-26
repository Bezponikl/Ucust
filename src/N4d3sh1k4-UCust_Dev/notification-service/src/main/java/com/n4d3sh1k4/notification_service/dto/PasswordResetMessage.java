package com.n4d3sh1k4.notification_service.dto;

public record PasswordResetMessage(String email, String token) {
}
