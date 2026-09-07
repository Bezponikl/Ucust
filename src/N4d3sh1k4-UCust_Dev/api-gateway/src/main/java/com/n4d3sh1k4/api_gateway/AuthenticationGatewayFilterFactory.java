package com.n4d3sh1k4.api_gateway;

import io.jsonwebtoken.Claims;
import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.factory.AbstractGatewayFilterFactory;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;

@Component
public class AuthenticationGatewayFilterFactory extends AbstractGatewayFilterFactory<AuthenticationGatewayFilterFactory.Config> {

    private final JwtUtils jwtUtils;
    private static final Logger log = LoggerFactory.getLogger(AuthenticationGatewayFilterFactory.class);

    public AuthenticationGatewayFilterFactory(JwtUtils jwtUtils) {
        super(Config.class);
        this.jwtUtils = jwtUtils;
    }

    public static class Config {}

    @Override
    public GatewayFilter apply(Config config) {
        return (exchange, chain) -> {
            ServerHttpRequest request = exchange.getRequest();
            String authHeader = request.getHeaders().getFirst(HttpHeaders.AUTHORIZATION);
            if (authHeader == null || !authHeader.startsWith("Bearer ")) {
                exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
                return exchange.getResponse().setComplete();
            }

            String token = authHeader.substring(7);

            if (jwtUtils.validateAccessToken(token)) {
                Claims claims = jwtUtils.getAccessClaims(token);

                ServerHttpRequest mutatedRequest = exchange.getRequest().mutate()
                        .header("X-User-Id", claims.getSubject())
                        .header("X-User-Roles", String.join(",", claims.get("roles", List.class)))
                        .build();

                log.info("Gateway forwarding request with cookies: {}",
                    mutatedRequest.getHeaders().get(HttpHeaders.COOKIE));
                return chain.filter(exchange.mutate().request(mutatedRequest).build());
            }

            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        };
    }
}