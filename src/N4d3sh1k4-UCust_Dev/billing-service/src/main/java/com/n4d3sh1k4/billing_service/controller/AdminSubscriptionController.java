package com.n4d3sh1k4.billing_service.controller;

import com.n4d3sh1k4.billing_service.dto.SubscriptionResponse;
import com.n4d3sh1k4.billing_service.service.SubscriptionService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@Tag(name = "Админ: подписки", description = "Управление тарифами пользователей (только для администраторов)")
@RestController
@RequestMapping("/admin/billing/subscriptions")
@RequiredArgsConstructor
public class AdminSubscriptionController {

    private final SubscriptionService subscriptionService;

    @Operation(summary = "Выдать пользователю тариф")
    @PutMapping("/{userId}/tariff/{tariffId}")
    public ResponseEntity<SubscriptionResponse> assignTariff(
            @PathVariable UUID userId,
            @PathVariable UUID tariffId) {
        return ResponseEntity.ok(subscriptionService.assignTariff(userId, tariffId));
    }

    @Operation(summary = "Получить подписку пользователя")
    @GetMapping("/{userId}")
    public ResponseEntity<SubscriptionResponse> getSubscription(@PathVariable UUID userId) {
        SubscriptionResponse response = subscriptionService.getSubscription(userId);
        return response != null
                ? ResponseEntity.ok(response)
                : ResponseEntity.notFound().build();
    }
}