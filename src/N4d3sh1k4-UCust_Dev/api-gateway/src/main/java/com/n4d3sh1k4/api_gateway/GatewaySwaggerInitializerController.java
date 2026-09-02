package com.n4d3sh1k4.api_gateway;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

@RestController
public class GatewaySwaggerInitializerController {

    @GetMapping(value = "/admin/swagger/swagger-initializer.js", produces = "application/javascript")
    public Mono<String> getCustomInitializer() {
        String script = "window.onload = function() {\n" +
                "  window.ui = SwaggerUIBundle({\n" +
                "    configUrl: '/v3/api-docs/swagger-config',\n" +
                "    urls: [\n" +
                "      {name: 'Security Service', url: '/admin/api-docs/security-service'},\n" +
                "      {name: 'User Service', url: '/admin/api-docs/user-service'},\n" +
                "      {name: 'Business Service', url: '/admin/api-docs/business-service'},\n" +
                "      {name: 'Billing Service', url: '/admin/api-docs/billing-service'},\n" +
                "      {name: 'Generate Orchestration Service', url: '/admin/api-docs/generative-orchestration-service'},\n"+
                "    ],\n" +
                "    dom_id: '#swagger-ui',\n" +
                "    deepLinking: true,\n" +
                "    presets: [\n" +
                "      SwaggerUIBundle.presets.apis,\n" +
                "      SwaggerUIStandalonePreset\n" +
                "    ],\n" +
                "    plugins: [\n" +
                "      SwaggerUIBundle.plugins.DownloadUrl\n" +
                "    ],\n" +
                "    layout: 'StandaloneLayout'\n" +
                "  });\n" +
                "};";
        return Mono.just(script);
    }
}