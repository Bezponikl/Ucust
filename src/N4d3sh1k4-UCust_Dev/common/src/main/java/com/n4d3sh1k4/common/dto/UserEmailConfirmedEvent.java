package com.n4d3sh1k4.common.dto;

import java.util.UUID;

public record UserEmailConfirmedEvent(
        UUID userId,
        String email
) {}
