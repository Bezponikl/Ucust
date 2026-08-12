package com.n4d3sh1k4.common.exception;

import org.springframework.http.HttpStatus;

public class PaymentRequiredException extends BaseException {
    public PaymentRequiredException(String message) {
        super(message, "PAYMENT_REQUIRED", HttpStatus.PAYMENT_REQUIRED);
    }
}