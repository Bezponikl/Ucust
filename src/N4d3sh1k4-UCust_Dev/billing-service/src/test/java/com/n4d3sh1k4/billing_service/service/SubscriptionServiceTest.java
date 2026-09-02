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
import com.n4d3sh1k4.billing_service.dto.SubscriptionOverview;
import com.n4d3sh1k4.billing_service.dto.SubscriptionResponse;
import com.n4d3sh1k4.common.exception.ContentNotFoundException;
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
import java.util.Map;
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
class SubscriptionServiceTest {

    private static final UUID USER_ID = UUID.fromString("22222222-2222-2222-2222-222222222222");
    private static final UUID FREE_ID = UUID.fromString("33333333-3333-3333-3333-333333333333");
    private static final UUID PRO_ID = UUID.fromString("44444444-4444-4444-4444-444444444444");

    @Mock
    private UserSubscriptionRepository subscriptionRepository;

    @Mock
    private TariffRepository tariffRepository;

    @Mock
    private UsageCounterRepository usageCounterRepository;

    @InjectMocks
    private SubscriptionService subscriptionService;

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

    private Tariff proTariff() {
        return Tariff.builder()
                .id(PRO_ID)
                .name("PRO")
                .cost(new BigDecimal("29.99"))
                .projects(10)
                .posts(200)
                .chatBotType(ChatBotType.ADVANCED)
                .supportType(SupportType.CHAT)
                .analyticsType(AnalyticsType.PRO)
                .aiGenerations(500)
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

    @Test
    void assignFreeTariff_whenNoSubscription_createsFreeSubscription() {
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.empty());
        when(tariffRepository.findByName("FREE")).thenReturn(Optional.of(freeTariff()));
        when(subscriptionRepository.save(any(UserSubscription.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));

        subscriptionService.assignFreeTariff(USER_ID);

        ArgumentCaptor<UserSubscription> captor = ArgumentCaptor.forClass(UserSubscription.class);
        verify(subscriptionRepository).save(captor.capture());

        UserSubscription saved = captor.getValue();
        assertThat(saved.getUserId()).isEqualTo(USER_ID);
        assertThat(saved.getTariffId()).isEqualTo(FREE_ID);
        assertThat(saved.isPaid()).isTrue();
        assertThat(saved.getNextResetDate()).isAfter(Instant.now());
    }

    @Test
    void assignFreeTariff_whenSubscriptionExists_skips() {
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.of(subscription()));

        subscriptionService.assignFreeTariff(USER_ID);

        verify(subscriptionRepository, never()).save(any());
        verify(tariffRepository, never()).findByName("FREE");
    }

    @Test
    void assignFreeTariff_whenFreeTariffMissing_throwsContentNotFound() {
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.empty());
        when(tariffRepository.findByName("FREE")).thenReturn(Optional.empty());

