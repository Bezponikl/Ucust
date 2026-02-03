package com.n4d3sh1k4.eta_main.domain.repository;

import com.n4d3sh1k4.eta_main.domain.model.users.Privilege;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.UUID;

@Repository
public interface PrivilegeRepository extends JpaRepository<Privilege, UUID> {
}
