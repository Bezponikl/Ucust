package com.n4d3sh1k4.business_service.domain.model.project.support;

import jakarta.persistence.Embeddable;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Embeddable
@Getter
@Setter
@NoArgsConstructor // Тот самый пустой конструктор, который просит MapStruct
@AllArgsConstructor
public class SocialLinks {
    private String instagram;
    private String telegram;
    private String website;
}