package com.n4d3sh1k4.eta_main.controller.user;

import com.n4d3sh1k4.eta_main.domain.repository.RoleRepository;
import com.n4d3sh1k4.eta_main.dto.*;
import com.n4d3sh1k4.eta_main.domain.repository.UserRepository;
import com.n4d3sh1k4.eta_main.dto.request_dto.ForgotPasswordRequest;
import com.n4d3sh1k4.eta_main.dto.request_dto.LoginRequest;
import com.n4d3sh1k4.eta_main.dto.request_dto.RegisterRequest;
import com.n4d3sh1k4.eta_main.dto.request_dto.ResetPasswordRequest;
import com.n4d3sh1k4.eta_main.jwt.JwtProvider;
import com.n4d3sh1k4.eta_main.security.UserDetailsServiceImpl;
import com.n4d3sh1k4.eta_main.service.AuthService;
import com.n4d3sh1k4.eta_main.service.RefreshTokenService;
import com.n4d3sh1k4.eta_main.utils.CookieUtils;
import jakarta.validation.Valid;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;

import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final AuthService authService;

    public AuthController(AuthenticationManager authenticationManager, RefreshTokenService refreshTokenService, UserRepository userRepository, UserDetailsServiceImpl userDetailsService, JwtProvider jwtProvider, UserDetailsServiceImpl userDetailsServiceImpl, PasswordEncoder passwordEncoder, RoleRepository roleRepository, CookieUtils cookieUtils, AuthService authService) {
        this.authenticationManager = authenticationManager;
        this.authService = authService;
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@Valid @RequestBody RegisterRequest req) {
        AuthServiceResult result = authService.registerUser(req);
        return ResponseEntity.ok()
                .header(HttpHeaders.SET_COOKIE, result.getCookie())
                .body(new JwtResponse(result.getAccesToken()));
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@Valid @RequestBody LoginRequest loginRequest) {
        Authentication authentication = authenticationManager.authenticate(new UsernamePasswordAuthenticationToken(loginRequest.getEmail(), loginRequest.getPassword()));
        SecurityContextHolder.getContext().setAuthentication(authentication);
        AuthServiceResult result = authService.loginUser(loginRequest);
        return ResponseEntity.ok()
                .header(HttpHeaders.SET_COOKIE, result.getCookie())
                .body(new JwtResponse(result.getAccesToken()));
    }

    @PostMapping("/logout")
    public ResponseEntity<?> logout(@CookieValue(name = "refreshToken", required = false) String refreshToken) {
        AuthServiceResult result = authService.logoutUser(refreshToken);
        return ResponseEntity.ok()
                .header(HttpHeaders.SET_COOKIE, result.getCookie())
                .body("Logged out successfully");
    }

    @PostMapping("/refresh")
    public ResponseEntity<?> refresh(@CookieValue(name = "refreshToken", required = false) String refreshToken) {
        if (refreshToken == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        AuthServiceResult result = authService.refreshToken(refreshToken);
        return ResponseEntity.ok()
                .header(HttpHeaders.SET_COOKIE, result.getCookie())
                .body(new JwtResponse(result.getAccesToken()));
    }

    @PostMapping("/forgot-password")
    public ResponseEntity<?> forgotPassword(@Valid @RequestBody ForgotPasswordRequest request) {
        authService.createPasswordResetToken(request.getEmail());
        return ResponseEntity.ok(HttpStatus.OK);
    }

    @PostMapping("/reset-password")
    public ResponseEntity<?> resetPassword(@Valid @RequestBody ResetPasswordRequest request) {
        authService.resetPassword(request.getToken(), request.getNewPassword());
        return ResponseEntity.ok(HttpStatus.OK);
    }

    @GetMapping("/check-me")
    public String checkMe(Authentication authentication) {
        return "Your authorities: " + authentication.getAuthorities();
    }
}