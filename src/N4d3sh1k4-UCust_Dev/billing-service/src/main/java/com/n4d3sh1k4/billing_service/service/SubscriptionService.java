package com.n4d3sh1k4.billing_service.service;

import com.n4d3sh1k4.billing_service.domain.model.billing.UserSubscription;
import com.n4d3sh1k4.billing_service.domain.model.tariff.Tariff;
import com.n4d3sh1k4.billing_service.domain.repository.TariffRepository;
import com.n4d3sh1k4.billing_service.domain.repository.UsageCounterRepository;
import com.n4d3sh1k4.billing_service.domain.repository.UserSubscriptionRepository;
import com.n4d3sh1k4.billing_service.dto.SubscriptionOverview;
import com.n4d3sh1k4.billing_service.dto.SubscriptionResponse;
import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class SubscriptionService {

    private final UserSubscriptionRepository subscriptionRepository;
    private final TariffRepository tariffRepository;
    private final UsageCounterRepository usageCounterRepository;

    @Transactional
    public void assignFreeTariff(UUID userId) {
        if (subscriptionRepository.findByUserId(userId).isPresent()) {
            log.info("User {} already has a subscription, skipping", userId);
            return;
        }

        Tariff freeTariff = tariffRepository.findByName("FREE")
                .orElseThrow(() -> new ContentNotFoundException("FREE tariff not found"));

        UserSubscription subscription = UserSubscription.builder()
                .userId(userId)
                .tariffId(freeTariff.getId())
                .startDate(Instant.now())
                .nextResetDate(Instant.now().plus(1, ChronoUnit.MONTHS))
                .paid(true)
                .build();

        subscriptionRepository.save(subscription);
        log.info("Assigned FREE tariff to user {}", userId);
    }

    @Transactional
    public SubscriptionResponse assignTariff(UUID userId, UUID tariffId) {
        Tariff tariff = tariffRepository.findById(tariffId)
                .orElseThrow(() -> new ContentNotFoundException("Tariff not found"));

        UserSubscription subscription = subscriptionRepository.findByUserId(userId)
                .orElseGet(UserSubscription::new);
        subscription.setUserId(userId);
        subscription.setTariffId(tariff.getId());
        subscription.setStartDate(Instant.now());
        subscription.setNextResetDate(Instant.now().plus(1, ChronoUnit.MONTHS));
        subscription.setPaid(true);
        subscriptionRepository.save(subscription);

        resetUsageCounters(userId);
        log.info("Assigned tariff {} to user {}", tariff.getName(), userId);

        return toResponse(subscription, tariff);
    }

    @Transactional
    public SubscriptionOverview purchaseTariff(UUID userId, UUID tariffId) {
        Tariff tariff = tariffRepository.findById(tariffId)
                .orElseThrow(() -> new ContentNotFoundException("Tariff not found"));

        // Заглушка: здесь будет вызов интегрированного платёжного провайдера.
        // Сейчас покупка сразу считается успешной (mock success).
        log.info("MOCK purchase: user {} buys tariff {}", userId, tariff.getName());

        UserSubscription subscription = subscriptionRepository.findByUserId(userId)
                .orElseGet(UserSubscription::new);
        subscription.setUserId(userId);
        subscription.setTariffId(tariff.getId());
        subscription.setStartDate(Instant.now());
        subscription.setNextResetDate(Instant.now().plus(1, ChronoUnit.MONTHS));
        subscription.setPaid(true);
        subscriptionRepository.save(subscription);

        resetUsageCounters(userId);
        log.info("User {} activated tariff {} for the current month", userId, tariff.getName());

        Tariff effectiveTariff = tariff;
        return new SubscriptionOverview(
                subscription.getUserId(),
                subscription.getTariffId(),
                effectiveTariff.getName(),
                subscription.getStartDate(),
                subscription.getNextResetDate(),
                quotasOf(userId, effectiveTariff)
        );
    }

    private Map<String, SubscriptionOverview.QuotaInfo> quotasOf(UUID userId, Tariff tariff) {
        Map<String, Integer> usedByFeature = new LinkedHashMap<>();
        usageCounterRepository.findAllByUserId(userId).forEach(counter ->
                usedByFeature.put(counter.getFeature(), counter.getUsed()));

        Map<String, SubscriptionOverview.QuotaInfo> quotas = new LinkedHashMap<>();
        quotas.put("project", quotaOf(usedByFeature, "project", tariff.getProjects()));
        quotas.put("post", quotaOf(usedByFeature, "post", tariff.getPosts()));
        quotas.put("generation", quotaOf(usedByFeature, "generation", tariff.getAiGenerations()));
        return quotas;
    }

    @Transactional(readOnly = true)
    public SubscriptionResponse getSubscription(UUID userId) {
        UserSubscription subscription = subscriptionRepository.findByUserId(userId)
                .orElse(null);
        if (subscription == null) {
            return null;
        }
        Tariff tariff = tariffRepository.findById(subscription.getTariffId())
                .orElse(null);
        return toResponse(subscription, tariff);
    }

    @Transactional(readOnly = true)
    public SubscriptionOverview getSubscriptionOverview(UUID userId) {
        UserSubscription subscription = subscriptionRepository.findByUserId(userId)
                .orElse(null);
        if (subscription == null) {
            return null;
        }
        Tariff tariff = tariffRepository.findById(subscription.getTariffId())
                .orElseThrow(() -> new ContentNotFoundException("Tariff not found"));

        return new SubscriptionOverview(
                subscription.getUserId(),
                subscription.getTariffId(),
                tariff.getName(),
                subscription.getStartDate(),
                subscription.getNextResetDate(),
                quotasOf(userId, tariff)
        );
    }

    private SubscriptionOverview.QuotaInfo quotaOf(Map<String, Integer> usedByFeature, String feature, int limit) {
        return new SubscriptionOverview.QuotaInfo(limit, usedByFeature.getOrDefault(feature, 0));
    }

    private void resetUsageCounters(UUID userId) {
        Instant now = Instant.now();
        usageCounterRepository.findAllByUserId(userId).forEach(counter -> {
            counter.setUsed(0);
            counter.setPeriodStart(now);
            usageCounterRepository.save(counter);
        });
    }

    private SubscriptionResponse toResponse(UserSubscription subscription, Tariff tariff) {
        return new SubscriptionResponse(
                subscription.getUserId(),
                subscription.getTariffId(),
                tariff != null ? tariff.getName() : null,
                subscription.getStartDate(),
                subscription.getNextResetDate()
        );
    }
}
