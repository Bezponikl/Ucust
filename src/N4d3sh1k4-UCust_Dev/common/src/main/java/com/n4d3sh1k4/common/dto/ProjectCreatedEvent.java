package com.n4d3sh1k4.common.dto;

import java.util.UUID;

public record ProjectCreatedEvent(
        UUID projectId,
        UUID userId,
        String industry,
        String description,
        String targetAudience,
        String toneOfVoice,
        String city,
        int postCount
) {}
