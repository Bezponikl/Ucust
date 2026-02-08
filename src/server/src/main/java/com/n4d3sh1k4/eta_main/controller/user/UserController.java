package com.n4d3sh1k4.eta_main.controller.user;

import io.swagger.v3.oas.annotations.Hidden;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Hidden
@RestController
@RequestMapping("/users/{id}")
public class UserController {

    @GetMapping()
    public ResponseEntity<?> UserInfo() {
        return ResponseEntity.ok().build();
    }

    @PatchMapping()
    public ResponseEntity<?> UserUpdate() {
        return ResponseEntity.ok().build();
    }

    @PostMapping()
    public ResponseEntity<?> UserDeactivate() {
        return ResponseEntity.ok().build();
    }

    @PostMapping("/password")
    public ResponseEntity<?> ResetPassword() {
        return ResponseEntity.ok().build();
    }

    @PostMapping("/sessions")
    public ResponseEntity<?> Sessions() {
        return ResponseEntity.ok().build();
    }

    @PostMapping("/verify-email")
    public ResponseEntity<?> VerifyEmail() {
        return ResponseEntity.ok().build();
    }
}
