package com.n4d3sh1k4.common.advice;

import com.n4d3sh1k4.common.dto.ApiError;
import com.n4d3sh1k4.common.dto.ApiResponse;
import com.n4d3sh1k4.common.exception.BaseException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.DisabledException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.nio.file.AccessDeniedException;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BaseException.class)
    public ResponseEntity<ApiResponse<Void>> handleBaseException(BaseException ex) {
        return ResponseEntity
                .status(ex.getStatus())
                .body(ApiResponse.error(ex.getCode(), ex.getMessage()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidation(MethodArgumentNotValidException ex) {
        String errorMessage = ex.getBindingResult().getFieldErrors().get(0).getDefaultMessage();
        return ResponseEntity
                .status(400)
                .body(ApiResponse.error("VALIDATION_ERROR", errorMessage));
    }

    @ExceptionHandler(BadCredentialsException.class)
    public ResponseEntity<ApiResponse<Void>> handleBadCredentialsException(BadCredentialsException ex) {
        return ResponseEntity
                .status(HttpStatus.UNAUTHORIZED) // Код 401
                .body(ApiResponse.error("AUTH_ERROR", "Incorrect credentials"));
    }

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ApiResponse<Void>> handleAccessDeniedException(AccessDeniedException ex) {
        return ResponseEntity
                .status(HttpStatus.FORBIDDEN) // Код 403
                .body(ApiResponse.error("ACCESS_DENIED", "You do not have sufficient permissions to perform this operation."));
    }

    @ExceptionHandler(DisabledException.class)
    public ResponseEntity<ApiResponse<Void>> handleDisabledException(DisabledException ex) {
        ApiError error = new ApiError(
                "EMAIL_NOT_VERIFIED",
                "Your account is not activated. Please confirm your email."
        );
        return new ResponseEntity<>(new ApiResponse<>(false, null, error, null), HttpStatus.FORBIDDEN);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleGeneralException(Exception ex) {
        ex.printStackTrace();
        return ResponseEntity
                .status(500)
                .body(ApiResponse.error("INTERNAL_SERVER_ERROR", "Server error " + ex.getMessage()));
    }
}