package com.n4d3sh1k4.common.exception;

import org.springframework.http.HttpStatus;

public class TooManyRequestsException extends BaseException {
    public TooManyRequestsException(String message) {
        super(message, "RATE_LIMIT_EXCEEDED", HttpStatus.TOO_MANY_REQUESTS);
    }
}
