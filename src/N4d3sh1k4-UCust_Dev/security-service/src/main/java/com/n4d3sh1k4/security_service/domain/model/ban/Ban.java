package com.n4d3sh1k4.security_service.domain.model.ban;

import com.n4d3sh1k4.security_service.domain.model.users.User;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "bans")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Ban {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id")
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Enumerated(EnumType.STRING)
    @Column(name = "type", nullable = false)
    private BanType type;

    @Column(name = "reason", columnDefinition = "TEXT")
    private String reason;

    @Column(name = "banned_by")
    private UUID bannedBy;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    @Column(name = "expires_at")
    private Instant expiresAt;

    @Column(name = "active", nullable = false)
    private boolean active;
}
