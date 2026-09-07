package com.n4d3sh1k4.billing_service.listener;

import com.n4d3sh1k4.billing_service.config.RabbitConfig;
import com.n4d3sh1k4.billing_service.service.SubscriptionService;
import com.n4d3sh1k4.common.dto.UserEmailConfirmedEvent;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.core.annotation.AnnotationUtils;

import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class UserConfirmedEventHandlerTest {

    private static final UUID USER_ID = UUID.fromString("22222222-2222-2222-2222-222222222222");

    @Mock
    private SubscriptionService subscriptionService;

    @InjectMocks
    private UserConfirmedEventHandler handler;

    @Test
    void handle_assignsFreeTariffForUser() {
        handler.handle(new UserEmailConfirmedEvent(USER_ID, "user@example.com"));

        verify(subscriptionService).assignFreeTariff(USER_ID);
    }

    @Test
    void listenerSubscribedToUserConfirmedQueue() {
        RabbitListener annotation = AnnotationUtils.findAnnotation(UserConfirmedEventHandler.class, RabbitListener.class);

        assertThat(annotation).isNotNull();
        assertThat(annotation.queues()).containsExactly(RabbitConfig.USER_CONFIRMED_QUEUE);
    }
}