package com.n4d3sh1k4.eta_main.exception;

public class TokenNotFoundException extends RuntimeException {
    public TokenNotFoundException(String message) {
        super(message);
    }

    public TokenNotFoundException() {
        super();
    }
}
