package com.n4d3sh1k4.user_service.mapper;

import com.n4d3sh1k4.user_service.domain.model.UserProfile;
import com.n4d3sh1k4.user_service.dto.ProfileResponse;
import com.n4d3sh1k4.user_service.dto.UpdateProfileRequest;
import org.mapstruct.*;
import org.springframework.beans.factory.annotation.Value;

@Mapper(
    componentModel = "spring",
    nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE
)
public abstract class ProfileMapper {

    @Value("${minio.base.path}")
    protected String bucketPath;

    @Value("${minio.base.avatar:b84e7c4a19b762c769541cd557e97f7f.png}")
    protected String defaultAvatar;

    // 1. Маппинг из Entity в Response
    // Мы указываем, что поле fullAvatarUrl должно формироваться методом toFullUrl
    @Mapping(target = "fullAvatarUrl", source = "avatarUrl", qualifiedByName = "toFullAvatarUrl")
    public abstract ProfileResponse toResponse(UserProfile entity);

    // 2. Обновление Entity из Request
    // Игнорируем поля, чтобы не было варнингов и случайных перезатираний
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "email", ignore = true)
    @Mapping(target = "avatarUrl", ignore = true)
    public abstract void updateEntityFromRequest(UpdateProfileRequest dto, @MappingTarget UserProfile entity);

    // Логика формирования ссылки
    @Named("toFullAvatarUrl")
    protected String toFullAvatarUrl(String avatarUrl) {
        if (avatarUrl != null && !avatarUrl.isBlank()) {
            return bucketPath + avatarUrl;
        }
        return bucketPath + defaultAvatar;
    }
}