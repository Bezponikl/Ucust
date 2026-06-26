package com.n4d3sh1k4.business_service.dto;

import com.n4d3sh1k4.business_service.domain.model.project.support.BusinessHours;
import com.n4d3sh1k4.business_service.domain.model.project.support.Industry;
import com.n4d3sh1k4.business_service.domain.model.project.support.SocialLinks;
import com.n4d3sh1k4.business_service.domain.model.project.support.ToneOfVoice;

import java.util.UUID;

public record ProjectResponse(
    UUID id,
    String name,
    Industry industry,
    String city,
    String description,
    String targetAudience,
    ToneOfVoice toneOfVoice,
    SocialLinks socialLinks,
    BusinessHours businessHours,
    UUID ownerId,
    String logoUrl
) {}
