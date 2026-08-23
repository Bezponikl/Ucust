package com.n4d3sh1k4.business_service.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Pattern;

@Schema(description = "Ссылки на соцсети")
public record SocialLinksRequest(
    @Schema(description = "Instagram (должен начинаться с https://)", example = "https://instagram.com/mybusiness")
    @Pattern(regexp = "^https://.*") String instagram,

    @Schema(description = "Telegram", example = "https://t.me/mybusiness")
    String telegram,

    @Schema(description = "Веб-сайт", example = "https://mybusiness.ru")
    String website
) {}
