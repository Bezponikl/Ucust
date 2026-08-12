package com.n4d3sh1k4.notification_service.dto;

import java.util.UUID;

public record EmailChangeMessage(
        String email,
        String token,
        String code,
        UUID userId
) {}
