package com.n4d3sh1k4.notification_service;

import com.n4d3sh1k4.notification_service.config.RabbitMailConfig;
import com.n4d3sh1k4.notification_service.dto.AccountLockedMessage;
import com.n4d3sh1k4.notification_service.dto.LoginMessage;
import com.n4d3sh1k4.notification_service.dto.PasswordResetMessage;
import com.n4d3sh1k4.notification_service.dto.NotificationEmailMessage;
import com.n4d3sh1k4.notification_service.service.EmailService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitHandler;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
@RabbitListener(queues = RabbitMailConfig.MAIL_QUEUE)
public class MailListener {

    private final EmailService emailService;

    @RabbitHandler
    public void handleRegistration(NotificationEmailMessage message) {
        log.info("Processing registration mail for: {}", message.email());
        executeSafe(() -> emailService.sendRegistrationEmail(message.email(), message.username(), message.token(), message.accountActivationTokenTtl()));
    }

    @RabbitHandler
    public void handlePasswordReset(PasswordResetMessage message) {
        log.info("Processing password reset mail for: {}", message.email());
        executeSafe(() -> emailService.sendResetPasswordEmail(message.email(), message.token(), message.passwordResetTokenTtl()));
    }

    @RabbitHandler
    public void handleAccountLocked(AccountLockedMessage message) {
        log.info("Processing user account mail for: {}", message.email());
        executeSafe(() -> emailService.sendAccountLockedEmail(message.email(), message.timestamp(), message.accountLockedCooldown()));
    }

    @RabbitHandler
    public void handleLogin(LoginMessage message) {
        log.info("Processing login notification mail for: {}", message.email());
        executeSafe(() -> emailService.sendLoginEmail(message.email(), message.ipAddress(), message.userAgent(), message.timestamp()));
    }

    private void executeSafe(Runnable action) {
        try {
            action.run();
        } catch (Exception e) {
            log.error("Error during email dispatch: {}", e.getMessage());
        }
    }
}