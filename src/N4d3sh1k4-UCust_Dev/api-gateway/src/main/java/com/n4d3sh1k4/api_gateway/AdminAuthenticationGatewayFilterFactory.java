package com.n4d3sh1k4.api_gateway;

import io.jsonwebtoken.Claims;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.factory.AbstractGatewayFilterFactory;
import org.springframework.http.HttpCookie;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseCookie;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class AdminAuthenticationGatewayFilterFactory extends AbstractGatewayFilterFactory<AdminAuthenticationGatewayFilterFactory.Config> {

    private final JwtUtils jwtUtils;
    private static final Logger log = LoggerFactory.getLogger(AdminAuthenticationGatewayFilterFactory.class);

    public AdminAuthenticationGatewayFilterFactory(JwtUtils jwtUtils) {
        super(Config.class);
        this.jwtUtils = jwtUtils;
    }

    public static class Config {
    }

    @Override
    public GatewayFilter apply(Config config) {
        return (exchange, chain) -> {
            ServerHttpRequest request = exchange.getRequest();
            String token = null;

            String authHeader = request.getHeaders().getFirst(HttpHeaders.AUTHORIZATION);
            if (authHeader != null && authHeader.startsWith("Bearer ")) {
                token = authHeader.substring(7);
            }

            if (token == null) {
                token = request.getQueryParams().getFirst("adm_token");
            }

            if (token == null) {
                HttpCookie cookie = request.getCookies().getFirst("Admin-Session-JWT");
                if (cookie != null) {
                    token = cookie.getValue();
                }
            }

            if (token == null) {
                log.warn("Admin resource access denied: Token missing.");
                exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
                return exchange.getResponse().setComplete();
            }

            if (jwtUtils.validateAccessToken(token)) {
                Claims claims = jwtUtils.getAccessClaims(token);
                List roles = claims.get("roles", List.class);

                if (roles == null || !roles.contains("ROLE_ADMIN")) {
                    log.warn("Access denied for user {}: Not an ADMIN", claims.getSubject());
                    exchange.getResponse().setStatusCode(HttpStatus.FORBIDDEN);
                    return exchange.getResponse().setComplete();
                }

                ServerHttpRequest.Builder mutatedRequestBuilder = request.mutate()
                        .header("X-User-Id", claims.getSubject())
                        .header("X-User-Roles", String.join(",", roles));

                if (request.getQueryParams().containsKey("adm_token")) {
                    ResponseCookie adminCookie = ResponseCookie.from("Admin-Session-JWT", token)
                            .httpOnly(true)
                            .secure(false)
                            .path("/")
                            .sameSite("Lax")
                            .build();
                    exchange.getResponse().addCookie(adminCookie);
                }

                log.info("Admin Filter forwarding request to: {}", request.getURI());
                return chain.filter(exchange.mutate().request(mutatedRequestBuilder.build()).build());
            }

            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        };
    }
}
