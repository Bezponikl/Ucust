package com.n4d3sh1k4.billing_service.config;

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
public class RabbitConfig {

    public static final String USER_CONFIRMED_QUEUE = "billing-user-confirmed-queue";
    public static final String USER_CONFIRMED_DLQ = USER_CONFIRMED_QUEUE + ".dlq";
    public static final String DLX = "user-exchange.dlx";

    @Bean
    public Queue userConfirmedQueue() {
        Map<String, Object> args = new HashMap<>();
        args.put("x-dead-letter-exchange", DLX);
        args.put("x-dead-letter-routing-key", USER_CONFIRMED_DLQ);
        return new Queue(USER_CONFIRMED_QUEUE, true, false, false, args);
    }

    @Bean
    public Queue userConfirmedDlq() {
        return new Queue(USER_CONFIRMED_DLQ, true);
    }

    @Bean
    public TopicExchange dlx() {
        return new TopicExchange(DLX);
    }

    @Bean
    public Binding userConfirmedDlqBinding(Queue userConfirmedDlq, TopicExchange dlx) {
        return BindingBuilder.bind(userConfirmedDlq).to(dlx).with(USER_CONFIRMED_DLQ);
    }

    @Bean
    public TopicExchange userExchange() {
        return new TopicExchange("user-exchange");
    }

    @Bean
    public Binding userConfirmedBinding(Queue userConfirmedQueue, TopicExchange userExchange) {
        return BindingBuilder.bind(userConfirmedQueue).to(userExchange).with("user.email.confirmed");
    }

    @Bean
    public JacksonJsonMessageConverter messageConverter() {
        JacksonJsonMessageConverter converter = new JacksonJsonMessageConverter();

        DefaultJacksonJavaTypeMapper typeMapper = new DefaultJacksonJavaTypeMapper();
        typeMapper.setTrustedPackages("*");

        converter.setJavaTypeMapper(typeMapper);

        return converter;
    }
}
