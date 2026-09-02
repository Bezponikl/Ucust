package com.n4d3sh1k4.billing_service.service;

import com.n4d3sh1k4.billing_service.domain.model.billing.UsageCounter;
import com.n4d3sh1k4.billing_service.domain.model.billing.UserSubscription;
import com.n4d3sh1k4.billing_service.domain.model.tariff.AnalyticsType;
import com.n4d3sh1k4.billing_service.domain.model.tariff.ChatBotType;
import com.n4d3sh1k4.billing_service.domain.model.tariff.SupportType;
import com.n4d3sh1k4.billing_service.domain.model.tariff.Tariff;
import com.n4d3sh1k4.billing_service.domain.repository.TariffRepository;
import com.n4d3sh1k4.billing_service.domain.repository.UsageCounterRepository;
import com.n4d3sh1k4.billing_service.domain.repository.UserSubscriptionRepository;
import com.n4d3sh1k4.billing_service.dto.CheckQuotaRequest;
import com.n4d3sh1k4.billing_service.dto.CheckQuotaResponse;
import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import com.n4d3sh1k4.common.exception.PaymentRequiredException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class QuotaServiceTest {

    private static final UUID USER_ID = UUID.fromString("22222222-2222-2222-2222-222222222222");
    private static final UUID FREE_ID = UUID.fromString("33333333-3333-3333-3333-333333333333");
    private static final UUID PRO_ID = UUID.fromString("44444444-4444-4444-4444-444444444444");

    @Mock
    private UserSubscriptionRepository subscriptionRepository;

    @Mock
    private UsageCounterRepository usageCounterRepository;

    @Mock
    private TariffRepository tariffRepository;

    @InjectMocks
    private QuotaService quotaService;

    private Tariff freeTariff() {
        return Tariff.builder()
                .id(FREE_ID)
                .name("FREE")
                .cost(BigDecimal.ZERO)
                .projects(1)
                .posts(5)
                .chatBotType(ChatBotType.NONE)
                .supportType(SupportType.NONE)
                .analyticsType(AnalyticsType.NONE)
                .aiGenerations(10)
                .build();
    }

    private Tariff paidTariff() {
        return Tariff.builder()
                .id(PRO_ID)
                .name("PRO")
                .cost(new BigDecimal("29.99"))
                .projects(5)
                .posts(50)
                .chatBotType(ChatBotType.ADVANCED)
                .supportType(SupportType.CHAT)
                .analyticsType(AnalyticsType.PRO)
                .aiGenerations(100)
                .build();
    }

    private UserSubscription subscription() {
        return UserSubscription.builder()
                .userId(USER_ID)
                .tariffId(FREE_ID)
                .startDate(Instant.now())
                .nextResetDate(Instant.now().atZone(ZoneOffset.UTC).plusMonths(1).toInstant())
                .paid(true)
                .build();
    }

    private CheckQuotaRequest request(String feature, int requested) {
        CheckQuotaRequest request = new CheckQuotaRequest();
        request.setUserId(USER_ID);
        request.setFeature(feature);
        request.setRequested(requested);
        return request;
    }

    @Test
    void checkQuota_whenNoSubscription_autoAssignsFreeTariffAndAllows() {
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.empty());
        when(tariffRepository.findByName("FREE")).thenReturn(Optional.of(freeTariff()));
        when(subscriptionRepository.save(any(UserSubscription.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));
        when(tariffRepository.findById(FREE_ID)).thenReturn(Optional.of(freeTariff()));
        when(usageCounterRepository.findByUserIdAndFeature(USER_ID, "project")).thenReturn(Optional.empty());
        when(usageCounterRepository.save(any(UsageCounter.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));

        CheckQuotaResponse response = quotaService.checkQuota(request("project", 1));

        assertThat(response.allowed()).isTrue();
        assertThat(response.remaining()).isEqualTo(1);
        assertThat(response.limit()).isEqualTo(1);
        assertThat(response.used()).isZero();
        assertThat(response.tariffName()).isEqualTo("FREE");

        ArgumentCaptor<UserSubscription> captor = ArgumentCaptor.forClass(UserSubscription.class);
        verify(subscriptionRepository).save(captor.capture());
        assertThat(captor.getValue().getTariffId()).isEqualTo(FREE_ID);
        assertThat(captor.getValue().isPaid()).isTrue();
    }

    @Test
    void checkQuota_whenLimitNegative_returnsUnlimited() {
        Tariff enterprise = Tariff.builder()
                .id(PRO_ID)
                .name("ENTERPRISE")
                .cost(new BigDecimal("99.99"))
                .projects(-1)
                .posts(-1)
                .chatBotType(ChatBotType.CUSTOM)
                .supportType(SupportType.PRIORITY)
                .analyticsType(AnalyticsType.ENTERPRISE)
                .aiGenerations(-1)
                .build();
        UserSubscription subscription = subscription();
        subscription.setTariffId(PRO_ID);
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.of(subscription));
        when(tariffRepository.findById(PRO_ID)).thenReturn(Optional.of(enterprise));

        CheckQuotaResponse response = quotaService.checkQuota(request("project", 1));

        assertThat(response.limit()).isEqualTo(-1);
        assertThat(response.remaining()).isEqualTo(Integer.MAX_VALUE);
        assertThat(response.allowed()).isTrue();
        assertThat(response.tariffName()).isEqualTo("ENTERPRISE");
    }

    @Test
    void checkQuota_whenNotPaid_returnsDenied() {
        UserSubscription unpaid = subscription();
        unpaid.setTariffId(PRO_ID);
        unpaid.setPaid(false);
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.of(unpaid));
        when(tariffRepository.findById(PRO_ID)).thenReturn(Optional.of(paidTariff()));

        CheckQuotaResponse response = quotaService.checkQuota(request("project", 1));

        assertThat(response.allowed()).isFalse();
        assertThat(response.remaining()).isZero();
        assertThat(response.limit()).isEqualTo(5);
        assertThat(response.used()).isZero();
    }

    @Test
    void checkQuota_whenMonthRollover_resetsCountersAndMarksUnpaid() {
        UserSubscription subscription = subscription();
        subscription.setTariffId(PRO_ID);
        subscription.setNextResetDate(Instant.now().minus(1, java.time.temporal.ChronoUnit.DAYS));
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.of(subscription));
        when(tariffRepository.findById(PRO_ID)).thenReturn(Optional.of(paidTariff()));
        UsageCounter counter = UsageCounter.builder()
                .userId(USER_ID).feature("post").used(7).limitValue(50)
                .periodStart(Instant.now().minus(30, java.time.temporal.ChronoUnit.DAYS)).build();
        when(usageCounterRepository.findAllByUserId(USER_ID)).thenReturn(List.of(counter));
        when(usageCounterRepository.findByUserIdAndFeature(USER_ID, "project")).thenReturn(Optional.empty());
        when(usageCounterRepository.save(any(UsageCounter.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));

        CheckQuotaResponse response = quotaService.checkQuota(request("project", 1));

        assertThat(response.allowed()).isTrue();
        assertThat(response.limit()).isEqualTo(5);
        assertThat(response.used()).isZero();

        ArgumentCaptor<UserSubscription> captor = ArgumentCaptor.forClass(UserSubscription.class);
        verify(subscriptionRepository).save(captor.capture());
        assertThat(captor.getValue().isPaid()).isFalse();
        assertThat(captor.getValue().getNextResetDate()).isAfter(Instant.now());

        ArgumentCaptor<UsageCounter> counterCaptor = ArgumentCaptor.forClass(UsageCounter.class);
        verify(usageCounterRepository, org.mockito.Mockito.times(2)).save(counterCaptor.capture());
        UsageCounter resetCounter = counterCaptor.getAllValues().stream()
                .filter(c -> "post".equals(c.getFeature()))
                .findFirst().orElseThrow();
        assertThat(resetCounter.getUsed()).isZero();
        assertThat(resetCounter.getLimitValue()).isEqualTo(50);
        assertThat(counterCaptor.getAllValues()).anyMatch(c -> "project".equals(c.getFeature()));
    }

    @Test
    void checkQuota_whenExistingCounter_updatesLimitAndComputesRemaining() {
        Tariff twentyProjects = Tariff.builder()
                .id(PRO_ID)
                .name("PRO")
                .cost(new BigDecimal("29.99"))
                .projects(20)
                .posts(50)
                .chatBotType(ChatBotType.ADVANCED)
                .supportType(SupportType.CHAT)
                .analyticsType(AnalyticsType.PRO)
                .aiGenerations(100)
                .build();
        UserSubscription subscription = subscription();
        subscription.setTariffId(PRO_ID);
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.of(subscription));
        when(tariffRepository.findById(PRO_ID)).thenReturn(Optional.of(twentyProjects));
        UsageCounter counter = UsageCounter.builder()
                .userId(USER_ID).feature("project").used(3).limitValue(10)
                .periodStart(Instant.now()).build();
        when(usageCounterRepository.findByUserIdAndFeature(USER_ID, "project")).thenReturn(Optional.of(counter));

        CheckQuotaResponse response = quotaService.checkQuota(request("project", 1));

        assertThat(response.allowed()).isTrue();
        assertThat(response.remaining()).isEqualTo(17);
        assertThat(response.limit()).isEqualTo(20);
        assertThat(response.used()).isEqualTo(3);

        ArgumentCaptor<UsageCounter> captor = ArgumentCaptor.forClass(UsageCounter.class);
        verify(usageCounterRepository).save(captor.capture());
        assertThat(captor.getValue().getLimitValue()).isEqualTo(20);
    }

    @Test
    void checkQuota_whenInsufficient_returnsDenied() {
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.of(subscription()));
        when(tariffRepository.findById(FREE_ID)).thenReturn(Optional.of(freeTariff()));
        UsageCounter counter = UsageCounter.builder()
                .userId(USER_ID).feature("project").used(1).limitValue(1)
                .periodStart(Instant.now()).build();
        when(usageCounterRepository.findByUserIdAndFeature(USER_ID, "project")).thenReturn(Optional.of(counter));

        CheckQuotaResponse response = quotaService.checkQuota(request("project", 2));

        assertThat(response.allowed()).isFalse();
        assertThat(response.remaining()).isZero();
        assertThat(response.limit()).isEqualTo(1);
        assertThat(response.used()).isEqualTo(1);
    }

    @Test
    void checkQuota_whenTariffNotFound_throwsContentNotFound() {
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.of(subscription()));
        when(tariffRepository.findById(FREE_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> quotaService.checkQuota(request("project", 1)))
                .isInstanceOf(ContentNotFoundException.class);
    }

    @Test
    void incrementUsage_incrementsCounter() {
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.of(subscription()));
        when(tariffRepository.findById(FREE_ID)).thenReturn(Optional.of(freeTariff()));
        UsageCounter counter = UsageCounter.builder()
                .userId(USER_ID).feature("post").used(2).limitValue(5)
                .periodStart(Instant.now()).build();
        when(usageCounterRepository.findByUserIdAndFeature(USER_ID, "post")).thenReturn(Optional.of(counter));

        quotaService.incrementUsage(USER_ID, "post");

        ArgumentCaptor<UsageCounter> captor = ArgumentCaptor.forClass(UsageCounter.class);
        verify(usageCounterRepository).save(captor.capture());
        assertThat(captor.getValue().getUsed()).isEqualTo(3);
    }

    @Test
    void incrementUsage_whenNotPaid_throwsPaymentRequired() {
        UserSubscription unpaid = subscription();
        unpaid.setTariffId(PRO_ID);
        unpaid.setPaid(false);
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.of(unpaid));
        when(tariffRepository.findById(PRO_ID)).thenReturn(Optional.of(paidTariff()));

        assertThatThrownBy(() -> quotaService.incrementUsage(USER_ID, "post"))
                .isInstanceOf(PaymentRequiredException.class);
    }

    @Test
    void incrementUsage_whenNoCounter_doesNothing() {
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.of(subscription()));
        when(tariffRepository.findById(FREE_ID)).thenReturn(Optional.of(freeTariff()));
        when(usageCounterRepository.findByUserIdAndFeature(USER_ID, "post")).thenReturn(Optional.empty());

        quotaService.incrementUsage(USER_ID, "post");

        verify(usageCounterRepository, never()).save(any());
    }
}