package com.n4d3sh1k4.billing_service.service;

import com.n4d3sh1k4.billing_service.domain.model.tariff.AnalyticsType;
import com.n4d3sh1k4.billing_service.domain.model.tariff.ChatBotType;
import com.n4d3sh1k4.billing_service.domain.model.tariff.SupportType;
import com.n4d3sh1k4.billing_service.domain.model.tariff.Tariff;
import com.n4d3sh1k4.billing_service.domain.repository.TariffRepository;
import com.n4d3sh1k4.billing_service.dto.TariffResponse;
import com.n4d3sh1k4.billing_service.dto.request_dto.CreateTariffRequest;
import com.n4d3sh1k4.billing_service.dto.request_dto.UpdateTariffRequest;
import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;

import java.math.BigDecimal;
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
class TariffServiceTest {

    private static final UUID TARIFF_ID = UUID.fromString("11111111-1111-1111-1111-111111111111");

    @Mock
    private TariffRepository repository;

    @InjectMocks
    private TariffService tariffService;

    private Tariff tariff() {
        return Tariff.builder()
                .id(TARIFF_ID)
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

    private CreateTariffRequest createRequest() {
        CreateTariffRequest request = new CreateTariffRequest();
        request.setName("PRO");
        request.setCost(new BigDecimal("29.99"));
        request.setProjects(10);
        request.setPosts(200);
        request.setChatBotType(ChatBotType.ADVANCED);
        request.setSupportType(SupportType.CHAT);
        request.setAnalyticsType(AnalyticsType.PRO);
        request.setAiGenerations(500);
        return request;
    }

    private UpdateTariffRequest updateRequest() {
        UpdateTariffRequest request = new UpdateTariffRequest();
        request.setName("PRO+");
        request.setCost(new BigDecimal("39.99"));
        return request;
    }

    @Test
    void createTariff_buildsEntityAndSaves() {
        when(repository.save(any(Tariff.class))).thenAnswer(invocation -> {
            Tariff tariff = invocation.getArgument(0);
            tariff.setId(TARIFF_ID);
            return tariff;
        });

        TariffResponse response = tariffService.createTariff(createRequest());

        assertThat(response.id()).isEqualTo(TARIFF_ID);
        assertThat(response.name()).isEqualTo("PRO");
        assertThat(response.cost()).isEqualByComparingTo("29.99");
        assertThat(response.projects()).isEqualTo(10);
        assertThat(response.chatBotType()).isEqualTo(ChatBotType.ADVANCED);

        org.mockito.ArgumentCaptor<Tariff> captor = org.mockito.ArgumentCaptor.forClass(Tariff.class);
        verify(repository).save(captor.capture());
        assertThat(captor.getValue().getAiGenerations()).isEqualTo(500);
    }

    @Test
    void updateTariff_updatesNonNullFields() {
        when(repository.findById(TARIFF_ID)).thenReturn(Optional.of(tariff()));

        TariffResponse response = tariffService.updateTariff(TARIFF_ID, updateRequest());

        assertThat(response.name()).isEqualTo("PRO+");
        assertThat(response.cost()).isEqualByComparingTo("39.99");
        assertThat(response.posts()).isEqualTo(200);
        assertThat(response.chatBotType()).isEqualTo(ChatBotType.ADVANCED);

        verify(repository).save(any(Tariff.class));
    }

    @Test
    void updateTariff_whenNotFound_throwsContentNotFound() {
        when(repository.findById(TARIFF_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> tariffService.updateTariff(TARIFF_ID, updateRequest()))
                .isInstanceOf(ContentNotFoundException.class);
    }

    @Test
    void getAllTariffs_returnsAll() {
        when(repository.findAll()).thenReturn(List.of(tariff()));

        List<TariffResponse> responses = tariffService.getAllTariffs();

        assertThat(responses).hasSize(1);
        assertThat(responses.get(0).name()).isEqualTo("PRO");
    }

    @Test
    void getTariff_whenFound_returnsResponse() {
        when(repository.findById(TARIFF_ID)).thenReturn(Optional.of(tariff()));

        TariffResponse response = tariffService.getTariff(TARIFF_ID);

        assertThat(response.id()).isEqualTo(TARIFF_ID);
        assertThat(response.name()).isEqualTo("PRO");
    }

    @Test
    void getTariff_whenNotFound_throwsContentNotFound() {
        when(repository.findById(TARIFF_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> tariffService.getTariff(TARIFF_ID))
                .isInstanceOf(ContentNotFoundException.class);
    }

    @Test
    void deleteTariff_whenExists_deletes() {
        when(repository.findById(TARIFF_ID)).thenReturn(Optional.of(tariff()));

        tariffService.deleteTariff(TARIFF_ID);

        verify(repository).delete(tariff());
    }

    @Test
    void deleteTariff_whenNotFound_throwsContentNotFound() {
        when(repository.findById(TARIFF_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> tariffService.deleteTariff(TARIFF_ID))
                .isInstanceOf(ContentNotFoundException.class);

        verify(repository, never()).delete(any());
    }
}