        assertThatThrownBy(() -> subscriptionService.assignFreeTariff(USER_ID))
                .isInstanceOf(ContentNotFoundException.class);
    }

    @Test
    void assignTariff_whenNoExistingSubscription_createsNew() {
        when(tariffRepository.findById(PRO_ID)).thenReturn(Optional.of(proTariff()));
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.empty());
        when(subscriptionRepository.save(any(UserSubscription.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));
        when(usageCounterRepository.findAllByUserId(USER_ID)).thenReturn(List.of());

        SubscriptionResponse response = subscriptionService.assignTariff(USER_ID, PRO_ID);

        assertThat(response.userId()).isEqualTo(USER_ID);
        assertThat(response.tariffId()).isEqualTo(PRO_ID);
        assertThat(response.tariffName()).isEqualTo("PRO");

        ArgumentCaptor<UserSubscription> captor = ArgumentCaptor.forClass(UserSubscription.class);
        verify(subscriptionRepository).save(captor.capture());
        assertThat(captor.getValue().getTariffId()).isEqualTo(PRO_ID);
    }

    @Test
    void assignTariff_whenExistingSubscription_updates() {
        when(tariffRepository.findById(PRO_ID)).thenReturn(Optional.of(proTariff()));
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.of(subscription()));
        when(usageCounterRepository.findAllByUserId(USER_ID)).thenReturn(List.of());

        SubscriptionResponse response = subscriptionService.assignTariff(USER_ID, PRO_ID);

        assertThat(response.tariffId()).isEqualTo(PRO_ID);

        ArgumentCaptor<UserSubscription> captor = ArgumentCaptor.forClass(UserSubscription.class);
        verify(subscriptionRepository).save(captor.capture());
        assertThat(captor.getValue().getTariffId()).isEqualTo(PRO_ID);
    }

    @Test
    void assignTariff_whenTariffNotFound_throwsContentNotFound() {
        when(tariffRepository.findById(PRO_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> subscriptionService.assignTariff(USER_ID, PRO_ID))
                .isInstanceOf(ContentNotFoundException.class);
    }

    @Test
    void purchaseTariff_returnsOverviewWithQuotas() {
        when(tariffRepository.findById(PRO_ID)).thenReturn(Optional.of(proTariff()));
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.of(subscription()));
        when(usageCounterRepository.findAllByUserId(USER_ID))
                .thenReturn(List.of())
                .thenReturn(List.of(
                        UsageCounter.builder().userId(USER_ID).feature("post").used(3).limitValue(200).build(),
                        UsageCounter.builder().userId(USER_ID).feature("project").used(1).limitValue(10).build()
                ));

        SubscriptionOverview overview = subscriptionService.purchaseTariff(USER_ID, PRO_ID);

        assertThat(overview.userId()).isEqualTo(USER_ID);
        assertThat(overview.tariffName()).isEqualTo("PRO");

        Map<String, SubscriptionOverview.QuotaInfo> quotas = overview.quotas();
        assertThat(quotas.get("project").limit()).isEqualTo(10);
        assertThat(quotas.get("post").limit()).isEqualTo(200);
        assertThat(quotas.get("post").used()).isEqualTo(3);
        assertThat(quotas.get("generation").limit()).isEqualTo(500);
        assertThat(quotas.get("generation").used()).isZero();
    }

    @Test
    void purchaseTariff_whenTariffNotFound_throwsContentNotFound() {
        when(tariffRepository.findById(PRO_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> subscriptionService.purchaseTariff(USER_ID, PRO_ID))
                .isInstanceOf(ContentNotFoundException.class);
    }

    @Test
    void getSubscription_whenFound_returnsResponse() {
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.of(subscription()));
        when(tariffRepository.findById(FREE_ID)).thenReturn(Optional.of(freeTariff()));

        SubscriptionResponse response = subscriptionService.getSubscription(USER_ID);

        assertThat(response.userId()).isEqualTo(USER_ID);
        assertThat(response.tariffName()).isEqualTo("FREE");
    }

    @Test
    void getSubscription_whenNoSubscription_returnsNull() {
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.empty());

        assertThat(subscriptionService.getSubscription(USER_ID)).isNull();
    }

    @Test
    void getSubscriptionOverview_whenFound_returnsOverviewWithQuotas() {
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.of(subscription()));
        when(tariffRepository.findById(FREE_ID)).thenReturn(Optional.of(freeTariff()));
        when(usageCounterRepository.findAllByUserId(USER_ID)).thenReturn(List.of());

        SubscriptionOverview overview = subscriptionService.getSubscriptionOverview(USER_ID);

        assertThat(overview.tariffName()).isEqualTo("FREE");
        assertThat(overview.quotas().get("project").limit()).isEqualTo(1);
        assertThat(overview.quotas().get("post").limit()).isEqualTo(5);
        assertThat(overview.quotas().get("generation").limit()).isEqualTo(10);
    }

    @Test
    void getSubscriptionOverview_whenNoSubscription_returnsNull() {
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.empty());

        assertThat(subscriptionService.getSubscriptionOverview(USER_ID)).isNull();
    }

    @Test
    void getSubscriptionOverview_whenTariffMissing_throwsContentNotFound() {
        when(subscriptionRepository.findByUserId(USER_ID)).thenReturn(Optional.of(subscription()));
        when(tariffRepository.findById(FREE_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> subscriptionService.getSubscriptionOverview(USER_ID))
                .isInstanceOf(ContentNotFoundException.class);
    }
}