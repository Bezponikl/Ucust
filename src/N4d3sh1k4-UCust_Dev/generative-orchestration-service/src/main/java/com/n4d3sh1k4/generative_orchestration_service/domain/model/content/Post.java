package com.n4d3sh1k4.generative_orchestration_service.domain.model.content;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "posts")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Post {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id")
    private UUID id;

    @Column(name = "project_id", nullable = false)
    private UUID projectId;

    @Column(name = "user_id", nullable = false)
    private UUID userId;

    @Column(name = "text", columnDefinition = "TEXT")
    private String text;

    @Column(name = "image_url")
    private String imageUrl;

    @Column(name = "hashtags")
    private String hashtags;

    @Column(name = "target_platforms")
    private String targetPlatforms;

    @Column(name = "scheduled_at")
    private Instant scheduledAt;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false)
    private PostStatus status;

    @Enumerated(EnumType.STRING)
    @Column(name = "content_type")
    private ContentType contentType;

    @Enumerated(EnumType.STRING)
    @Column(name = "generation_mode", nullable = false)
    private GenerationMode generationMode;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    @Column(name = "published_at")
    private Instant publishedAt;
}
