package com.n4d3sh1k4.billing_service.controller;

import com.n4d3sh1k4.billing_service.dto.CheckQuotaResponse;
import com.n4d3sh1k4.billing_service.dto.SubscriptionOverview;
import com.n4d3sh1k4.billing_service.service.QuotaService;
import com.n4d3sh1k4.billing_service.service.SubscriptionService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.autoconfigure.web.DataWebAutoConfiguration;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(excludeAutoConfiguration = DataWebAutoConfiguration.class)
@Import(UserQuotaController.class)
@AutoConfigureMockMvc(addFilters = true)
class UserQuotaControllerTest {

    private static final UUID USER_ID = UUID.fromString("22222222-2222-2222-2222-222222222222");
    private static final UUID TARIFF_ID = UUID.fromString("11111111-1111-1111-1111-111111111111");

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private QuotaService quotaService;

    @MockitoBean
    private SubscriptionService subscriptionService;

    private SubscriptionOverview overview() {
        Map<String, SubscriptionOverview.QuotaInfo> quotas = new LinkedHashMap<>();
        quotas.put("project", new SubscriptionOverview.QuotaInfo(1, 0));
        quotas.put("post", new SubscriptionOverview.QuotaInfo(5, 2));
        quotas.put("generation", new SubscriptionOverview.QuotaInfo(10, 1));
        return new SubscriptionOverview(
                USER_ID, TARIFF_ID, "FREE",
                Instant.parse("2026-01-01T00:00:00Z"),
                Instant.parse("2026-02-01T00:00:00Z"),
                quotas);
    }

    @Test
    void getMyQuota_returns200() throws Exception {
        when(quotaService.checkQuota(any())).thenReturn(new CheckQuotaResponse(true, 9, 10, 1, "FREE"));

        mockMvc.perform(get("/quota/me")
                        .with(user(USER_ID.toString())))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.allowed").value(true))
                .andExpect(jsonPath("$.data.remaining").value(9))
                .andExpect(jsonPath("$.data.limit").value(10))
                .andExpect(jsonPath("$.data.used").value(1))
                .andExpect(jsonPath("$.data.tariffName").value("FREE"));

        verify(quotaService).checkQuota(any());
    }

    @Test
    void getMyTariff_returns200() throws Exception {
        when(subscriptionService.getSubscriptionOverview(USER_ID)).thenReturn(overview());

        mockMvc.perform(get("/quota/me/tariff")
                        .with(user(USER_ID.toString())))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.userId").value(USER_ID.toString()))
                .andExpect(jsonPath("$.data.tariffName").value("FREE"))
                .andExpect(jsonPath("$.data.quotas.project.limit").value(1))
                .andExpect(jsonPath("$.data.quotas.post.used").value(2));

        verify(subscriptionService).getSubscriptionOverview(USER_ID);
    }

    @Test
    void getMyTariff_whenNoSubscription_returns404() throws Exception {
        when(subscriptionService.getSubscriptionOverview(USER_ID)).thenReturn(null);

        mockMvc.perform(get("/quota/me/tariff")
                        .with(user(USER_ID.toString())))
                .andExpect(status().isNotFound());

        verify(subscriptionService).getSubscriptionOverview(USER_ID);
    }

    @Test
    void purchase_returns200() throws Exception {
        when(subscriptionService.purchaseTariff(eq(USER_ID), eq(TARIFF_ID))).thenReturn(overview());

        mockMvc.perform(post("/quota/me/purchase")
                        .with(user(USER_ID.toString()))
                        .contentType("application/json")
                        .content("{\"tariffId\": \"" + TARIFF_ID + "\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.tariffName").value("FREE"));

        verify(subscriptionService).purchaseTariff(USER_ID, TARIFF_ID);
    }

    @Test
    void purchase_whenTariffIdMissing_returns400() throws Exception {
        mockMvc.perform(post("/quota/me/purchase")
                        .with(user(USER_ID.toString()))
                        .contentType("application/json")
                        .content("{}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("VALIDATION_ERROR"));

        verify(subscriptionService, never()).purchaseTariff(any(), any());
    }
}