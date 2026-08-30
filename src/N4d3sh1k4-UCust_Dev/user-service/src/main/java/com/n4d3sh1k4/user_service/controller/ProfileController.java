package com.n4d3sh1k4.user_service.controller;

import com.n4d3sh1k4.common.dto.ApiResponse;
import com.n4d3sh1k4.user_service.dto.ProfileResponse;
import com.n4d3sh1k4.user_service.dto.UpdateProfileRequest;
import com.n4d3sh1k4.user_service.dto.UserPrincipal;
import com.n4d3sh1k4.user_service.service.ProfileService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/user")
@RequiredArgsConstructor
public class ProfileController {

    private final ProfileService profileService;

    @GetMapping("/me")
    public ProfileResponse getMyProfile(@AuthenticationPrincipal UserPrincipal principal) {
        return profileService.getProfile(principal.id());
    }

    @PatchMapping("/me")
    public ProfileResponse updateProfile(
            @AuthenticationPrincipal UserPrincipal principal,
            @Valid @RequestBody UpdateProfileRequest request) {
        return profileService.update(principal.id(), request);
    }

    @PostMapping(value = "/me/avatar", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ApiResponse<String> uploadAvatar(
            @AuthenticationPrincipal UserPrincipal principal,
            @RequestParam("file") MultipartFile file) {
        return ApiResponse.success(profileService.uploadAvatar(principal.id(), file));
    }
}