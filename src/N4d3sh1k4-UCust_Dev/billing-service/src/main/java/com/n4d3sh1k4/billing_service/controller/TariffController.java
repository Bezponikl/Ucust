package com.n4d3sh1k4.billing_service.controller;

import com.n4d3sh1k4.billing_service.dto.TariffResponse;
import com.n4d3sh1k4.billing_service.dto.request_dto.CreateTariffRequest;
import com.n4d3sh1k4.billing_service.dto.request_dto.UpdateTariffRequest;
import com.n4d3sh1k4.billing_service.service.TariffService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@Tag(name = "Тарифы", description = "Управление тарифами")
@RestController
@RequestMapping("/tariffs")
@RequiredArgsConstructor
public class TariffController {

    private final TariffService tariffService;

    @Operation(summary = "Все тарифы")
    @GetMapping
    public ResponseEntity<List<TariffResponse>> getAllTariffs() {
        return ResponseEntity.ok(tariffService.getAllTariffs());
    }

    @Operation(summary = "Тариф по ID")
    @GetMapping("/{id}")
    public ResponseEntity<TariffResponse> getTariff(@PathVariable UUID id) {
        return ResponseEntity.ok(tariffService.getTariff(id));
    }

    @Operation(summary = "Создать тариф (админ)")
    @PostMapping
    public ResponseEntity<TariffResponse> createTariff(@Valid @RequestBody CreateTariffRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(tariffService.createTariff(request));
    }

    @Operation(summary = "Обновить тариф (админ)")
    @PutMapping("/{id}")
    public ResponseEntity<TariffResponse> updateTariff(@PathVariable UUID id, @Valid @RequestBody UpdateTariffRequest request) {
        return ResponseEntity.ok(tariffService.updateTariff(id, request));
    }

    @Operation(summary = "Удалить тариф (админ)")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTariff(@PathVariable UUID id) {
        tariffService.deleteTariff(id);
        return ResponseEntity.noContent().build();
    }
}
