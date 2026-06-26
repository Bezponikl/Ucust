package com.n4d3sh1k4.common.exception;

import org.springframework.http.HttpStatus;

public class TokenNotFoundException extends BaseException {
    public TokenNotFoundException(String message, String code, HttpStatus status) {
        super(message, code, status);
    }

}
