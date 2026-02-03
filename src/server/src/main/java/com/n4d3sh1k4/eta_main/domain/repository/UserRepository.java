package com.n4d3sh1k4.eta_main.domain.repository;

import com.n4d3sh1k4.eta_main.domain.model.users.User;

import java.util.Optional;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserRepository extends JpaRepository<User, UUID> {
    Optional<User> findByEmail(String email);
}
