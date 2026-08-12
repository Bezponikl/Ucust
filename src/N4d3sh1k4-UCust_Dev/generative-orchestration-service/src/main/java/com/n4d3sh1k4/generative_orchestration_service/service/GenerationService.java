package com.n4d3sh1k4.generative_orchestration_service.service;

import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.Post;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.PostStatus;
import com.n4d3sh1k4.generative_orchestration_service.domain.repository.PostRepository;
import com.n4d3sh1k4.generative_orchestration_service.dto.PostResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class GenerationService {

    private final PostRepository postRepository;

    @Transactional
    public PostResponse confirmPost(UUID postId) {
        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new ContentNotFoundException("Post not found"));
        post.setStatus(PostStatus.CONFIRMED);
        postRepository.save(post);
        return toResponse(post);
    }

    @Transactional
    public PostResponse publishPost(UUID postId) {
        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new ContentNotFoundException("Post not found"));
        post.setStatus(PostStatus.PUBLISHED);
        post.setPublishedAt(Instant.now());
        postRepository.save(post);
        return toResponse(post);
    }

    @Transactional(readOnly = true)
    public PostResponse getPostById(UUID postId) {
        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new ContentNotFoundException("Post not found"));
        return toResponse(post);
    }

    @Transactional(readOnly = true)
    public List<PostResponse> getPostsByProject(UUID projectId) {
        return postRepository.findByProjectIdOrderByCreatedAtDesc(projectId)
                .stream()
                .map(this::toResponse)
                .toList();
    }

    private PostResponse toResponse(Post post) {
        return new PostResponse(
                post.getId(),
                post.getProjectId(),
                post.getText(),
                post.getImageUrl(),
                post.getHashtags(),
                post.getTargetPlatforms(),
                post.getScheduledAt(),
                post.getStatus(),
                post.getContentType(),
                post.getGenerationMode(),
                post.getCreatedAt()
        );
    }
}
