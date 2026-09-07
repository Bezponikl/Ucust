package com.n4d3sh1k4.api_gateway;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import org.springframework.web.server.WebFilter;
import org.springframework.web.server.WebFilterChain;
import reactor.core.publisher.Mono;

@Component
@Slf4j
public class RequestLoggingFilter implements WebFilter {

    private static final java.util.Set<String> SENSITIVE_HEADERS = java.util.Set.of("cookie", "authorization");

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, WebFilterChain chain) {
        var request = exchange.getRequest();
        log.debug("→ {} {} (query: {})",
                request.getMethod(),
                request.getURI(),
                request.getQueryParams());

        return chain.filter(exchange).then(Mono.fromRunnable(() ->
                log.debug("← {} {} → {}", request.getMethod(), request.getURI(), exchange.getResponse().getStatusCode())
        ));
    }
}
