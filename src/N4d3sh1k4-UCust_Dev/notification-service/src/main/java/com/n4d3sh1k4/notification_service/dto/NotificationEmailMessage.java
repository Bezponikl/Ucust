package com.n4d3sh1k4.notification_service.dto;

public record NotificationEmailMessage(
        String username,
        String email,
        String token,
        String accountActivationTokenTtl) {
}
