package com.n4d3sh1k4.api_gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class ApiGatewayApplication {

	public static void main(String[] args) {
		SpringApplication.run(ApiGatewayApplication.class, args);
	}


	@Bean
	public RouteLocator customRouteLocator(RouteLocatorBuilder builder, AuthenticationGatewayFilterFactory authFilter) {

		final String API_PREFIX = "/api/v0";

		return builder.routes()
				.route("security-service-public", r -> r
						.path(
								API_PREFIX + "/auth/login",
								API_PREFIX + "/auth/register",
								API_PREFIX + "/auth/refresh",
								API_PREFIX + "/auth/forgot-password",
								API_PREFIX + "/auth/reset-password",
								API_PREFIX + "/auth/confirm",
								API_PREFIX + "/auth/resend-confirmation",
								API_PREFIX + "/oauth2/**",
								API_PREFIX + "/login/oauth2/**")
						.filters(f -> f.stripPrefix(2))
						.uri("lb://security-service"))

				.route("security-service-private", r -> r
						.path(API_PREFIX + "/auth/logout",
								API_PREFIX + "/status/hello")
						.filters(f -> f
								.filter(authFilter.apply(new AuthenticationGatewayFilterFactory.Config()))
								.stripPrefix(2))
						.uri("lb://security-service"))

				.route("user-service-private", r -> r.path(API_PREFIX + "/user/**")
						.filters(f -> f
								.filter(authFilter.apply(new AuthenticationGatewayFilterFactory.Config()))
								.stripPrefix(2))
						.uri("lb://user-service"))

				.route("projects-service-private", r -> r.path(API_PREFIX + "/projects/**")
						.filters(f -> f
								.filter(authFilter.apply(new AuthenticationGatewayFilterFactory.Config()))
								.stripPrefix(2))
						.uri("lb://business-service"))

				.build();
	}
}