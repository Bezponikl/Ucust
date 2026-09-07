package com.n4d3sh1k4.generative_orchestration_service.domain.model.content;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

@Entity
@Table(name = "post_statistics")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PostStatistics {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id")
    private UUID id;

    @Column(name = "post_id", nullable = false)
    private UUID postId;

    @Column(name = "platform")
    private String platform;

    @Column(name = "likes")
    private int likes;

    @Column(name = "shares")
    private int shares;

    @Column(name = "comments")
    private int comments;

    @Column(name = "impressions")
    private int impressions;
}
