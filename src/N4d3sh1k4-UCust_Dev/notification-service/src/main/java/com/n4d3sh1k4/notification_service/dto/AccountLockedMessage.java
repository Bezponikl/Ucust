package com.n4d3sh1k4.notification_service.dto;

import java.time.Instant;

public record AccountLockedMessage(String email, Instant timestamp) {
}
