package com.n4d3sh1k4.security_service.service;

import com.n4d3sh1k4.common.exception.BaseException;
import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import com.n4d3sh1k4.security_service.domain.model.ban.Ban;
import com.n4d3sh1k4.security_service.domain.model.ban.BanType;
import com.n4d3sh1k4.security_service.domain.model.users.User;
import com.n4d3sh1k4.security_service.domain.repository.BanRepository;
import com.n4d3sh1k4.security_service.domain.repository.UserRepository;
import com.n4d3sh1k4.security_service.dto.BanResponse;
import com.n4d3sh1k4.security_service.dto.request_dto.CreateBanRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class BanService {

    private final BanRepository banRepository;
    private final UserRepository userRepository;

    @Transactional
    public BanResponse createBan(CreateBanRequest request, UUID adminId) {
        User user = userRepository.findById(request.getUserId())
                .orElseThrow(() -> new ContentNotFoundException("User not found"));

        banRepository.findByUserIdAndActiveTrue(user.getId()).ifPresent(activeBan -> {
            throw new BaseException("User already has an active ban", "BAN_ALREADY_ACTIVE", HttpStatus.CONFLICT);
        });

        Ban ban = Ban.builder()
                .user(user)
                .type(BanType.MANUAL)
                .reason(request.getReason())
                .bannedBy(adminId)
                .createdAt(Instant.now())
                .expiresAt(request.getExpiresAt())
                .active(true)
                .build();

        banRepository.save(ban);

        log.warn("User {} banned by admin {}. Reason: {}", user.getEmail(), adminId, request.getReason());

        return toResponse(ban);
    }

    @Transactional
    public void unban(UUID banId) {
        Ban ban = banRepository.findById(banId)
                .orElseThrow(() -> new ContentNotFoundException("Ban not found"));

        if (!ban.isActive()) {
            throw new BaseException("Ban is already inactive", "BAN_ALREADY_INACTIVE", HttpStatus.BAD_REQUEST);
        }

        ban.setActive(false);
        banRepository.save(ban);

        log.info("Ban {} for user {} deactivated", banId, ban.getUser().getEmail());
    }

    @Transactional
    public void unbanAllActiveByUser(UUID userId) {
        banRepository.deactivateAllActiveByUserId(userId);
        log.info("All active bans deactivated for user {}", userId);
    }

    @Transactional(readOnly = true)
    public BanResponse getActiveBanByUser(UUID userId) {
        return banRepository.findByUserIdAndActiveTrue(userId)
                .map(this::toResponse)
                .orElse(null);
    }

    @Transactional(readOnly = true)
    public boolean isUserBanned(UUID userId) {
        return banRepository.findByUserIdAndActiveTrue(userId)
                .map(ban -> {
                    if (ban.getExpiresAt() != null && ban.getExpiresAt().isBefore(Instant.now())) {
                        ban.setActive(false);
                        banRepository.save(ban);
                        return false;
                    }
                    return true;
                })
                .orElse(false);
    }

    @Transactional(readOnly = true)
    public List<BanResponse> getUserBans(UUID userId) {
        return banRepository.findByUserIdOrderByCreatedAtDesc(userId)
                .stream()
                .map(this::toResponse)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<BanResponse> getAllActiveBans() {
        return banRepository.findAllActive()
                .stream()
                .map(this::toResponse)
                .toList();
    }

    private BanResponse toResponse(Ban ban) {
        return new BanResponse(
                ban.getId(),
                ban.getUser().getId(),
                ban.getUser().getEmail(),
                ban.getType(),
                ban.getReason(),
                ban.getBannedBy(),
                ban.getCreatedAt(),
                ban.getExpiresAt(),
                ban.isActive()
        );
    }
}
