package com.n4d3sh1k4.user_service.config;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.TopicExchange;
import org.springframework.amqp.support.converter.JacksonJsonMessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;



@Configuration
public class RabbitConfig {

    public static final String QUEUE = "user-profile-queue";
    public static final String EXCHANGE = "user-exchange";
    public static final String ROUTING_KEY = "user.created";

    // 1. Создаем очередь
    @Bean
    public Queue queue() {
        return new Queue(QUEUE, true); // true = надежная (не пропадет при рестарте Rabbit)
    }

    // 2. Создаем обменник
    @Bean
    public TopicExchange exchange() {
        return new TopicExchange(EXCHANGE);
    }

    // 3. Связываем их: "Направляй сообщения с ключом user.created в эту очередь"
    @Bean
    public Binding binding(Queue queue, TopicExchange exchange) {
        return BindingBuilder.bind(queue).to(exchange).with(ROUTING_KEY);
    }

    // 4. Тот самый конвертер, чтобы понимать JSON
    @Bean
    public JacksonJsonMessageConverter messageConverter() {
        return new JacksonJsonMessageConverter();
    }
}