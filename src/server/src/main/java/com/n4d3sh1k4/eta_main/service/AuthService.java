package com.n4d3sh1k4.eta_main.service;

import com.n4d3sh1k4.eta_main.domain.model.security.PasswordResetToken;
import com.n4d3sh1k4.eta_main.domain.model.users.User;
import com.n4d3sh1k4.eta_main.domain.repository.PasswordResetTokenRepository;
import com.n4d3sh1k4.eta_main.domain.repository.RoleRepository;
import com.n4d3sh1k4.eta_main.domain.repository.UserRepository;
import com.n4d3sh1k4.eta_main.dto.request_dto.LoginRequest;
import com.n4d3sh1k4.eta_main.dto.request_dto.RegisterRequest;
import com.n4d3sh1k4.eta_main.dto.AuthServiceResult;
import com.n4d3sh1k4.eta_main.exception.BadCredentialsException;

import com.n4d3sh1k4.eta_main.exception.TokenNotFoundException;
import com.n4d3sh1k4.eta_main.exception.UserAlreadyExistsException;
import com.n4d3sh1k4.eta_main.jwt.JwtProvider;
import com.n4d3sh1k4.eta_main.utils.CookieUtils;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    private final PasswordResetTokenRepository passwordResetTokenRepository;

    private final RefreshTokenService refreshTokenService;
    private final EmailService emailService;

    private final PasswordEncoder passwordEncoder;
    private final JwtProvider jwtProvider;
    private final CookieUtils cookieUtils;
    private final AuthenticationManager authenticationManager;

    @Transactional
    public AuthServiceResult registerUser(RegisterRequest req) {
        if (userRepository.findByEmail(req.getEmail()).isPresent()) {
            throw new UserAlreadyExistsException("A user with this email already exists!");
        }

        String encodedPassword = passwordEncoder.encode(req.getPassword());

        User user = new User();
        user.setUsername(req.getUsername());
        user.setEmail(req.getEmail());
        user.setPasswordHash(encodedPassword);
        user.setRoles(roleRepository.findByName("USER"));
        userRepository.save(user);

        return new AuthServiceResult(
                jwtProvider.generateAccessToken(user),
                cookieUtils.generateRefreshTokenCookie(user).toString()
        );
    }

    @Transactional
    public AuthServiceResult loginUser(LoginRequest req) {
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(req.getEmail(), req.getPassword()));
        SecurityContextHolder.getContext().setAuthentication(authentication);

        User user = userRepository.findByEmail(req.getEmail()).orElseThrow();

        return new AuthServiceResult(
                jwtProvider.generateAccessToken(user),
                cookieUtils.generateRefreshTokenCookie(user).toString()
        );
    }

    @Transactional
    public AuthServiceResult logoutUser(String refreshToken) {
        if (refreshToken == null) {
            throw new BadCredentialsException("You are already logged out");
        }
        refreshTokenService.deleteByUser(refreshTokenService.findByToken(refreshToken).get().getUser());
        return new AuthServiceResult(
                cookieUtils.getCleanRefreshTokenCookie().toString()
        );
    }

    @Transactional
    public AuthServiceResult refreshToken(String refreshToken) {
        User user = refreshTokenService.findByToken(refreshToken).orElseThrow(TokenNotFoundException::new).getUser();
        return new AuthServiceResult(
                jwtProvider.generateAccessToken(user),
                cookieUtils.generateRefreshTokenCookie(user).toString()
        );
    }

    public void createPasswordResetToken(String email) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));
        passwordResetTokenRepository.deleteByUser(user);
        String token = UUID.randomUUID().toString();
        PasswordResetToken myToken = new PasswordResetToken();
        myToken.setToken(token);
        myToken.setUser(user);
        myToken.setExpiryDate(LocalDateTime.now().plusMinutes(15));
        passwordResetTokenRepository.save(myToken);
        emailService.sendResetTokenEmail(user.getEmail(), token);
    }

    @Transactional
    public void resetPassword(String token, String newPassword) {
        PasswordResetToken resetToken = passwordResetTokenRepository.findByToken(token)
                .orElseThrow(() -> new RuntimeException("Invalid token"));

        if (resetToken.isExpired()) {
            passwordResetTokenRepository.delete(resetToken);
            throw new RuntimeException("Token expired");
        }
        User user = resetToken.getUser();
        user.setPasswordHash(passwordEncoder.encode(newPassword));
        userRepository.save(user);
        refreshTokenService.deleteByUser(user);
        passwordResetTokenRepository.delete(resetToken);
    }
}