package com.n4d3sh1k4.billing_service.service;

import com.n4d3sh1k4.billing_service.domain.model.tariff.Tariff;
import com.n4d3sh1k4.billing_service.domain.model.billing.UsageCounter;
import com.n4d3sh1k4.billing_service.domain.model.billing.UserSubscription;
import com.n4d3sh1k4.billing_service.domain.repository.TariffRepository;
import com.n4d3sh1k4.billing_service.domain.repository.UsageCounterRepository;
import com.n4d3sh1k4.billing_service.domain.repository.UserSubscriptionRepository;
import com.n4d3sh1k4.billing_service.dto.CheckQuotaRequest;
import com.n4d3sh1k4.billing_service.dto.CheckQuotaResponse;
import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import com.n4d3sh1k4.common.exception.PaymentRequiredException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class QuotaService {

    private final UserSubscriptionRepository subscriptionRepository;
    private final UsageCounterRepository usageCounterRepository;
    private final TariffRepository tariffRepository;

    @Transactional
    public CheckQuotaResponse checkQuota(CheckQuotaRequest request) {
        UUID userId = request.getUserId();
        UserSubscription subscription = subscriptionRepository.findByUserId(userId)
                .orElseGet(() -> assignFreeTariff(userId));

        Tariff tariff = tariffRepository.findById(subscription.getTariffId())
                .orElseThrow(() -> new ContentNotFoundException("Tariff not found"));

        int limit = resolveLimit(tariff, request.getFeature());
        if (limit < 0) {
            return new CheckQuotaResponse(isPaidForMonth(subscription, tariff),
                    Integer.MAX_VALUE, -1, 0, tariff.getName());
        }

        if (!isPaidForMonth(subscription, tariff)) {
            return new CheckQuotaResponse(false, 0, limit, 0, tariff.getName());
        }

        Instant now = Instant.now();

        // Monthly rollover: advance the billing period and reset all counters for the user once.
        // A new month requires a new payment, so clear the paid flag.
        if (subscription.getNextResetDate().isBefore(now)) {
            Instant periodStart = rollForward(subscription.getNextResetDate(), now);
            subscription.setNextResetDate(periodStart);
            subscription.setPaid(false);
            subscriptionRepository.save(subscription);
            resetAllCounters(userId, periodStart, tariff);
        }

        UsageCounter counter = usageCounterRepository.findByUserIdAndFeature(userId, request.getFeature())
                .orElseGet(() -> createCounter(userId, request.getFeature(), limit, subscription.getNextResetDate()));

        if (counter.getLimitValue() != limit) {
            counter.setLimitValue(limit);
        }

        int remaining = counter.getLimitValue() - counter.getUsed();
        boolean allowed = remaining >= request.getRequested();
        usageCounterRepository.save(counter);

        log.debug("Quota check for user {} feature {}: {}/{} used -> allowed={}",
                userId, request.getFeature(), counter.getUsed(), counter.getLimitValue(), allowed);

        return new CheckQuotaResponse(allowed, Math.max(remaining, 0), counter.getLimitValue(), counter.getUsed(), tariff.getName());
    }

    @Transactional
    public void incrementUsage(UUID userId, String feature) {
        UserSubscription subscription = subscriptionRepository.findByUserId(userId)
                .orElseGet(() -> assignFreeTariff(userId));
        Tariff tariff = tariffRepository.findById(subscription.getTariffId())
                .orElseThrow(() -> new ContentNotFoundException("Tariff not found"));

        if (!isPaidForMonth(subscription, tariff)) {
            throw new PaymentRequiredException("Payment is required to use this tariff for the current month");
        }

        usageCounterRepository.findByUserIdAndFeature(userId, feature).ifPresent(counter -> {
            counter.setUsed(counter.getUsed() + 1);
            usageCounterRepository.save(counter);
        });
    }

    private boolean isPaidForMonth(UserSubscription subscription, Tariff tariff) {
        // Бесплатные тарифы (cost <= 0) не требуют оплаты.
        return tariff.getCost().compareTo(BigDecimal.ZERO) <= 0 || subscription.isPaid();
    }

    private Instant rollForward(Instant nextResetDate, Instant now) {
        Instant next = nextResetDate;
        while (!next.isAfter(now)) {
            next = next.atZone(ZoneOffset.UTC).plusMonths(1).toInstant();
        }
        return next;
    }

    private void resetAllCounters(UUID userId, Instant periodStart, Tariff tariff) {
        for (UsageCounter counter : usageCounterRepository.findAllByUserId(userId)) {
            counter.setUsed(0);
            counter.setPeriodStart(periodStart);
            counter.setLimitValue(resolveLimit(tariff, counter.getFeature()));
            usageCounterRepository.save(counter);
        }
    }

    private UsageCounter createCounter(UUID userId, String feature, int limit, Instant periodStart) {
        return UsageCounter.builder()
                .userId(userId)
                .feature(feature)
                .used(0)
                .limitValue(limit)
                .periodStart(periodStart)
                .build();
    }

    private UserSubscription assignFreeTariff(UUID userId) {
        Tariff freeTariff = tariffRepository.findByName("FREE")
                .orElseThrow(() -> new ContentNotFoundException("FREE tariff not found"));
        UserSubscription subscription = UserSubscription.builder()
                .userId(userId)
                .tariffId(freeTariff.getId())
                .startDate(Instant.now())
                .nextResetDate(Instant.now().atZone(ZoneOffset.UTC).plusMonths(1).toInstant())
                .paid(true)
                .build();
        subscriptionRepository.save(subscription);
        log.info("Auto-assigned FREE tariff to user {} (no subscription found)", userId);
        return subscription;
    }

    private int resolveLimit(Tariff tariff, String feature) {
        return switch (feature) {
            case "generation" -> tariff.getAiGenerations();
            case "post" -> tariff.getPosts();
            case "project" -> tariff.getProjects();
            default -> 0;
        };
    }
}
