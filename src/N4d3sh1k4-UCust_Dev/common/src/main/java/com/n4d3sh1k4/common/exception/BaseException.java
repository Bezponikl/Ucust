package com.n4d3sh1k4.common.exception;

import org.springframework.http.HttpStatus;

public class BaseException extends RuntimeException {
    private final String message;
    private final String code;
    private final HttpStatus status;

    public BaseException(String message, String code, HttpStatus status) {
        this.message = message;
        this.code = code;
        this.status = status;
    }

    public String getCode() { return code; }
    public HttpStatus getStatus() { return status; }
    public String getMessage() { return message; }
}
