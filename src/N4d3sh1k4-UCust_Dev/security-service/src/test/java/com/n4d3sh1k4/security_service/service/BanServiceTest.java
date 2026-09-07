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
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;
import org.springframework.http.HttpStatus;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class BanServiceTest {

    @Mock
    private BanRepository banRepository;

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private BanService banService;

    private final UUID userId = UUID.randomUUID();
    private final UUID adminId = UUID.randomUUID();

    private User user() {
        User u = new User();
        u.setId(userId);
        u.setEmail("user@example.com");
        return u;
    }

    private Ban activeBan() {
        return Ban.builder()
                .id(UUID.randomUUID())
                .user(user())
                .type(BanType.MANUAL)
                .reason("Нарушение правил")
                .bannedBy(adminId)
                .createdAt(Instant.now())
                .expiresAt(null)
                .active(true)
                .build();
    }

    private CreateBanRequest createBanRequest() {
        CreateBanRequest req = new CreateBanRequest();
        req.setUserId(userId);
        req.setReason("Нарушение правил");
        req.setExpiresAt(null);
        return req;
    }

    // ---------- createBan ----------

    @Test
    void createBan_whenUserNotFound_throwsContentNotFound() {
        when(userRepository.findById(userId)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> banService.createBan(createBanRequest(), adminId))
                .isInstanceOf(ContentNotFoundException.class);
    }

    @Test
    void createBan_whenActiveBanExists_throwsBanAlreadyActive() {
        when(userRepository.findById(userId)).thenReturn(Optional.of(user()));
        when(banRepository.findByUserIdAndActiveTrue(userId)).thenReturn(Optional.of(activeBan()));

        assertThatThrownBy(() -> banService.createBan(createBanRequest(), adminId))
                .isInstanceOf(BaseException.class)
                .satisfies(e -> {
                    assertThat(((BaseException) e).getCode()).isEqualTo("BAN_ALREADY_ACTIVE");
                    assertThat(((BaseException) e).getStatus()).isEqualTo(HttpStatus.CONFLICT);
                });

        verify(banRepository, never()).save(any(Ban.class));
    }

    @Test
    void createBan_whenValid_savesBanAndReturnsResponse() {
        when(userRepository.findById(userId)).thenReturn(Optional.of(user()));
        when(banRepository.findByUserIdAndActiveTrue(userId)).thenReturn(Optional.empty());
        when(banRepository.save(any(Ban.class))).thenAnswer(inv -> {
            Ban b = inv.getArgument(0);
            b.setId(UUID.randomUUID());
            return b;
        });

        BanResponse response = banService.createBan(createBanRequest(), adminId);

        ArgumentCaptor<Ban> banCaptor = ArgumentCaptor.forClass(Ban.class);
        verify(banRepository).save(banCaptor.capture());
        Ban saved = banCaptor.getValue();
        assertThat(saved.getUser().getId()).isEqualTo(userId);
        assertThat(saved.getType()).isEqualTo(BanType.MANUAL);
        assertThat(saved.getReason()).isEqualTo("Нарушение правил");
        assertThat(saved.getBannedBy()).isEqualTo(adminId);
        assertThat(saved.isActive()).isTrue();

        assertThat(response.id()).isEqualTo(saved.getId());
        assertThat(response.userId()).isEqualTo(userId);
        assertThat(response.email()).isEqualTo("user@example.com");
        assertThat(response.type()).isEqualTo(BanType.MANUAL);
        assertThat(response.reason()).isEqualTo("Нарушение правил");
        assertThat(response.bannedBy()).isEqualTo(adminId);
        assertThat(response.active()).isTrue();
    }

    // ---------- unban ----------

    @Test
    void unban_whenBanNotFound_throwsContentNotFound() {
        UUID banId = UUID.randomUUID();
        when(banRepository.findById(banId)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> banService.unban(banId))
                .isInstanceOf(ContentNotFoundException.class);
    }

    @Test
    void unban_whenAlreadyInactive_throwsBanAlreadyInactive() {
        Ban ban = activeBan();
        ban.setActive(false);
        when(banRepository.findById(ban.getId())).thenReturn(Optional.of(ban));

        assertThatThrownBy(() -> banService.unban(ban.getId()))
                .isInstanceOf(BaseException.class)
                .satisfies(e -> {
                    assertThat(((BaseException) e).getCode()).isEqualTo("BAN_ALREADY_INACTIVE");
                    assertThat(((BaseException) e).getStatus()).isEqualTo(HttpStatus.BAD_REQUEST);
                });

        verify(banRepository, never()).save(any(Ban.class));
    }

    @Test
    void unban_whenActive_deactivatesAndSaves() {
        Ban ban = activeBan();
        when(banRepository.findById(ban.getId())).thenReturn(Optional.of(ban));

        banService.unban(ban.getId());

        assertThat(ban.isActive()).isFalse();
        verify(banRepository).save(ban);
    }

    // ---------- unbanAllActiveByUser ----------

    @Test
    void unbanAllActiveByUser_delegatesToRepository() {
        banService.unbanAllActiveByUser(userId);

        verify(banRepository).deactivateAllActiveByUserId(userId);
    }

    // ---------- getActiveBanByUser ----------

    @Test
    void getActiveBanByUser_whenPresent_returnsResponse() {
        Ban ban = activeBan();
        when(banRepository.findByUserIdAndActiveTrue(userId)).thenReturn(Optional.of(ban));

        BanResponse response = banService.getActiveBanByUser(userId);

        assertThat(response).isNotNull();
        assertThat(response.id()).isEqualTo(ban.getId());
        assertThat(response.userId()).isEqualTo(userId);
    }

    @Test
    void getActiveBanByUser_whenAbsent_returnsNull() {
        when(banRepository.findByUserIdAndActiveTrue(userId)).thenReturn(Optional.empty());

        assertThat(banService.getActiveBanByUser(userId)).isNull();
    }

    // ---------- isUserBanned ----------

    @Test
    void isUserBanned_whenNoBan_returnsFalse() {
        when(banRepository.findByUserIdAndActiveTrue(userId)).thenReturn(Optional.empty());

        assertThat(banService.isUserBanned(userId)).isFalse();
    }

    @Test
    void isUserBanned_whenActiveBanNotExpired_returnsTrue() {
        Ban ban = activeBan();
        ban.setExpiresAt(Instant.now().plusSeconds(3600));
        when(banRepository.findByUserIdAndActiveTrue(userId)).thenReturn(Optional.of(ban));

        assertThat(banService.isUserBanned(userId)).isTrue();
        verify(banRepository, never()).save(any(Ban.class));
    }

    @Test
    void isUserBanned_whenActiveBanExpired_deactivatesAndReturnsFalse() {
        Ban ban = activeBan();
        ban.setExpiresAt(Instant.now().minusSeconds(60));
        when(banRepository.findByUserIdAndActiveTrue(userId)).thenReturn(Optional.of(ban));

        assertThat(banService.isUserBanned(userId)).isFalse();

        assertThat(ban.isActive()).isFalse();
        verify(banRepository).save(ban);
    }

    // ---------- getUserBans / getAllActiveBans ----------

    @Test
    void getUserBans_mapsAllBans() {
        Ban ban1 = activeBan();
        Ban ban2 = activeBan();
        when(banRepository.findByUserIdOrderByCreatedAtDesc(userId))
                .thenReturn(List.of(ban1, ban2));

        List<BanResponse> responses = banService.getUserBans(userId);

        assertThat(responses).hasSize(2);
        assertThat(responses).extracting(BanResponse::id).containsExactly(ban1.getId(), ban2.getId());
    }

    @Test
    void getAllActiveBans_mapsAllBans() {
        Ban ban = activeBan();
        when(banRepository.findAllActive()).thenReturn(List.of(ban));

        List<BanResponse> responses = banService.getAllActiveBans();

        assertThat(responses).hasSize(1);
        assertThat(responses.get(0).id()).isEqualTo(ban.getId());
        assertThat(responses.get(0).active()).isTrue();
    }
}