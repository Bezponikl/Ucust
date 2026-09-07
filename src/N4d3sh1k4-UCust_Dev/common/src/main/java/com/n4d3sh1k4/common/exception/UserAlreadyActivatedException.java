package com.n4d3sh1k4.common.exception;

import org.springframework.http.HttpStatus;

public class UserAlreadyActivatedException extends BaseException {
    public UserAlreadyActivatedException(String message) {
        super(message, "USER_ALREADY_ACTIVATED", HttpStatus.CONFLICT);
    }
}