package com.n4d3sh1k4.notification_service.service;

import ch.qos.logback.classic.pattern.EnsureExceptionHandling;
import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;
import org.thymeleaf.TemplateEngine;
import org.thymeleaf.context.Context;

import java.time.Instant;

@Service
@RequiredArgsConstructor
@Slf4j
public class EmailService {

    private final JavaMailSender mailSender;
    private final TemplateEngine templateEngine;

    public void sendRegistrationEmail(String to, String username, String token) {
        Context context = new Context();
        context.setVariable("username", username);
        context.setVariable("activationUrl", "http://localhost:8180/api/v0/auth/confirm?token=" + token);

        String htmlContent = templateEngine.process("account-activate-email", context);

        sendHtmlEmail(to, "Подтверждение регистрации", htmlContent);
        log.info("Email sent to {}", to);
    }

    public void sendResetPasswordEmail(String to, String token) {
        Context context = new Context();
        context.setVariable("activationUrl", "http://localhost:8180/reset-password?token=" + token);

        String htmlContent = templateEngine.process("password-reset-email", context);

        sendHtmlEmail(to, "Сброс пароля", htmlContent);
        log.info("Reset password email sent to {}", to);
    }

    public void sendAccountLockedEmail(String to, Instant time) {
        Context context = new Context();
        context.setVariable("lockDate", " в "+time);

        String htmlContent = templateEngine.process("account-locked-email", context);

        sendHtmlEmail(to, "Сброс пароля", htmlContent);
    }

    private void sendHtmlEmail(String to, String subject, String htmlContent) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");

            helper.setTo(to);
            helper.setSubject(subject);
            helper.setText(htmlContent, true); // true означает, что это HTML

            mailSender.send(message);
        } catch (MessagingException e) {
            // Логируем ошибку отправки
        }
    }
}