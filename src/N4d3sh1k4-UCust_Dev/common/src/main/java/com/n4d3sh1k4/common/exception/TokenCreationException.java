package com.n4d3sh1k4.common.exception;

import org.springframework.http.HttpStatus;

public class TokenCreationException extends BaseException {
    public TokenCreationException(String message) {
        super(message, "TOKEN_GENERATION_FAILED", HttpStatus.INTERNAL_SERVER_ERROR);
    }
}