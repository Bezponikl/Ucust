package com.n4d3sh1k4.notification_service.dto;

import java.time.Instant;

public record LoginMessage(
        String email,
        String ipAddress,
        String userAgent,
        Instant timestamp
) {
}
