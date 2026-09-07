package com.n4d3sh1k4.billing_service.controller;

import com.n4d3sh1k4.billing_service.dto.CheckQuotaResponse;
import com.n4d3sh1k4.billing_service.dto.CheckQuotaRequest;
import com.n4d3sh1k4.billing_service.dto.PurchaseTariffRequest;
import com.n4d3sh1k4.billing_service.dto.SubscriptionOverview;
import com.n4d3sh1k4.billing_service.service.QuotaService;
import com.n4d3sh1k4.billing_service.service.SubscriptionService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@Tag(name = "Квоты пользователя")
@RestController
@RequestMapping("/quota")
@RequiredArgsConstructor
public class UserQuotaController {

    private final QuotaService quotaService;
    private final SubscriptionService subscriptionService;

    @Operation(summary = "Получить свою квоту по фиче")
    @GetMapping("/me")
    public ResponseEntity<CheckQuotaResponse> getMyQuota(
            @RequestParam(defaultValue = "generation") String feature,
            Authentication authentication) {
        UUID userId = UUID.fromString(authentication.getName());
        CheckQuotaRequest request = new CheckQuotaRequest();
        request.setUserId(userId);
        request.setFeature(feature);
        request.setRequested(1);
        return ResponseEntity.ok(quotaService.checkQuota(request));
    }

    @Operation(summary = "Получить свой тариф и квоты по всем фичам")
    @GetMapping("/me/tariff")
    public ResponseEntity<SubscriptionOverview> getMySubscription(Authentication authentication) {
        UUID userId = UUID.fromString(authentication.getName());
        SubscriptionOverview overview = subscriptionService.getSubscriptionOverview(userId);
        return overview != null
                ? ResponseEntity.ok(overview)
                : ResponseEntity.notFound().build();
    }

    @Operation(summary = "Купить тариф (заглушка, далее — оплата через провайдера)")
    @PostMapping("/me/purchase")
    public ResponseEntity<SubscriptionOverview> purchase(
            @Valid @RequestBody PurchaseTariffRequest request,
            Authentication authentication) {
        UUID userId = UUID.fromString(authentication.getName());
        return ResponseEntity.ok(subscriptionService.purchaseTariff(userId, request.tariffId()));
    }
}