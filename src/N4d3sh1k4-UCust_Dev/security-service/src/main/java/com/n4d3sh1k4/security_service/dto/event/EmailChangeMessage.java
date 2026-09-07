package com.n4d3sh1k4.security_service.dto.event;

import java.util.UUID;

public record EmailChangeMessage(
        String email,
        String token,
        String code,
        UUID userId
) {}
