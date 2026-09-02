package com.n4d3sh1k4.billing_service.controller;

import com.n4d3sh1k4.billing_service.dto.SubscriptionResponse;
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
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(excludeAutoConfiguration = DataWebAutoConfiguration.class)
@Import(AdminSubscriptionController.class)
@AutoConfigureMockMvc(addFilters = true)
class AdminSubscriptionControllerTest {

    private static final UUID USER_ID = UUID.fromString("22222222-2222-2222-2222-222222222222");
    private static final UUID TARIFF_ID = UUID.fromString("11111111-1111-1111-1111-111111111111");

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private SubscriptionService subscriptionService;

    private SubscriptionResponse response() {
        return new SubscriptionResponse(
                USER_ID, TARIFF_ID, "PRO",
                Instant.parse("2026-01-01T00:00:00Z"),
                Instant.parse("2026-02-01T00:00:00Z"));
    }

    @Test
    void assignTariff_returns200() throws Exception {
        when(subscriptionService.assignTariff(USER_ID, TARIFF_ID)).thenReturn(response());

        mockMvc.perform(put("/admin/billing/subscriptions/{userId}/tariff/{tariffId}", USER_ID, TARIFF_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.userId").value(USER_ID.toString()))
                .andExpect(jsonPath("$.data.tariffId").value(TARIFF_ID.toString()))
                .andExpect(jsonPath("$.data.tariffName").value("PRO"));

        verify(subscriptionService).assignTariff(USER_ID, TARIFF_ID);
    }

    @Test
    void getSubscription_returns200() throws Exception {
        when(subscriptionService.getSubscription(USER_ID)).thenReturn(response());

        mockMvc.perform(get("/admin/billing/subscriptions/{userId}", USER_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.tariffName").value("PRO"));

        verify(subscriptionService).getSubscription(USER_ID);
    }

    @Test
    void getSubscription_whenNoSubscription_returns404() throws Exception {
        when(subscriptionService.getSubscription(USER_ID)).thenReturn(null);

        mockMvc.perform(get("/admin/billing/subscriptions/{userId}", USER_ID))
                .andExpect(status().isNotFound());

        verify(subscriptionService).getSubscription(USER_ID);
    }
}