package com.n4d3sh1k4.eta_main.exception;

public class TokenExpiredException extends RuntimeException{
    public TokenExpiredException(String message) {
        super(message);
    }

    public TokenExpiredException() {
        super();
    }
}
