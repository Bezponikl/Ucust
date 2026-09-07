package com.n4d3sh1k4.security_service.security;

import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.user.DefaultOAuth2User;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class CustomOAuth2UserService extends DefaultOAuth2UserService {

    @Override
    public OAuth2User loadUser(OAuth2UserRequest userRequest) throws OAuth2AuthenticationException {
        OAuth2User oAuth2User = super.loadUser(userRequest);
        String clientRegistrationId = userRequest.getClientRegistration().getRegistrationId();

        if ("vk".equalsIgnoreCase(clientRegistrationId)) {
            Map<String, Object> attributes = oAuth2User.getAttributes();

            if (attributes.containsKey("response")) {
                List<Map<String, Object>> responseList = (List<Map<String, Object>>) attributes.get("response");
                if (responseList != null && !responseList.isEmpty()) {
                    Map<String, Object> vkUserAttributes = new HashMap<>(responseList.get(0));

                    Map<String, Object> additionalParameters = userRequest.getAdditionalParameters();
                    if (additionalParameters.containsKey("email")) {
                        vkUserAttributes.put("email", additionalParameters.get("email"));
                    }
                    if (additionalParameters.containsKey("phone")) {
                        vkUserAttributes.put("phone", additionalParameters.get("phone"));
                    }

                    String userNameAttributeName = userRequest.getClientRegistration()
                            .getProviderDetails().getUserInfoEndpoint().getUserNameAttributeName();

                    return new DefaultOAuth2User(
                            oAuth2User.getAuthorities(),
                            vkUserAttributes,
                            userNameAttributeName
                    );
                }
            }
        }
        return oAuth2User;
    }
}