package com.metabolic.platform.exception;

public class OrchestratorCommunicationException extends BackendApiException {
    public OrchestratorCommunicationException(String message) {
        super(message);
    }

    public OrchestratorCommunicationException(String message, Throwable cause) {
        super(message, cause);
    }
}
