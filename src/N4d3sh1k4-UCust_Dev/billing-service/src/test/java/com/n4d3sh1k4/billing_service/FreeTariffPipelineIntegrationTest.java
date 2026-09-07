package com.n4d3sh1k4.billing_service;

import com.n4d3sh1k4.billing_service.config.RabbitConfig;
import com.n4d3sh1k4.billing_service.domain.model.billing.UserSubscription;
import com.n4d3sh1k4.billing_service.domain.model.tariff.Tariff;
import com.n4d3sh1k4.billing_service.domain.repository.TariffRepository;
import com.n4d3sh1k4.billing_service.domain.repository.UserSubscriptionRepository;
import com.n4d3sh1k4.billing_service.listener.UserConfirmedEventHandler;
import com.n4d3sh1k4.common.dto.UserEmailConfirmedEvent;
import org.junit.jupiter.api.Test;
import org.springframework.amqp.core.Binding;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

import java.time.Instant;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@TestPropertySource(properties = {
        "spring.datasource.url=jdbc:h2:mem:testdb",
        "spring.datasource.driver-class-name=org.h2.Driver",
        "spring.jpa.database-platform=org.hibernate.dialect.H2Dialect",
        "spring.rabbitmq.listener.simple.auto-startup=false"
})
class FreeTariffPipelineIntegrationTest {

    @Autowired
    private UserConfirmedEventHandler handler;

    @Autowired
    private UserSubscriptionRepository subscriptionRepository;

    @Autowired
    private TariffRepository tariffRepository;

    @Autowired
    @Qualifier("userConfirmedBinding")
    private Binding userConfirmedBinding;

    @Test
    void emailConfirmedEvent_createsFreeSubscription() {
        Tariff freeTariff = tariffRepository.findByName("FREE").orElseThrow();
        UUID userId = UUID.randomUUID();

        handler.handle(new UserEmailConfirmedEvent(userId, "user@example.com"));

        UserSubscription subscription = subscriptionRepository.findByUserId(userId).orElseThrow();
        assertThat(subscription.getTariffId()).isEqualTo(freeTariff.getId());
        assertThat(subscription.isPaid()).isTrue();
        assertThat(subscription.getStartDate()).isNotNull();
        assertThat(subscription.getNextResetDate()).isAfter(Instant.now());
    }

    @Test
    void emailConfirmedEvent_whenAlreadySubscribed_keepsExisting() {
        Tariff freeTariff = tariffRepository.findByName("FREE").orElseThrow();
        UUID userId = UUID.randomUUID();
        UserEmailConfirmedEvent event = new UserEmailConfirmedEvent(userId, "user@example.com");

        handler.handle(event);
        handler.handle(event);

        UserSubscription subscription = subscriptionRepository.findByUserId(userId).orElseThrow();
        assertThat(subscription.getTariffId()).isEqualTo(freeTariff.getId());
    }

    @Test
    void rabbitWiring_bindsUserConfirmedQueueToUserExchange() {
        assertThat(RabbitConfig.USER_CONFIRMED_QUEUE).isEqualTo("billing-user-confirmed-queue");
        assertThat(userConfirmedBinding.getExchange()).isEqualTo("user-exchange");
        assertThat(userConfirmedBinding.getDestination()).isEqualTo(RabbitConfig.USER_CONFIRMED_QUEUE);
        assertThat(userConfirmedBinding.getRoutingKey()).isEqualTo("user.email.confirmed");
    }
}