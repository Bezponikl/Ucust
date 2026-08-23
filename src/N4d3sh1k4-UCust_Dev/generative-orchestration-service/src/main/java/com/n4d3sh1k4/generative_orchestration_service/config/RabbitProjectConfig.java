package com.n4d3sh1k4.generative_orchestration_service.config;

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
public class RabbitProjectConfig {

    public static final String PROJECT_QUEUE = "project-generation-queue";
    public static final String PROJECT_DLQ = PROJECT_QUEUE + ".dlq";
    public static final String DLX = "user-exchange.dlx";

    @Bean
    public Queue projectQueue() {
        Map<String, Object> args = new HashMap<>();
        args.put("x-dead-letter-exchange", DLX);
        args.put("x-dead-letter-routing-key", PROJECT_DLQ);
        return new Queue(PROJECT_QUEUE, true, false, false, args);
    }

    @Bean
    public Queue projectDlq() {
        return new Queue(PROJECT_DLQ, true);
    }

    @Bean
    public TopicExchange dlx() {
        return new TopicExchange(DLX);
    }

    @Bean
    public Binding projectDlqBinding(Queue projectDlq, TopicExchange dlx) {
        return BindingBuilder.bind(projectDlq).to(dlx).with(PROJECT_DLQ);
    }

    @Bean
    public TopicExchange projectExchange() {
        return new TopicExchange("user-exchange");
    }

    @Bean
    public Binding projectBinding(Queue projectQueue, TopicExchange projectExchange) {
        return BindingBuilder.bind(projectQueue).to(projectExchange).with("project.created");
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
