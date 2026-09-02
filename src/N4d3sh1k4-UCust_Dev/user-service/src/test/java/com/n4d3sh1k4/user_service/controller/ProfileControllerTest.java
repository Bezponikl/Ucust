package com.n4d3sh1k4.user_service.controller;

import com.n4d3sh1k4.common.exception.UniversalExeption;
import com.n4d3sh1k4.common.exception.UserNotFoundException;
import com.n4d3sh1k4.user_service.dto.ProfileResponse;
import com.n4d3sh1k4.user_service.dto.UpdateProfileRequest;
import com.n4d3sh1k4.user_service.dto.UserPrincipal;
import com.n4d3sh1k4.user_service.service.ProfileService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.autoconfigure.web.DataWebAutoConfiguration;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.HttpStatus;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.RequestPostProcessor;

import java.util.Set;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.authentication;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(excludeAutoConfiguration = DataWebAutoConfiguration.class)
@Import(ProfileController.class)
@AutoConfigureMockMvc(addFilters = true)
class ProfileControllerTest {

    private static final UUID USER_ID = UUID.fromString("550e8400-e29b-41d4-a716-446655440000");
    private static final String AVATAR_URL = "http://minio:9000/user-service/avatars/avatar.jpg";

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private ProfileService profileService;

    private UserPrincipal principal;
    private ProfileResponse profileResponse;

    @BeforeEach
    void setUp() {
        principal = new UserPrincipal(USER_ID, "user@example.com", Set.of("ROLE_USER"));
        profileResponse = new ProfileResponse(
                USER_ID, "Олег", "Иванов", "user@example.com",
                "79991234567", "Разработчик", AVATAR_URL);
    }

    private RequestPostProcessor authenticated() {
        return authentication(new UsernamePasswordAuthenticationToken(
                principal, null, principal.getAuthorities()));
    }

    // ---------- GET /user/me ----------

    @Test
    void getMyProfile_returnsCurrentUserProfile() throws Exception {
        when(profileService.getProfile(USER_ID)).thenReturn(profileResponse);

        mockMvc.perform(get("/user/me").with(authenticated()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.id").value(USER_ID.toString()))
                .andExpect(jsonPath("$.data.firstName").value("Олег"))
                .andExpect(jsonPath("$.data.lastName").value("Иванов"))
                .andExpect(jsonPath("$.data.email").value("user@example.com"))
                .andExpect(jsonPath("$.data.phone").value("79991234567"))
                .andExpect(jsonPath("$.data.position").value("Разработчик"))
                .andExpect(jsonPath("$.data.fullAvatarUrl").value(AVATAR_URL));

        verify(profileService).getProfile(USER_ID);
    }

    @Test
    void getMyProfile_whenUserNotFound_returns404() throws Exception {
        when(profileService.getProfile(USER_ID)).thenThrow(new UserNotFoundException("User not found"));

        mockMvc.perform(get("/user/me").with(authenticated()))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.error.code").value("USER_NOT_FOUND"));
    }

    // ---------- PATCH /user/me ----------

    @Test
    void updateProfile_updatesAndReturnsProfile() throws Exception {
        when(profileService.update(eq(USER_ID), any(UpdateProfileRequest.class))).thenReturn(profileResponse);

        mockMvc.perform(patch("/user/me")
                        .with(authenticated())
                        .contentType("application/json")
                        .content("""
                                {
                                  "firstName": "Петр",
                                  "phone": "79991234567"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.firstName").value("Олег"));

        ArgumentCaptor<UpdateProfileRequest> captor = ArgumentCaptor.forClass(UpdateProfileRequest.class);
        verify(profileService).update(eq(USER_ID), captor.capture());
        assertThat(captor.getValue().firstName()).isEqualTo("Петр");
        assertThat(captor.getValue().phone()).isEqualTo("79991234567");
        assertThat(captor.getValue().lastName()).isNull();
    }

    @Test
    void updateProfile_whenValidationFails_returns400() throws Exception {
        mockMvc.perform(patch("/user/me")
                        .with(authenticated())
                        .contentType("application/json")
                        .content("""
                                {
                                  "firstName": "John"
                                }
                                """))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.error.code").value("VALIDATION_ERROR"));
    }

    // ---------- POST /user/me/avatar ----------

    @Test
    void uploadAvatar_uploadsAndReturnsUrl() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file", "avatar.jpg", "image/jpeg", new byte[]{1, 2, 3});
        when(profileService.uploadAvatar(eq(USER_ID), any())).thenReturn(AVATAR_URL);

        mockMvc.perform(multipart("/user/me/avatar")
                        .file(file)
                        .with(authenticated()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data").value(AVATAR_URL));

        verify(profileService).uploadAvatar(eq(USER_ID), any());
    }

    @Test
    void uploadAvatar_whenFileTooLarge_returns413() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file", "avatar.jpg", "image/jpeg", new byte[]{1, 2, 3});
        when(profileService.uploadAvatar(eq(USER_ID), any()))
                .thenThrow(new UniversalExeption("File to large (max 5MB).", "FILE_TOO_LARGE", HttpStatus.CONTENT_TOO_LARGE));

        mockMvc.perform(multipart("/user/me/avatar")
                        .file(file)
                        .with(authenticated()))
                .andExpect(status().is(413))
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.error.code").value("FILE_TOO_LARGE"));
    }

    @Test
    void uploadAvatar_whenInvalidFileType_returns415() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file", "avatar.txt", "text/plain", new byte[]{1, 2, 3});
        when(profileService.uploadAvatar(eq(USER_ID), any()))
                .thenThrow(new UniversalExeption("Only images are allowed.", "INVALID_FILE_TYPE", HttpStatus.UNSUPPORTED_MEDIA_TYPE));

        mockMvc.perform(multipart("/user/me/avatar")
                        .file(file)
                        .with(authenticated()))
                .andExpect(status().is(415))
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.error.code").value("INVALID_FILE_TYPE"));
    }

    @Test
    void uploadAvatar_whenFileParamMissing_returns400() throws Exception {
        mockMvc.perform(multipart("/user/me/avatar").with(authenticated()))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.error.code").value("MISSING_FILE"));
    }
}