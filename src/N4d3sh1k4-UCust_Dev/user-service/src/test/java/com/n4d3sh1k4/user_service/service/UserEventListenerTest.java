package com.n4d3sh1k4.user_service.service;

import com.n4d3sh1k4.user_service.domain.model.UserProfile;
import com.n4d3sh1k4.user_service.domain.repository.UserProfileRepository;
import com.n4d3sh1k4.user_service.dto.UserCreatedEvent;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class UserEventListenerTest {

    private static final UUID USER_ID = UUID.fromString("550e8400-e29b-41d4-a716-446655440000");

    @Mock
    private UserProfileRepository profileRepository;

    @InjectMocks
    private UserEventListener eventListener;

    private UserCreatedEvent event() {
        return new UserCreatedEvent(USER_ID, "Олег", "Иванов", "user@example.com", "79991234567");
    }

    @Test
    void handleUserCreated_whenProfileExists_skipsSave() {
        when(profileRepository.existsById(USER_ID)).thenReturn(true);

        eventListener.handleUserCreated(event());

        verify(profileRepository, never()).save(any(UserProfile.class));
    }

    @Test
    void handleUserCreated_whenNewProfile_savesWithAllFields() {
        when(profileRepository.existsById(USER_ID)).thenReturn(false);

        eventListener.handleUserCreated(event());

        ArgumentCaptor<UserProfile> captor = ArgumentCaptor.forClass(UserProfile.class);
        verify(profileRepository).save(captor.capture());
        UserProfile saved = captor.getValue();
        assertThat(saved.getId()).isEqualTo(USER_ID);
        assertThat(saved.getFirstName()).isEqualTo("Олег");
        assertThat(saved.getLastName()).isEqualTo("Иванов");
        assertThat(saved.getEmail()).isEqualTo("user@example.com");
        assertThat(saved.getPhone()).isEqualTo("79991234567");
    }
}