package com.n4d3sh1k4.notification_service.config;

import com.n4d3sh1k4.notification_service.dto.AccountLockedMessage;
import com.n4d3sh1k4.notification_service.dto.EmailChangeMessage;
import com.n4d3sh1k4.notification_service.dto.LoginMessage;
import com.n4d3sh1k4.notification_service.dto.PasswordResetMessage;
import com.n4d3sh1k4.notification_service.dto.NotificationEmailMessage;
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
    public static final String EMAIL_CHANGE_INIT_QUEUE = "mail-email-change-init-queue";
    public static final String EMAIL_CHANGE_NEW_QUEUE = "mail-email-change-new-queue";
    public static final String EMAIL_CHANGE_DONE_QUEUE = "mail-email-change-done-queue";
    public static final String DLX = "user-exchange.dlx";

    private Queue durableQueue(String name) {
        Map<String, Object> args = new HashMap<>();
        args.put("x-dead-letter-exchange", DLX);
        args.put("x-dead-letter-routing-key", name + ".dlq");
        return new Queue(name, true, false, false, args);
    }

    @Bean
    public Queue mailQueue() {
        return durableQueue(MAIL_QUEUE);
    }

    @Bean
    public Queue mailDlq() {
        return new Queue(MAIL_QUEUE + ".dlq", true);
    }

    @Bean
    public TopicExchange dlx() {
        return new TopicExchange(DLX);
    }

    @Bean
    public Binding mailDlqBinding(Queue mailDlq, TopicExchange dlx) {
        return BindingBuilder.bind(mailDlq).to(dlx).with(MAIL_QUEUE + ".dlq");
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
    public Queue emailChangeInitQueue() {
        return durableQueue(EMAIL_CHANGE_INIT_QUEUE);
    }

    @Bean
    public Queue emailChangeNewQueue() {
        return durableQueue(EMAIL_CHANGE_NEW_QUEUE);
    }

    @Bean
    public Queue emailChangeDoneQueue() {
        return durableQueue(EMAIL_CHANGE_DONE_QUEUE);
    }

    @Bean
    public Queue emailChangeInitDlq() {
        return new Queue(EMAIL_CHANGE_INIT_QUEUE + ".dlq", true);
    }

    @Bean
    public Queue emailChangeNewDlq() {
        return new Queue(EMAIL_CHANGE_NEW_QUEUE + ".dlq", true);
    }

    @Bean
    public Queue emailChangeDoneDlq() {
        return new Queue(EMAIL_CHANGE_DONE_QUEUE + ".dlq", true);
    }

    @Bean
    public Binding emailChangeInitDlqBinding(Queue emailChangeInitDlq, TopicExchange dlx) {
        return BindingBuilder.bind(emailChangeInitDlq).to(dlx).with(EMAIL_CHANGE_INIT_QUEUE + ".dlq");
    }

    @Bean
    public Binding emailChangeNewDlqBinding(Queue emailChangeNewDlq, TopicExchange dlx) {
        return BindingBuilder.bind(emailChangeNewDlq).to(dlx).with(EMAIL_CHANGE_NEW_QUEUE + ".dlq");
    }

    @Bean
    public Binding emailChangeDoneDlqBinding(Queue emailChangeDoneDlq, TopicExchange dlx) {
        return BindingBuilder.bind(emailChangeDoneDlq).to(dlx).with(EMAIL_CHANGE_DONE_QUEUE + ".dlq");
    }

    @Bean
    public Binding emailChangeInitBinding(Queue emailChangeInitQueue, TopicExchange exchange) {
        return BindingBuilder.bind(emailChangeInitQueue).to(exchange).with("user.email.change.init");
    }

    @Bean
    public Binding emailChangeNewBinding(Queue emailChangeNewQueue, TopicExchange exchange) {
        return BindingBuilder.bind(emailChangeNewQueue).to(exchange).with("user.email.change.new");
    }

    @Bean
    public Binding emailChangeDoneBinding(Queue emailChangeDoneQueue, TopicExchange exchange) {
        return BindingBuilder.bind(emailChangeDoneQueue).to(exchange).with("user.email.change.done");
    }

    @Bean
    public JacksonJsonMessageConverter messageConverter() {
        JacksonJsonMessageConverter converter = new JacksonJsonMessageConverter();

        DefaultJacksonJavaTypeMapper typeMapper = new DefaultJacksonJavaTypeMapper();
        typeMapper.setTrustedPackages("*");

        Map<String, Class<?>> idClassMapping = new HashMap<>();

        idClassMapping.put("com.n4d3sh1k4.security_service.dto.event.PasswordResetMessage", PasswordResetMessage.class);
        idClassMapping.put("com.n4d3sh1k4.security_service.dto.event.NotificationEmailMessage", NotificationEmailMessage.class);
        idClassMapping.put("com.n4d3sh1k4.security_service.dto.event.AccountLockedMessage", AccountLockedMessage.class);
        idClassMapping.put("com.n4d3sh1k4.security_service.dto.event.LoginEvent", LoginMessage.class);
        idClassMapping.put("com.n4d3sh1k4.security_service.dto.event.EmailChangeMessage", EmailChangeMessage.class);

        typeMapper.setIdClassMapping(idClassMapping);
        converter.setJavaTypeMapper(typeMapper);

        return converter;
    }
}