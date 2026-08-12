package com.n4d3sh1k4.billing_service.service;

import com.n4d3sh1k4.billing_service.domain.model.tariff.Tariff;
import com.n4d3sh1k4.billing_service.domain.repository.TariffRepository;
import com.n4d3sh1k4.billing_service.dto.TariffResponse;
import com.n4d3sh1k4.billing_service.dto.request_dto.CreateTariffRequest;
import com.n4d3sh1k4.billing_service.dto.request_dto.UpdateTariffRequest;
import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class TariffService {

    private final TariffRepository tariffRepository;

    @Transactional
    public TariffResponse createTariff(CreateTariffRequest request) {
        Tariff tariff = Tariff.builder()
                .name(request.getName())
                .cost(request.getCost())
                .projects(request.getProjects())
                .posts(request.getPosts())
                .chatBotType(request.getChatBotType())
                .supportType(request.getSupportType())
                .analyticsType(request.getAnalyticsType())
                .aiGenerations(request.getAiGenerations())
                .build();

        tariffRepository.save(tariff);
        log.info("Tariff {} created", tariff.getName());

        return toResponse(tariff);
    }

    @Transactional
    public TariffResponse updateTariff(UUID id, UpdateTariffRequest request) {
        Tariff tariff = tariffRepository.findById(id)
                .orElseThrow(() -> new ContentNotFoundException("Tariff not found"));

        if (request.getName() != null) tariff.setName(request.getName());
        if (request.getCost() != null) tariff.setCost(request.getCost());
        if (request.getProjects() != null) tariff.setProjects(request.getProjects());
        if (request.getPosts() != null) tariff.setPosts(request.getPosts());
        if (request.getChatBotType() != null) tariff.setChatBotType(request.getChatBotType());
        if (request.getSupportType() != null) tariff.setSupportType(request.getSupportType());
        if (request.getAnalyticsType() != null) tariff.setAnalyticsType(request.getAnalyticsType());
        if (request.getAiGenerations() != null) tariff.setAiGenerations(request.getAiGenerations());

        tariffRepository.save(tariff);
        log.info("Tariff {} updated", tariff.getName());

        return toResponse(tariff);
    }

    @Transactional(readOnly = true)
    public List<TariffResponse> getAllTariffs() {
        return tariffRepository.findAll().stream()
                .map(this::toResponse)
                .toList();
    }

    @Transactional(readOnly = true)
    public TariffResponse getTariff(UUID id) {
        return tariffRepository.findById(id)
                .map(this::toResponse)
                .orElseThrow(() -> new ContentNotFoundException("Tariff not found"));
    }

    @Transactional
    public void deleteTariff(UUID id) {
        Tariff tariff = tariffRepository.findById(id)
                .orElseThrow(() -> new ContentNotFoundException("Tariff not found"));
        tariffRepository.delete(tariff);
        log.info("Tariff {} deleted", tariff.getName());
    }

    private TariffResponse toResponse(Tariff tariff) {
        return new TariffResponse(
                tariff.getId(),
                tariff.getName(),
                tariff.getCost(),
                tariff.getProjects(),
                tariff.getPosts(),
                tariff.getChatBotType(),
                tariff.getSupportType(),
                tariff.getAnalyticsType(),
                tariff.getAiGenerations()
        );
    }
}
