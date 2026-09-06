package com.n4d3sh1k4.business_service.mapper;

import com.n4d3sh1k4.business_service.domain.model.project.Project;
import com.n4d3sh1k4.business_service.domain.model.project.support.BusinessHours;
import com.n4d3sh1k4.business_service.domain.model.project.support.Industry;
import com.n4d3sh1k4.business_service.domain.model.project.support.SocialLinks;
import com.n4d3sh1k4.business_service.domain.model.project.support.ToneOfVoice;
import com.n4d3sh1k4.business_service.dto.BusinessHoursRequest;
import com.n4d3sh1k4.business_service.dto.ProjectRequest;
import com.n4d3sh1k4.business_service.dto.ProjectResponse;
import com.n4d3sh1k4.business_service.dto.SocialLinksRequest;
import com.n4d3sh1k4.business_service.dto.UpdateProjectRequest;
import java.time.DayOfWeek;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.UUID;
import javax.annotation.processing.Generated;
import org.springframework.stereotype.Component;

@Generated(
    value = "org.mapstruct.ap.MappingProcessor",
    date = "2026-08-27T01:50:10+0300",
    comments = "version: 1.6.3, compiler: IncrementalProcessingEnvironment from gradle-language-java-9.0.0.jar, environment: Java 25.0.1 (Eclipse Adoptium)"
)
@Component
public class ProjectMapperImpl extends ProjectMapper {

    @Override
    public ProjectResponse toResponse(Project entity) {
        if ( entity == null ) {
            return null;
        }

        String logoUrl = null;
        UUID id = null;
        String name = null;
        Industry industry = null;
        String city = null;
        String description = null;
        String targetAudience = null;
        ToneOfVoice toneOfVoice = null;
        SocialLinks socialLinks = null;
        BusinessHours businessHours = null;
        UUID ownerId = null;

        logoUrl = toFullUrl( entity.getLogoUrl() );
        id = entity.getId();
        name = entity.getName();
        industry = entity.getIndustry();
        city = entity.getCity();
        description = entity.getDescription();
        targetAudience = entity.getTargetAudience();
        toneOfVoice = entity.getToneOfVoice();
        socialLinks = entity.getSocialLinks();
        businessHours = entity.getBusinessHours();
        ownerId = entity.getOwnerId();

        ProjectResponse projectResponse = new ProjectResponse( id, name, industry, city, description, targetAudience, toneOfVoice, socialLinks, businessHours, ownerId, logoUrl );

        return projectResponse;
    }

    @Override
    public Project toEntity(ProjectRequest dto) {
        if ( dto == null ) {
            return null;
        }

        Project project = new Project();

        project.setName( dto.name() );
        project.setIndustry( dto.industry() );
        project.setCity( dto.city() );
        project.setDescription( dto.description() );
        project.setTargetAudience( dto.targetAudience() );
        project.setToneOfVoice( dto.toneOfVoice() );
        project.setSocialLinks( socialLinksRequestToSocialLinks( dto.socialLinks() ) );
        project.setBusinessHours( businessHoursRequestToBusinessHours( dto.businessHours() ) );

        return project;
    }

    @Override
    public void updateEntity(UpdateProjectRequest dto, Project entity) {
        if ( dto == null ) {
            return;
        }

        if ( dto.name() != null ) {
            entity.setName( dto.name() );
        }
        if ( dto.industry() != null ) {
            entity.setIndustry( dto.industry() );
        }
        if ( dto.city() != null ) {
            entity.setCity( dto.city() );
        }
        if ( dto.description() != null ) {
            entity.setDescription( dto.description() );
        }
        if ( dto.targetAudience() != null ) {
            entity.setTargetAudience( dto.targetAudience() );
        }
        if ( dto.toneOfVoice() != null ) {
            entity.setToneOfVoice( dto.toneOfVoice() );
        }
        if ( dto.socialLinks() != null ) {
            if ( entity.getSocialLinks() == null ) {
                entity.setSocialLinks( new SocialLinks() );
            }
            updateSocialLinks( dto.socialLinks(), entity.getSocialLinks() );
        }
        if ( dto.businessHours() != null ) {
            if ( entity.getBusinessHours() == null ) {
                entity.setBusinessHours( new BusinessHours() );
            }
            updateBusinessHours( dto.businessHours(), entity.getBusinessHours() );
        }
    }

    @Override
    public void updateSocialLinks(SocialLinksRequest dto, SocialLinks entity) {
        if ( dto == null ) {
            return;
        }

        if ( dto.instagram() != null ) {
            entity.setInstagram( dto.instagram() );
        }
        if ( dto.telegram() != null ) {
            entity.setTelegram( dto.telegram() );
        }
        if ( dto.website() != null ) {
            entity.setWebsite( dto.website() );
        }
    }

    @Override
    public void updateBusinessHours(BusinessHoursRequest dto, BusinessHours entity) {
        if ( dto == null ) {
            return;
        }

        if ( dto.openTime() != null ) {
            entity.setOpenTime( dto.openTime() );
        }
        if ( dto.closeTime() != null ) {
            entity.setCloseTime( dto.closeTime() );
        }
        if ( entity.getOffDays() != null ) {
            List<DayOfWeek> list = dto.offDays();
            if ( list != null ) {
                entity.getOffDays().clear();
                entity.getOffDays().addAll( list );
            }
        }
        else {
            List<DayOfWeek> list = dto.offDays();
            if ( list != null ) {
                entity.setOffDays( new LinkedHashSet<DayOfWeek>( list ) );
            }
        }
    }

    protected SocialLinks socialLinksRequestToSocialLinks(SocialLinksRequest socialLinksRequest) {
        if ( socialLinksRequest == null ) {
            return null;
        }

        SocialLinks socialLinks = new SocialLinks();

        socialLinks.setInstagram( socialLinksRequest.instagram() );
        socialLinks.setTelegram( socialLinksRequest.telegram() );
        socialLinks.setWebsite( socialLinksRequest.website() );

        return socialLinks;
    }

    protected BusinessHours businessHoursRequestToBusinessHours(BusinessHoursRequest businessHoursRequest) {
        if ( businessHoursRequest == null ) {
            return null;
        }

        BusinessHours businessHours = new BusinessHours();

        businessHours.setOpenTime( businessHoursRequest.openTime() );
        businessHours.setCloseTime( businessHoursRequest.closeTime() );
        List<DayOfWeek> list = businessHoursRequest.offDays();
        if ( list != null ) {
            businessHours.setOffDays( new LinkedHashSet<DayOfWeek>( list ) );
        }

        return businessHours;
    }
}
