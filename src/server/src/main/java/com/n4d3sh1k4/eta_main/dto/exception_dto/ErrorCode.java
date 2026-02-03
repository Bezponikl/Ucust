package com.n4d3sh1k4.eta_main.dto.exception_dto;

import lombok.Getter;

@Getter
public enum ErrorCode {
    USER_ALREADY_EXISTS("A user with this email already exists"),
    INVALID_CREDENTIALS("Incorrect login or password"),
    TOKEN_EXPIRED("Token has expired"),
    TOKEN_NOT_FOUND("Token not found"),
    VALIDATION_ERROR("Field validation error"),
    SERVER_ERROR("Internal server error"),
    USER_NOT_FOUND("The user was not found in the system");

    private final String defaultMessage;

    ErrorCode(String defaultMessage) {
        this.defaultMessage = defaultMessage;
    }

}