package com.n4d3sh1k4.user_service.controller;

import com.n4d3sh1k4.common.dto.ApiResponse;
import com.n4d3sh1k4.user_service.dto.ProfileResponse;
import com.n4d3sh1k4.user_service.dto.UpdateProfileRequest;
import com.n4d3sh1k4.user_service.dto.UserPrincipal;
import com.n4d3sh1k4.user_service.service.ProfileService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@Tag(name = "Профиль", description = "Управление профилем пользователя")
@RestController
@RequestMapping("/user")
@RequiredArgsConstructor
public class ProfileController {

    private final ProfileService profileService;

    @Operation(summary = "Получить профиль текущего пользователя",
               description = "Возвращает полную информацию о профиле авторизованного пользователя.")
    @GetMapping("/me")
    public ProfileResponse getMyProfile(@AuthenticationPrincipal UserPrincipal principal) {
        return profileService.getProfile(principal.id());
    }

    @Operation(summary = "Обновить профиль",
               description = "Позволяет изменить имя, фамилию, телефон и должность текущего пользователя.")
    @PatchMapping("/me")
    public ProfileResponse updateProfile(
            @AuthenticationPrincipal UserPrincipal principal,
            @Valid @RequestBody UpdateProfileRequest request) {
        return profileService.update(principal.id(), request);
    }

    @Operation(summary = "Загрузить аватар",
               description = "Загружает изображение аватара для текущего пользователя. Принимает multipart/form-data.")
    @PostMapping(value = "/me/avatar", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ApiResponse<String> uploadAvatar(
            @AuthenticationPrincipal UserPrincipal principal,
            @Parameter(description = "Файл изображения (JPEG, PNG)")
            @RequestParam("file") MultipartFile file) {
        return ApiResponse.success(profileService.uploadAvatar(principal.id(), file));
    }
}