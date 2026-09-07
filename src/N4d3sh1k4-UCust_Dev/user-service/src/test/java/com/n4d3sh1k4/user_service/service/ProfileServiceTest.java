package com.n4d3sh1k4.user_service.service;

import com.n4d3sh1k4.common.exception.UniversalExeption;
import com.n4d3sh1k4.common.exception.UserNotFoundException;
import com.n4d3sh1k4.user_service.domain.model.UserProfile;
import com.n4d3sh1k4.user_service.domain.repository.UserProfileRepository;
import com.n4d3sh1k4.user_service.dto.ProfileResponse;
import com.n4d3sh1k4.user_service.dto.UpdateProfileRequest;
import com.n4d3sh1k4.user_service.mapper.ProfileMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;
import org.springframework.http.HttpStatus;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.multipart.MultipartFile;

import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class ProfileServiceTest {

    private static final UUID USER_ID = UUID.fromString("550e8400-e29b-41d4-a716-446655440000");
    private static final String BUCKET_PATH = "http://minio:9000/user-service/";

    @Mock
    private ProfileMapper profileMapper;

    @Mock
    private UserProfileRepository userProfileRepository;

    @Mock
    private MinioService minioService;

    @InjectMocks
    private ProfileService profileService;

    private UserProfile user;
    private ProfileResponse response;

    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(profileService, "bucketPath", BUCKET_PATH);

        user = new UserProfile();
        user.setId(USER_ID);
        user.setFirstName("Олег");
        user.setLastName("Иванов");
        user.setEmail("user@example.com");
        user.setPhone("79991234567");
        user.setPosition("Разработчик");
        user.setAvatarUrl(null);

        response = new ProfileResponse(
                USER_ID, "Олег", "Иванович" ,"Иванов", "user@example.com",
                "79991234567", "Разработчик", BUCKET_PATH + "avatars/avatar.jpg");
    }

    private MockMultipartFile avatarFile(String name, String contentType, byte[] content) {
        return new MockMultipartFile("file", name, contentType, content);
    }

    // ---------- getProfile ----------

    @Test
    void getProfile_whenUserFound_returnsMappedResponse() {
        when(userProfileRepository.findById(USER_ID)).thenReturn(Optional.of(user));
        when(profileMapper.toResponse(user)).thenReturn(response);

        ProfileResponse result = profileService.getProfile(USER_ID);

        assertThat(result).isEqualTo(response);
        verify(profileMapper).toResponse(user);
    }

    @Test
    void getProfile_whenUserNotFound_throwsUserNotFound() {
        when(userProfileRepository.findById(USER_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> profileService.getProfile(USER_ID))
                .isInstanceOf(UserNotFoundException.class);
    }

    // ---------- update ----------

    @Test
    void update_whenUserFound_updatesEntityAndReturnsResponse() {
        UpdateProfileRequest request = new UpdateProfileRequest("Петр", null, null, "79991234567", "Менеджер");
        when(userProfileRepository.findById(USER_ID)).thenReturn(Optional.of(user));
        when(profileMapper.toResponse(user)).thenReturn(response);

        ProfileResponse result = profileService.update(USER_ID, request);

        verify(profileMapper).updateEntityFromRequest(request, user);
        verify(profileMapper).toResponse(user);
        assertThat(result).isEqualTo(response);
    }

    @Test
    void update_whenUserNotFound_throwsUserNotFound() {
        when(userProfileRepository.findById(USER_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> profileService.update(USER_ID, new UpdateProfileRequest("Петр", null, null, null, null)))
                .isInstanceOf(UserNotFoundException.class);

        verify(profileMapper, never()).updateEntityFromRequest(any(), any());
    }

    // ---------- uploadAvatar ----------

    @Test
    void uploadAvatar_whenUserNotFound_throwsUserNotFound() {
        when(userProfileRepository.findById(USER_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> profileService.uploadAvatar(USER_ID, avatarFile("a.jpg", "image/jpeg", new byte[]{1})))
                .isInstanceOf(UserNotFoundException.class);
    }

    @Test
    void uploadAvatar_whenFileTooLarge_throwsFileTooLarge() {
        when(userProfileRepository.findById(USER_ID)).thenReturn(Optional.of(user));
        MultipartFile big = avatarFile("a.jpg", "image/jpeg", new byte[5 * 1024 * 1024 + 1]);

        assertThatThrownBy(() -> profileService.uploadAvatar(USER_ID, big))
                .isInstanceOf(UniversalExeption.class)
                .satisfies(e -> {
                    assertThat(((UniversalExeption) e).getCode()).isEqualTo("FILE_TOO_LARGE");
                    assertThat(((UniversalExeption) e).getStatus()).isEqualTo(HttpStatus.CONTENT_TOO_LARGE);
                });

        verify(minioService, never()).uploadFile(any(), anyString());
        verify(userProfileRepository, never()).save(any(UserProfile.class));
    }

    @Test
    void uploadAvatar_whenNotAnImage_throwsInvalidFileType() {
        when(userProfileRepository.findById(USER_ID)).thenReturn(Optional.of(user));
        MultipartFile text = avatarFile("a.txt", "text/plain", new byte[]{1, 2, 3});

        assertThatThrownBy(() -> profileService.uploadAvatar(USER_ID, text))
                .isInstanceOf(UniversalExeption.class)
                .satisfies(e -> {
                    assertThat(((UniversalExeption) e).getCode()).isEqualTo("INVALID_FILE_TYPE");
                    assertThat(((UniversalExeption) e).getStatus()).isEqualTo(HttpStatus.UNSUPPORTED_MEDIA_TYPE);
                });
    }

    @Test
    void uploadAvatar_whenContentTypeNull_throwsInvalidFileType() {
        when(userProfileRepository.findById(USER_ID)).thenReturn(Optional.of(user));
        MultipartFile noType = avatarFile("a.jpg", null, new byte[]{1, 2, 3});

        assertThatThrownBy(() -> profileService.uploadAvatar(USER_ID, noType))
                .isInstanceOf(UniversalExeption.class)
                .satisfies(e -> {
                    assertThat(((UniversalExeption) e).getCode()).isEqualTo("INVALID_FILE_TYPE");
                    assertThat(((UniversalExeption) e).getStatus()).isEqualTo(HttpStatus.UNSUPPORTED_MEDIA_TYPE);
                });
    }

    @Test
    void uploadAvatar_whenOctetStreamButRealImage_passesValidation() {
        when(userProfileRepository.findById(USER_ID)).thenReturn(Optional.of(user));
        byte[] png = {(byte) 0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 1, 2, 3, 4};
        MultipartFile file = avatarFile("avatar.png", "application/octet-stream", png);

        profileService.uploadAvatar(USER_ID, file);

        verify(minioService, times(1)).uploadFile(eq(file), eq("avatars/" + USER_ID));
    }

    @Test
    void uploadAvatar_whenHasOldAvatar_deletesOldAndUploadsNew() {
        user.setAvatarUrl("avatars/old/old.jpg");
        when(userProfileRepository.findById(USER_ID)).thenReturn(Optional.of(user));
        when(minioService.uploadFile(any(MultipartFile.class), anyString()))
                .thenAnswer(inv -> inv.getArgument(1));
        MultipartFile file = avatarFile("avatar.jpg", "image/jpeg", new byte[]{1, 2, 3});

        String result = profileService.uploadAvatar(USER_ID, file);

        verify(minioService).deleteFile("avatars/old/old.jpg");
        verify(minioService, times(1)).uploadFile(eq(file), eq("avatars/" + USER_ID));
        assertThat(user.getAvatarUrl()).isEqualTo("avatars/" + USER_ID);
        assertThat(result).isEqualTo(BUCKET_PATH + "avatars/" + USER_ID);
        verify(userProfileRepository).save(user);
    }

    @Test
    void uploadAvatar_whenNoOldAvatar_doesNotDelete() {
        when(userProfileRepository.findById(USER_ID)).thenReturn(Optional.of(user));
        when(minioService.uploadFile(any(MultipartFile.class), anyString()))
                .thenAnswer(inv -> inv.getArgument(1));
        MultipartFile file = avatarFile("avatar.jpg", "image/jpeg", new byte[]{1, 2, 3});

        profileService.uploadAvatar(USER_ID, file);

        verify(minioService, never()).deleteFile(anyString());
        assertThat(user.getAvatarUrl()).isEqualTo("avatars/" + USER_ID);
    }
}