package com.n4d3sh1k4.eta_main.controller.user;

import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/status")
public class StatusController {

    @SecurityRequirement(name = "bearerAuth")
    @GetMapping("/hello")
    public String hello() {
        return "hello";
    }

}
