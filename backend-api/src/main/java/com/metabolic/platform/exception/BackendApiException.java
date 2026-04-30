package com.metabolic.platform.exception;

public class BackendApiException extends RuntimeException {
    public BackendApiException(String message) {
        super(message);
    }

    public BackendApiException(String message, Throwable cause) {
        super(message, cause);
    }
}
