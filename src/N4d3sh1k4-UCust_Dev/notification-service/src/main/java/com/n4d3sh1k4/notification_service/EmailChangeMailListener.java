package com.n4d3sh1k4.notification_service;

import com.n4d3sh1k4.notification_service.config.RabbitMailConfig;
import com.n4d3sh1k4.notification_service.dto.EmailChangeMessage;
import com.n4d3sh1k4.notification_service.service.EmailService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
public class EmailChangeMailListener {

    private final EmailService emailService;

    @RabbitListener(queues = RabbitMailConfig.EMAIL_CHANGE_INIT_QUEUE)
    public void handleEmailChangeInit(EmailChangeMessage message) {
        log.info("Processing email change init for user: {}", message.userId());
        executeSafe(() -> emailService.sendEmailChangeInitEmail(message.email(), message.token()));
    }

    @RabbitListener(queues = RabbitMailConfig.EMAIL_CHANGE_NEW_QUEUE)
    public void handleEmailChangeNew(EmailChangeMessage message) {
        log.info("Processing email change new email confirmation for: {}", message.email());
        executeSafe(() -> emailService.sendEmailChangeNewEmail(message.email(), message.code()));
    }

    @RabbitListener(queues = RabbitMailConfig.EMAIL_CHANGE_DONE_QUEUE)
    public void handleEmailChangeDone(EmailChangeMessage message) {
        log.info("Processing email change done for user: {}", message.userId());
        executeSafe(() -> emailService.sendEmailChangeDoneEmail(message.email()));
    }

    private void executeSafe(Runnable action) {
        try {
            action.run();
        } catch (Exception e) {
            log.error("Error during email dispatch: {}", e.getMessage());
        }
    }
}