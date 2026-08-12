package com.n4d3sh1k4.billing_service.config;

import com.n4d3sh1k4.billing_service.domain.model.tariff.*;
import com.n4d3sh1k4.billing_service.domain.repository.TariffRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;

@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {

    private final TariffRepository tariffRepository;

    @Override
    public void run(String... args) {
        if (tariffRepository.count() > 0) {
            return;
        }

        log.info("Seeding initial tariffs...");

        tariffRepository.save(Tariff.builder()
                .name("FREE")
                .cost(BigDecimal.ZERO)
                .projects(1)
                .posts(5)
                .chatBotType(ChatBotType.NONE)
                .supportType(SupportType.NONE)
                .analyticsType(AnalyticsType.NONE)
                .aiGenerations(10)
                .build());

        tariffRepository.save(Tariff.builder()
                .name("STARTER")
                .cost(new BigDecimal("9.99"))
                .projects(3)
                .posts(30)
                .chatBotType(ChatBotType.BASIC)
                .supportType(SupportType.EMAIL)
                .analyticsType(AnalyticsType.BASIC)
                .aiGenerations(100)
                .build());

        tariffRepository.save(Tariff.builder()
                .name("PRO")
                .cost(new BigDecimal("29.99"))
                .projects(10)
                .posts(200)
                .chatBotType(ChatBotType.ADVANCED)
                .supportType(SupportType.CHAT)
                .analyticsType(AnalyticsType.PRO)
                .aiGenerations(500)
                .build());

        tariffRepository.save(Tariff.builder()
                .name("ENTERPRISE")
                .cost(new BigDecimal("99.99"))
                .projects(-1)
                .posts(-1)
                .chatBotType(ChatBotType.CUSTOM)
                .supportType(SupportType.PRIORITY)
                .analyticsType(AnalyticsType.ENTERPRISE)
                .aiGenerations(-1)
                .build());

        log.info("Initial tariffs seeded");
    }
}
