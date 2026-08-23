package com.n4d3sh1k4.common.exception;

import org.springframework.http.HttpStatus;

public class UserAlreadyExistsException extends BaseException {
    public UserAlreadyExistsException(String message) {
        super(message, "USER_ALREADY_EXISTS", HttpStatus.CONFLICT);
    }
}