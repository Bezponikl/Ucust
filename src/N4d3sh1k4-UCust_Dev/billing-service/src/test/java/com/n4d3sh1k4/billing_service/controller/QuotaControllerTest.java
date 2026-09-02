package com.n4d3sh1k4.billing_service.controller;

import com.n4d3sh1k4.billing_service.dto.CheckQuotaResponse;
import com.n4d3sh1k4.billing_service.service.QuotaService;
import com.n4d3sh1k4.common.exception.PaymentRequiredException;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.autoconfigure.web.DataWebAutoConfiguration;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(excludeAutoConfiguration = DataWebAutoConfiguration.class)
@Import(QuotaController.class)
@AutoConfigureMockMvc(addFilters = true)
class QuotaControllerTest {

    private static final UUID USER_ID = UUID.fromString("22222222-2222-2222-2222-222222222222");

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private QuotaService quotaService;

    @Test
    void checkQuota_returns200() throws Exception {
        when(quotaService.checkQuota(any())).thenReturn(new CheckQuotaResponse(true, 4, 5, 1, "FREE"));

        mockMvc.perform(post("/internal/quota/check")
                        .contentType("application/json")
                        .content("{\"userId\": \"" + USER_ID + "\", \"feature\": \"post\", \"requested\": 1}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.allowed").value(true))
                .andExpect(jsonPath("$.data.limit").value(5))
                .andExpect(jsonPath("$.data.used").value(1));

        verify(quotaService).checkQuota(any());
    }

    @Test
    void checkQuota_whenFeatureBlank_returns400() throws Exception {
        mockMvc.perform(post("/internal/quota/check")
                        .contentType("application/json")
                        .content("{\"userId\": \"" + USER_ID + "\", \"feature\": \"\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("VALIDATION_ERROR"));

        verify(quotaService, never()).checkQuota(any());
    }

    @Test
    void incrementUsage_returns200() throws Exception {
        mockMvc.perform(post("/internal/quota/use/{userId}/{feature}", USER_ID, "post"))
                .andExpect(status().isOk());

        verify(quotaService).incrementUsage(USER_ID, "post");
    }

    @Test
    void incrementUsage_whenNotPaid_returns402() throws Exception {
        org.mockito.Mockito.doThrow(new PaymentRequiredException("Payment is required to use this tariff for the current month"))
                .when(quotaService).incrementUsage(USER_ID, "post");

        mockMvc.perform(post("/internal/quota/use/{userId}/{feature}", USER_ID, "post"))
                .andExpect(status().isPaymentRequired())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.error.code").value("PAYMENT_REQUIRED"));

        verify(quotaService).incrementUsage(USER_ID, "post");
    }
}