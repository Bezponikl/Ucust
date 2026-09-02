package com.n4d3sh1k4.billing_service.controller;

import com.n4d3sh1k4.billing_service.domain.model.tariff.AnalyticsType;
import com.n4d3sh1k4.billing_service.domain.model.tariff.ChatBotType;
import com.n4d3sh1k4.billing_service.domain.model.tariff.SupportType;
import com.n4d3sh1k4.billing_service.dto.TariffResponse;
import com.n4d3sh1k4.billing_service.service.TariffService;
import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.autoconfigure.web.DataWebAutoConfiguration;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(excludeAutoConfiguration = DataWebAutoConfiguration.class)
@Import(TariffController.class)
@AutoConfigureMockMvc(addFilters = true)
class TariffControllerTest {

    private static final UUID TARIFF_ID = UUID.fromString("11111111-1111-1111-1111-111111111111");

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private TariffService tariffService;

    private TariffResponse response() {
        return new TariffResponse(
                TARIFF_ID, "PRO", new BigDecimal("29.99"), 10, 200,
                ChatBotType.ADVANCED, SupportType.CHAT, AnalyticsType.PRO, 500);
    }

    private String validCreateJson() {
        return "{"
                + "\"name\": \"PRO\","
                + "\"cost\": 29.99,"
                + "\"projects\": 10,"
                + "\"posts\": 200,"
                + "\"chatBotType\": \"ADVANCED\","
                + "\"supportType\": \"CHAT\","
                + "\"analyticsType\": \"PRO\","
                + "\"aiGenerations\": 500"
                + "}";
    }

    @Test
    void getAllTariffs_returns200List() throws Exception {
        when(tariffService.getAllTariffs()).thenReturn(List.of(response()));

        mockMvc.perform(get("/tariffs"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data").isArray())
                .andExpect(jsonPath("$.data[0].name").value("PRO"))
                .andExpect(jsonPath("$.data[0].cost").value(29.99))
                .andExpect(jsonPath("$.data[0].aiGenerations").value(500));

        verify(tariffService).getAllTariffs();
    }

    @Test
    void getTariff_returns200() throws Exception {
        when(tariffService.getTariff(TARIFF_ID)).thenReturn(response());

        mockMvc.perform(get("/tariffs/{id}", TARIFF_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.id").value(TARIFF_ID.toString()))
                .andExpect(jsonPath("$.data.chatBotType").value("ADVANCED"))
                .andExpect(jsonPath("$.data.supportType").value("CHAT"))
                .andExpect(jsonPath("$.data.analyticsType").value("PRO"));

        verify(tariffService).getTariff(TARIFF_ID);
    }

    @Test
    void getTariff_whenNotFound_returns404() throws Exception {
        when(tariffService.getTariff(TARIFF_ID))
                .thenThrow(new ContentNotFoundException("Tariff not found"));

        mockMvc.perform(get("/tariffs/{id}", TARIFF_ID))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.error.code").value("NOT_FOUND"));

        verify(tariffService).getTariff(TARIFF_ID);
    }

    @Test
    void createTariff_validRequest_returns201() throws Exception {
        when(tariffService.createTariff(any())).thenReturn(response());

        mockMvc.perform(post("/tariffs")
                        .contentType("application/json")
                        .content(validCreateJson()))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.id").value(TARIFF_ID.toString()))
                .andExpect(jsonPath("$.data.name").value("PRO"));

        verify(tariffService).createTariff(any());
    }

    @Test
    void createTariff_whenNameBlank_returns400() throws Exception {
        mockMvc.perform(post("/tariffs")
                        .contentType("application/json")
                        .content("{"
                                + "\"cost\": 29.99,"
                                + "\"chatBotType\": \"ADVANCED\","
                                + "\"supportType\": \"CHAT\","
                                + "\"analyticsType\": \"PRO\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.error.code").value("VALIDATION_ERROR"));

        verify(tariffService, never()).createTariff(any());
    }

    @Test
    void createTariff_whenNegativeCost_returns400() throws Exception {
        mockMvc.perform(post("/tariffs")
                        .contentType("application/json")
                        .content("{"
                                + "\"name\": \"PRO\","
                                + "\"cost\": -1,"
                                + "\"chatBotType\": \"ADVANCED\","
                                + "\"supportType\": \"CHAT\","
                                + "\"analyticsType\": \"PRO\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("VALIDATION_ERROR"));

        verify(tariffService, never()).createTariff(any());
    }

    @Test
    void updateTariff_returns200() throws Exception {
        when(tariffService.updateTariff(eq(TARIFF_ID), any())).thenReturn(response());

        mockMvc.perform(put("/tariffs/{id}", TARIFF_ID)
                        .contentType("application/json")
                        .content("{\"name\": \"PRO\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.name").value("PRO"));

        verify(tariffService).updateTariff(eq(TARIFF_ID), any());
    }

    @Test
    void deleteTariff_returns204() throws Exception {
        mockMvc.perform(delete("/tariffs/{id}", TARIFF_ID))
                .andExpect(status().isNoContent());

        verify(tariffService).deleteTariff(TARIFF_ID);
    }
}