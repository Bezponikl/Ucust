package com.n4d3sh1k4.business_service.domain.model.project;

import com.n4d3sh1k4.business_service.domain.model.project.support.BusinessHours;
import com.n4d3sh1k4.business_service.domain.model.project.support.Industry;
import com.n4d3sh1k4.business_service.domain.model.project.support.SocialLinks;
import com.n4d3sh1k4.business_service.domain.model.project.support.ToneOfVoice;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.util.UUID;

@Entity
@Getter
@Setter
public class Project {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    private String name;
    @Enumerated(EnumType.STRING)
    private Industry industry;
    private String city;
    private String description;
    private String targetAudience;

    @Enumerated(EnumType.STRING)
    private ToneOfVoice toneOfVoice;

    @Embedded
    private SocialLinks socialLinks;

    @Embedded
    private BusinessHours businessHours;

    private String logoUrl;
    private UUID ownerId;
}
