package com.n4d3sh1k4.business_service.dto;

import com.n4d3sh1k4.business_service.domain.model.project.support.Industry;
import com.n4d3sh1k4.business_service.domain.model.project.support.ToneOfVoice;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record ProjectRequest(
    @NotBlank
    @Size(min = 2, max = 100)
    String name,
    @NotNull
    Industry industry,
    @NotBlank
    @Size(max = 50)
    String city,
    @Size(max = 2000)
    String description,
    @Size(max = 500)
    String targetAudience,
    @NotNull
    ToneOfVoice toneOfVoice,
    @Valid
    SocialLinksRequest socialLinks,
    @Valid
    BusinessHoursRequest businessHours
) {}