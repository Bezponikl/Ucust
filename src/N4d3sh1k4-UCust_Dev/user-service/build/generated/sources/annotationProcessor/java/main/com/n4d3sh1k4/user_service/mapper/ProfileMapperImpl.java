package com.n4d3sh1k4.user_service.mapper;

import com.n4d3sh1k4.user_service.domain.model.UserProfile;
import com.n4d3sh1k4.user_service.dto.ProfileResponse;
import com.n4d3sh1k4.user_service.dto.UpdateProfileRequest;
import java.util.UUID;
import javax.annotation.processing.Generated;
import org.springframework.stereotype.Component;

@Generated(
    value = "org.mapstruct.ap.MappingProcessor",
    date = "2026-08-27T02:32:50+0300",
    comments = "version: 1.6.3, compiler: IncrementalProcessingEnvironment from gradle-language-java-9.0.0.jar, environment: Java 25.0.1 (Eclipse Adoptium)"
)
@Component
public class ProfileMapperImpl extends ProfileMapper {

    @Override
    public ProfileResponse toResponse(UserProfile entity) {
        if ( entity == null ) {
            return null;
        }

        String fullAvatarUrl = null;
        UUID id = null;
        String firstName = null;
        String middleName = null;
        String lastName = null;
        String email = null;
        String phone = null;
        String position = null;

        fullAvatarUrl = toFullAvatarUrl( entity.getAvatarUrl() );
        id = entity.getId();
        firstName = entity.getFirstName();
        middleName = entity.getMiddleName();
        lastName = entity.getLastName();
        email = entity.getEmail();
        phone = entity.getPhone();
        position = entity.getPosition();

        ProfileResponse profileResponse = new ProfileResponse( id, firstName, middleName, lastName, email, phone, position, fullAvatarUrl );

        return profileResponse;
    }

    @Override
    public void updateEntityFromRequest(UpdateProfileRequest dto, UserProfile entity) {
        if ( dto == null ) {
            return;
        }

        if ( dto.firstName() != null ) {
            entity.setFirstName( dto.firstName() );
        }
        if ( dto.middleName() != null ) {
            entity.setMiddleName( dto.middleName() );
        }
        if ( dto.lastName() != null ) {
            entity.setLastName( dto.lastName() );
        }
        if ( dto.phone() != null ) {
            entity.setPhone( dto.phone() );
        }
        if ( dto.position() != null ) {
            entity.setPosition( dto.position() );
        }
    }
}
