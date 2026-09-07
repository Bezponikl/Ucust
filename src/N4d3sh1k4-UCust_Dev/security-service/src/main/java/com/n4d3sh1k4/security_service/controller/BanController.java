package com.n4d3sh1k4.security_service.controller;

import com.n4d3sh1k4.security_service.dto.BanResponse;
import com.n4d3sh1k4.security_service.dto.request_dto.CreateBanRequest;
import com.n4d3sh1k4.security_service.service.BanService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@Tag(name = "Баны", description = "Управление банами пользователей (только админ)")
@RestController
@RequestMapping("/admin/bans")
@RequiredArgsConstructor
public class BanController {

    private final BanService banService;

    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "Забанить пользователя")
    @PostMapping
    public ResponseEntity<BanResponse> createBan(@Valid @RequestBody CreateBanRequest request, Authentication authentication) {
        UUID adminId = UUID.fromString(authentication.getName());
        BanResponse ban = banService.createBan(request, adminId);
        return ResponseEntity.status(HttpStatus.CREATED).body(ban);
    }

    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "Разбанить (деактивировать бан)")
    @PostMapping("/{id}/unban")
    public ResponseEntity<Void> unban(@PathVariable UUID id) {
        banService.unban(id);
        return ResponseEntity.ok().build();
    }

    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "Все активные баны")
    @GetMapping
    public ResponseEntity<List<BanResponse>> getActiveBans() {
        return ResponseEntity.ok(banService.getAllActiveBans());
    }

    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "Получить активный бан пользователя")
    @GetMapping("/user/{userId}")
    public ResponseEntity<BanResponse> getUserActiveBan(@PathVariable UUID userId) {
        BanResponse ban = banService.getActiveBanByUser(userId);
        if (ban == null) {
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.ok(ban);
    }

    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "История банов пользователя")
    @GetMapping("/user/{userId}/history")
    public ResponseEntity<List<BanResponse>> getUserBanHistory(@PathVariable UUID userId) {
        return ResponseEntity.ok(banService.getUserBans(userId));
    }

    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "Проверить, забанен ли пользователь")
    @GetMapping("/user/{userId}/check")
    public ResponseEntity<Boolean> isUserBanned(@PathVariable UUID userId) {
        return ResponseEntity.ok(banService.isUserBanned(userId));
    }
}