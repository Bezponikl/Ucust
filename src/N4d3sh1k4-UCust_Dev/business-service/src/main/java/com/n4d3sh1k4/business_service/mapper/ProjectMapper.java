package com.n4d3sh1k4.business_service.mapper;

import com.n4d3sh1k4.business_service.domain.model.project.Project;
import com.n4d3sh1k4.business_service.domain.model.project.support.BusinessHours;
import com.n4d3sh1k4.business_service.domain.model.project.support.SocialLinks;
import com.n4d3sh1k4.business_service.dto.*;
import org.mapstruct.*;
import org.springframework.beans.factory.annotation.Value;

@Mapper(componentModel = "spring", nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
public abstract class ProjectMapper {

    @Value("${minio.default.path}")
    protected String bucketPath;

    @Value("${minio.default.logo}")
    protected String defaultLogo;

    @Mapping(target = "logoUrl", source = "logoUrl", qualifiedByName = "toFullUrl")
    public abstract ProjectResponse toResponse(Project entity);

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "logoUrl", ignore = true)
    @Mapping(target = "ownerId", ignore = true)
    public abstract Project toEntity(ProjectRequest dto);

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "logoUrl", ignore = true)
    @Mapping(target = "ownerId", ignore = true)
    public abstract void updateEntity(UpdateProjectRequest dto, @MappingTarget Project entity);

    public abstract void updateSocialLinks(SocialLinksRequest dto, @MappingTarget SocialLinks entity);

    public abstract void updateBusinessHours(BusinessHoursRequest dto, @MappingTarget BusinessHours entity);

    @Named("toFullUrl")
    protected String toFullUrl(String logoPath) {
        if (logoPath != null && !logoPath.isBlank()) {
            return bucketPath + logoPath;
        }
        return bucketPath + defaultLogo;
    }
}