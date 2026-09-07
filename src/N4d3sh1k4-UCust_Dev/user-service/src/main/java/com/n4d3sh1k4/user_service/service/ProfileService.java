package com.n4d3sh1k4.user_service.service;

import com.n4d3sh1k4.common.exception.UniversalExeption;
import com.n4d3sh1k4.common.exception.UserNotFoundException;
import com.n4d3sh1k4.user_service.domain.model.UserProfile;
import com.n4d3sh1k4.user_service.domain.repository.UserProfileRepository;
import com.n4d3sh1k4.user_service.dto.ProfileResponse;
import com.n4d3sh1k4.user_service.dto.UpdateProfileRequest;
import com.n4d3sh1k4.user_service.mapper.ProfileMapper;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class ProfileService {

    @Value("${minio.base.path}")
    private String bucketPath;

    private final ProfileMapper profileMapper;
    private final UserProfileRepository userProfileRepository;
    private final MinioService minioService;

    @Transactional
    public ProfileResponse getProfile(UUID userId) {
        UserProfile user = userProfileRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("User not found"));
        return profileMapper.toResponse(user);
    }

    @Transactional
    public ProfileResponse update(UUID userId, UpdateProfileRequest request) {
        UserProfile user = userProfileRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("User not found"));
        profileMapper.updateEntityFromRequest(request, user);
        return profileMapper.toResponse(user);
    }

    @Transactional
    public String uploadAvatar(UUID userId, MultipartFile file) {
        UserProfile user = userProfileRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("User not found"));
        validateAvatar(file);
        if (user.getAvatarUrl() != null) {
            minioService.deleteFile(user.getAvatarUrl());
        }
        String url = "avatars/" + userId;
        minioService.uploadFile(file, url);
        user.setAvatarUrl(url);
        userProfileRepository.save(user);
        return bucketPath + url;
    }

    private void validateAvatar(MultipartFile file) {
        if (file.getSize() > 5 * 1024 * 1024) {
            throw new UniversalExeption("File to large (max 5MB).", "FILE_TOO_LARGE", HttpStatus.CONTENT_TOO_LARGE);
        }
        String contentType = file.getContentType();
        if (contentType != null && contentType.startsWith("image/")) {
            return;
        }
        try (InputStream in = file.getInputStream()) {
            if (isImageSignature(in.readNBytes(12))) {
                return;
            }
        } catch (IOException ignored) {
        }
        throw new UniversalExeption("Only images are allowed.", "INVALID_FILE_TYPE", HttpStatus.UNSUPPORTED_MEDIA_TYPE);
    }

    private static boolean isImageSignature(byte[] b) {
        if (b.length >= 4 && (b[0] & 0xFF) == 0x89 && b[1] == 0x50 && b[2] == 0x4E && b[3] == 0x47) return true;
        if (b.length >= 3 && (b[0] & 0xFF) == 0xFF && (b[1] & 0xFF) == 0xD8 && (b[2] & 0xFF) == 0xFF) return true;
        if (b.length >= 4 && b[0] == 'G' && b[1] == 'I' && b[2] == 'F' && b[3] == '8') return true;
        return b.length >= 12 && b[0] == 'R' && b[1] == 'I' && b[2] == 'F' && b[3] == 'F'
                && b[8] == 'W' && b[9] == 'E' && b[10] == 'B' && b[11] == 'P';
    }
}