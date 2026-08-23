package com.n4d3sh1k4.billing_service.listener;

import com.n4d3sh1k4.billing_service.config.RabbitConfig;
import com.n4d3sh1k4.billing_service.service.SubscriptionService;
import com.n4d3sh1k4.common.dto.UserEmailConfirmedEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitHandler;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
@RabbitListener(queues = RabbitConfig.USER_CONFIRMED_QUEUE)
public class UserConfirmedEventHandler {

    private final SubscriptionService subscriptionService;

    @RabbitHandler
    public void handle(UserEmailConfirmedEvent event) {
        log.info("Received user.email.confirmed event for user {}", event.userId());
        subscriptionService.assignFreeTariff(event.userId());
    }
}
