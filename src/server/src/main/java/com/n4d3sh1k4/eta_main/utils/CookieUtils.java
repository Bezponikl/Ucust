package com.n4d3sh1k4.eta_main.utils;

import com.n4d3sh1k4.eta_main.domain.model.users.User;
import com.n4d3sh1k4.eta_main.service.RefreshTokenService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseCookie;
import org.springframework.stereotype.Component;

@Component
public class CookieUtils {

    private final String cookieName = "refreshToken";

    private final RefreshTokenService refreshTokenService;

    @Value("${cookie.secure.state}")
    private Boolean cookieSecureState;

    public CookieUtils(RefreshTokenService refreshTokenService) {
        this.refreshTokenService = refreshTokenService;
    }

    public ResponseCookie generateRefreshTokenCookie(User user) {
        return ResponseCookie.from(cookieName, refreshTokenService.createRefreshToken(user).getToken())
                .httpOnly(true)
                .secure(cookieSecureState)
                .sameSite("None")
                .path("/api/vTest")
                .maxAge(30 * 24 * 60 * 60) // 30 дней
                .build();
    }

    public ResponseCookie getCleanRefreshTokenCookie() {
        return ResponseCookie.from(cookieName, "")
                .path("/api/vTest")
                .maxAge(0) // Удаляет куку у клиента
                .build();
    }
}