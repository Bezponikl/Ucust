package com.n4d3sh1k4.eta_main.domain.model;

import com.n4d3sh1k4.eta_main.domain.model.users.Privilege;
import com.n4d3sh1k4.eta_main.domain.model.users.Role;
import com.n4d3sh1k4.eta_main.domain.repository.PrivilegeRepository;
import com.n4d3sh1k4.eta_main.domain.repository.RoleRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {

    private final RoleRepository roleRepository;
    private final PrivilegeRepository privilegeRepository;

    @Override
    public void run(String... args) {

        if (roleRepository.count() == 0) {

            Privilege read = privilegeRepository.save(
                    new Privilege("USER_READ"));
            Privilege write = privilegeRepository.save(
                    new Privilege("USER_WRITE"));

            Role userRole = new Role("ROLE_USER");
            userRole.setPrivileges(List.of(read, write));
            roleRepository.save(userRole);

            Role adminRole = new Role("ROLE_ADMIN");
            adminRole.setPrivileges(List.of(read, write));
            roleRepository.save(adminRole);
        }
    }
}

