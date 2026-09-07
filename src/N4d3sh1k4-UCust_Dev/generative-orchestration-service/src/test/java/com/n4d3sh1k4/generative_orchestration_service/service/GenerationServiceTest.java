package com.n4d3sh1k4.generative_orchestration_service.service;

import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.GenerationMode;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.Post;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.PostStatus;
import com.n4d3sh1k4.generative_orchestration_service.domain.repository.PostRepository;
import com.n4d3sh1k4.generative_orchestration_service.dto.PostResponse;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class GenerationServiceTest {

    private static final UUID POST_ID = UUID.fromString("11111111-1111-1111-1111-111111111111");
    private static final UUID PROJECT_ID = UUID.fromString("22222222-2222-2222-2222-222222222222");
    private static final UUID USER_ID = UUID.fromString("33333333-3333-3333-3333-333333333333");
    private static final Instant CREATED_AT = Instant.parse("2026-01-01T09:00:00Z");

    @Mock
    private PostRepository postRepository;

    @InjectMocks
    private GenerationService generationService;

    private Post post(PostStatus status) {
        return Post.builder()
                .id(POST_ID)
                .projectId(PROJECT_ID)
                .userId(USER_ID)
                .text("Текст поста")
                .status(status)
                .generationMode(GenerationMode.AUTO)
                .createdAt(CREATED_AT)
                .build();
    }

    @Test
    void confirmPost_whenExists_setsConfirmedAndSaves() {
        Post post = post(PostStatus.DRAFT);
        when(postRepository.findById(POST_ID)).thenReturn(Optional.of(post));

        PostResponse response = generationService.confirmPost(POST_ID);

        assertThat(response.id()).isEqualTo(POST_ID);
        assertThat(response.status()).isEqualTo(PostStatus.CONFIRMED);
        assertThat(post.getStatus()).isEqualTo(PostStatus.CONFIRMED);
        verify(postRepository).save(post);
    }

    @Test
    void confirmPost_whenNotFound_throwsContentNotFound() {
        when(postRepository.findById(POST_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> generationService.confirmPost(POST_ID))
                .isInstanceOf(ContentNotFoundException.class)
                .satisfies(e -> assertThat(((ContentNotFoundException) e).getCode()).isEqualTo("NOT_FOUND"));

        verify(postRepository, never()).save(any(Post.class));
    }

    @Test
    void publishPost_whenExists_setsPublishedAndTimestamp() {
        Post post = post(PostStatus.CONFIRMED);
        when(postRepository.findById(POST_ID)).thenReturn(Optional.of(post));

        PostResponse response = generationService.publishPost(POST_ID);

        assertThat(response.status()).isEqualTo(PostStatus.PUBLISHED);
        assertThat(post.getStatus()).isEqualTo(PostStatus.PUBLISHED);
        assertThat(post.getPublishedAt()).isNotNull();
        verify(postRepository).save(post);
    }

    @Test
    void publishPost_whenNotFound_throwsContentNotFound() {
        when(postRepository.findById(POST_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> generationService.publishPost(POST_ID))
                .isInstanceOf(ContentNotFoundException.class);

        verify(postRepository, never()).save(any(Post.class));
    }

    @Test
    void getPostById_whenExists_returnsResponse() {
        Post post = post(PostStatus.DRAFT);
        when(postRepository.findById(POST_ID)).thenReturn(Optional.of(post));

        PostResponse response = generationService.getPostById(POST_ID);

        assertThat(response.id()).isEqualTo(POST_ID);
        assertThat(response.projectId()).isEqualTo(PROJECT_ID);
        assertThat(response.text()).isEqualTo("Текст поста");
        assertThat(response.status()).isEqualTo(PostStatus.DRAFT);
        assertThat(response.generationMode()).isEqualTo(GenerationMode.AUTO);
        assertThat(response.createdAt()).isEqualTo(CREATED_AT);
    }

    @Test
    void getPostById_whenNotFound_throwsContentNotFound() {
        when(postRepository.findById(POST_ID)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> generationService.getPostById(POST_ID))
                .isInstanceOf(ContentNotFoundException.class);
    }

    @Test
    void getPostsByProject_mapsToResponses() {
        Post first = post(PostStatus.DRAFT);
        Post second = post(PostStatus.CONFIRMED);
        when(postRepository.findByProjectIdOrderByCreatedAtDesc(PROJECT_ID))
                .thenReturn(List.of(first, second));

        List<PostResponse> responses = generationService.getPostsByProject(PROJECT_ID);

        assertThat(responses).hasSize(2);
        assertThat(responses.get(0).id()).isEqualTo(POST_ID);
        assertThat(responses.get(0).status()).isEqualTo(PostStatus.DRAFT);
        assertThat(responses.get(1).status()).isEqualTo(PostStatus.CONFIRMED);
    }

    @Test
    void getPostsByProject_whenEmpty_returnsEmptyList() {
        when(postRepository.findByProjectIdOrderByCreatedAtDesc(PROJECT_ID)).thenReturn(List.of());

        assertThat(generationService.getPostsByProject(PROJECT_ID)).isEmpty();
    }
}