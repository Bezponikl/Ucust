package com.n4d3sh1k4.security_service.controller;

import com.n4d3sh1k4.common.exception.BaseException;
import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import com.n4d3sh1k4.security_service.domain.model.ban.BanType;
import com.n4d3sh1k4.security_service.dto.BanResponse;
import com.n4d3sh1k4.security_service.dto.request_dto.CreateBanRequest;
import com.n4d3sh1k4.security_service.jwt.JwtProvider;
import com.n4d3sh1k4.security_service.service.BanService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.autoconfigure.web.DataWebAutoConfiguration;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.HttpStatus;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(excludeAutoConfiguration = DataWebAutoConfiguration.class)
@Import(BanController.class)
@AutoConfigureMockMvc(addFilters = true)
class BanControllerTest {

    private static final String ADMIN_ID = "550e8400-e29b-41d4-a716-446655440000";
    private static final String USER_ID = "550e8400-e29b-41d4-a716-446655440001";

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private BanService banService;

    @MockitoBean
    private JwtProvider jwtProvider;

    private BanResponse banResponse() {
        return new BanResponse(
                UUID.fromString("11111111-2222-3333-4444-555555555555"),
                UUID.fromString(USER_ID),
                "user@gmail.com",
                BanType.MANUAL,
                "Нарушение правил платформы",
                UUID.fromString(ADMIN_ID),
                Instant.parse("2026-08-01T10:00:00Z"),
                null,
                true
        );
    }

    @Test
    void createBan_success_returns201() throws Exception {
        UUID adminUuid = UUID.fromString(ADMIN_ID);
        when(banService.createBan(any(CreateBanRequest.class), eq(adminUuid)))
                .thenReturn(banResponse());

        mockMvc.perform(post("/admin/bans")
                        .with(user(ADMIN_ID))
                        .contentType("application/json")
                        .content("""
                                {
                                  "userId": "550e8400-e29b-41d4-a716-446655440001",
                                  "reason": "Нарушение правил платформы"
                                }
                                """))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.userId").value(USER_ID))
                .andExpect(jsonPath("$.data.type").value("MANUAL"))
                .andExpect(jsonPath("$.data.active").value(true));
    }

    @Test
    void createBan_missingUserId_returns400() throws Exception {
        mockMvc.perform(post("/admin/bans")
                        .with(user(ADMIN_ID))
                        .contentType("application/json")
                        .content("{\"reason\": \"Нарушение правил платформы\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("VALIDATION_ERROR"));
    }

    @Test
    void createBan_blankReason_returns400() throws Exception {
        mockMvc.perform(post("/admin/bans")
                        .with(user(ADMIN_ID))
                        .contentType("application/json")
                        .content("""
                                {
                                  "userId": "550e8400-e29b-41d4-a716-446655440001",
                                  "reason": "  "
                                }
                                """))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("VALIDATION_ERROR"));
    }

    @Test
    void createBan_userNotFound_returns404() throws Exception {
        doThrow(new ContentNotFoundException("User not found"))
                .when(banService).createBan(any(), any());

        mockMvc.perform(post("/admin/bans")
                        .with(user(ADMIN_ID))
                        .contentType("application/json")
                        .content("""
                                {
                                  "userId": "550e8400-e29b-41d4-a716-446655440001",
                                  "reason": "Нарушение правил платформы"
                                }
                                """))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.error.code").value("NOT_FOUND"));
    }

    @Test
    void createBan_alreadyActive_returns409() throws Exception {
        doThrow(new BaseException("User already has an active ban", "BAN_ALREADY_ACTIVE", HttpStatus.CONFLICT))
                .when(banService).createBan(any(), any());

        mockMvc.perform(post("/admin/bans")
                        .with(user(ADMIN_ID))
                        .contentType("application/json")
                        .content("""
                                {
                                  "userId": "550e8400-e29b-41d4-a716-446655440001",
                                  "reason": "Нарушение правил платформы"
                                }
                                """))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.error.code").value("BAN_ALREADY_ACTIVE"));
    }

    @Test
    void unban_success_returns200() throws Exception {
        mockMvc.perform(post("/admin/bans/11111111-2222-3333-4444-555555555555/unban")
                        .with(user(ADMIN_ID)))
                .andExpect(status().isOk());

        org.mockito.Mockito.verify(banService).unban(UUID.fromString("11111111-2222-3333-4444-555555555555"));
    }

    @Test
    void unban_notFound_returns404() throws Exception {
        doThrow(new ContentNotFoundException("Ban not found"))
                .when(banService).unban(any(UUID.class));

        mockMvc.perform(post("/admin/bans/11111111-2222-3333-4444-555555555555/unban")
                        .with(user(ADMIN_ID)))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.error.code").value("NOT_FOUND"));
    }

    @Test
    void unban_alreadyInactive_returns400() throws Exception {
        doThrow(new BaseException("Ban is already inactive", "BAN_ALREADY_INACTIVE", HttpStatus.BAD_REQUEST))
                .when(banService).unban(any(UUID.class));

        mockMvc.perform(post("/admin/bans/11111111-2222-3333-4444-555555555555/unban")
                        .with(user(ADMIN_ID)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("BAN_ALREADY_INACTIVE"));
    }

    @Test
    void getActiveBans_returns200() throws Exception {
        when(banService.getAllActiveBans()).thenReturn(List.of(banResponse()));

        mockMvc.perform(get("/admin/bans").with(user(ADMIN_ID)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data[0].id").value("11111111-2222-3333-4444-555555555555"));
    }

    @Test
    void getActiveBans_empty_returns200() throws Exception {
        when(banService.getAllActiveBans()).thenReturn(List.of());

        mockMvc.perform(get("/admin/bans").with(user(ADMIN_ID)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data").isArray())
                .andExpect(jsonPath("$.data").isEmpty());
    }

    @Test
    void getUserActiveBan_found_returns200() throws Exception {
        when(banService.getActiveBanByUser(UUID.fromString(USER_ID))).thenReturn(banResponse());

        mockMvc.perform(get("/admin/bans/user/" + USER_ID).with(user(ADMIN_ID)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.userId").value(USER_ID));
    }

    @Test
    void getUserActiveBan_noBan_returns204() throws Exception {
        when(banService.getActiveBanByUser(UUID.fromString(USER_ID))).thenReturn(null);

        mockMvc.perform(get("/admin/bans/user/" + USER_ID).with(user(ADMIN_ID)))
                .andExpect(status().isNoContent());
    }

    @Test
    void getUserBanHistory_returns200() throws Exception {
        when(banService.getUserBans(UUID.fromString(USER_ID))).thenReturn(List.of(banResponse()));

        mockMvc.perform(get("/admin/bans/user/" + USER_ID + "/history").with(user(ADMIN_ID)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data[0].active").value(true));
    }

    @Test
    void isUserBanned_true_returns200() throws Exception {
        when(banService.isUserBanned(UUID.fromString(USER_ID))).thenReturn(true);

        mockMvc.perform(get("/admin/bans/user/" + USER_ID + "/check").with(user(ADMIN_ID)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data").value(true));
    }

    @Test
    void isUserBanned_false_returns200() throws Exception {
        when(banService.isUserBanned(UUID.fromString(USER_ID))).thenReturn(false);

        mockMvc.perform(get("/admin/bans/user/" + USER_ID + "/check").with(user(ADMIN_ID)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data").value(false));
    }
}