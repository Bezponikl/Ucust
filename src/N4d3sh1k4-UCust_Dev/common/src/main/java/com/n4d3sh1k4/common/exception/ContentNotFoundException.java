package com.n4d3sh1k4.common.exception;

import org.springframework.http.HttpStatus;

public class ContentNotFoundException extends BaseException {
    public ContentNotFoundException(String message) {
        super(message, "NOT_FOUND", HttpStatus.NOT_FOUND);
    }
}