package com.n4d3sh1k4.notification_service.config;

import com.n4d3sh1k4.notification_service.dto.AccountLockedMessage;
import com.n4d3sh1k4.notification_service.dto.PasswordResetMessage;
import com.n4d3sh1k4.notification_service.dto.UserCreatedMessage;
import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.TopicExchange;
import org.springframework.amqp.support.converter.DefaultJacksonJavaTypeMapper;
import org.springframework.amqp.support.converter.JacksonJsonMessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.HashMap;
import java.util.Map;


@Configuration
public class RabbitMailConfig {

    public static final String MAIL_QUEUE = "mail-notification-queue";

    @Bean
    public Queue mailQueue() {
        return new Queue(MAIL_QUEUE, true);
    }

    @Bean
    public TopicExchange exchange() {
        return new TopicExchange("user-exchange");
    }

    @Bean
    public Binding binding(Queue mailQueue, TopicExchange exchange) {
        return BindingBuilder.bind(mailQueue).to(exchange).with("user.registration.email");
    }

    @Bean
    public Binding passwordResetBinding(Queue mailQueue, TopicExchange exchange) {
        return BindingBuilder.bind(mailQueue).to(exchange).with("user.password.reset");
    }

    @Bean
    public Binding userAccountLockedBinding(Queue mailQueue, TopicExchange exchange) {
        return BindingBuilder.bind(mailQueue).to(exchange).with("user.account.locked");
    }

    @Bean
    public JacksonJsonMessageConverter messageConverter() { // Используем новый класс без "2"
        JacksonJsonMessageConverter converter = new JacksonJsonMessageConverter();

        DefaultJacksonJavaTypeMapper typeMapper = new DefaultJacksonJavaTypeMapper();
        // Доверяем всем пакетам для гибкости микросервисов
        typeMapper.setTrustedPackages("*");

        // Настраиваем нашу "карту соответствия"
        Map<String, Class<?>> idClassMapping = new HashMap<>();

        // Мапим сообщения из Security на локальные события Notification
        idClassMapping.put("com.n4d3sh1k4.security_service.dto.event.PasswordResetMessage", PasswordResetMessage.class);
        idClassMapping.put("com.n4d3sh1k4.security_service.dto.event.NotificationEmailMessage", UserCreatedMessage.class);
        idClassMapping.put("com.n4d3sh1k4.security_service.dto.event.AccountLockedMessage", AccountLockedMessage.class);

        typeMapper.setIdClassMapping(idClassMapping);
        converter.setJavaTypeMapper(typeMapper);

        return converter;
    }
}