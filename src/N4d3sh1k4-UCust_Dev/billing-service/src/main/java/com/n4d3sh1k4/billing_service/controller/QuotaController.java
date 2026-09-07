package com.n4d3sh1k4.billing_service.controller;

import com.n4d3sh1k4.billing_service.dto.CheckQuotaRequest;
import com.n4d3sh1k4.billing_service.dto.CheckQuotaResponse;
import com.n4d3sh1k4.billing_service.service.QuotaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@Tag(name = "Квоты", description = "Проверка и управление лимитами пользователей")
@RestController
@RequestMapping("/internal/quota")
@RequiredArgsConstructor
public class QuotaController {

    private final QuotaService quotaService;

    @Operation(summary = "Проверить квоту пользователя (внутренний)")
    @PostMapping("/check")
    public ResponseEntity<CheckQuotaResponse> checkQuota(@Valid @RequestBody CheckQuotaRequest request) {
        return ResponseEntity.ok(quotaService.checkQuota(request));
    }

    @Operation(summary = "Инкрементировать использование (внутренний)")
    @PostMapping("/use/{userId}/{feature}")
    public ResponseEntity<Void> incrementUsage(@PathVariable UUID userId, @PathVariable String feature) {
        quotaService.incrementUsage(userId, feature);
        return ResponseEntity.ok().build();
    }
}