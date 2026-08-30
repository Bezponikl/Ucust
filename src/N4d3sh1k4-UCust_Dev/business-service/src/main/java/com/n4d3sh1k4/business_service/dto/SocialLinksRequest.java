package com.n4d3sh1k4.business_service.dto;

import jakarta.validation.constraints.Pattern;

public record SocialLinksRequest(
    @Pattern(regexp = "^https://.*") String instagram,
    String telegram,
    String website
) {}
