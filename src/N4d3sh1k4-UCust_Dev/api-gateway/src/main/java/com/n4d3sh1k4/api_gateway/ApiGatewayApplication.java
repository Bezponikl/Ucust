package com.n4d3sh1k4.api_gateway;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class ApiGatewayApplication {

	@Value("${services.security-service.uri}")
    private String securityServiceUri;

	@Value("${services.user-service.uri}")
    private String userServiceUri;

    @Value("${services.business-service.uri}")
    private String businessServiceUri;

    @Value("${services.billing-service.uri}")
    private String billingServiceUri;

    @Value("${services.generative-orchestration-service.uri}")
    private String generativeOrchestrationServiceUri;

    @Value("${services.dozzle.uri}")
    private String dozzleUri;

    @Value("${services.pgadmin.uri}")
    private String pgadminUri;

    @Value("${rabbitmq.admin.uri}")
    private String rabbitmqUri;

	@Value("${minio.admin.uri}")
    private String minioUri;

    @Value("${minio.s3.uri}")
    private String minioS3Uri;

	static void main(String[] args) {
		SpringApplication.run(ApiGatewayApplication.class, args);
	}


	@Bean
	public RouteLocator customRouteLocator(RouteLocatorBuilder builder, AuthenticationGatewayFilterFactory authFilter, AdminAuthenticationGatewayFilterFactory adminAuthFilter) {

		final String API_PREFIX = "/api/v0";

		return builder.routes()

		//Security Service
				//security-service (opened)
				.route("security-service-public", r -> r
						.path(
								API_PREFIX + "/auth/login",
								API_PREFIX + "/auth/register",
								API_PREFIX + "/auth/refresh",
								API_PREFIX + "/auth/forgot-password",
								API_PREFIX + "/auth/reset-password",
								API_PREFIX + "/auth/confirm-email",
								API_PREFIX + "/auth/resend-confirmation",
								API_PREFIX + "/auth/yandex-mobile",
								API_PREFIX + "/auth/link-social",
								API_PREFIX + "/auth/change-email/set-new-email",
								API_PREFIX + "/auth/change-email/confirm",
								API_PREFIX + "/oauth2/**",
								API_PREFIX + "/login/oauth2/**")
						.filters(f -> f.stripPrefix(2))
						.uri(securityServiceUri))

				//security-service (authenticated)
				.route("security-service-private", r -> r
						.path(API_PREFIX + "/auth/logout",
								API_PREFIX + "/auth/change-email/verify-password",
								API_PREFIX + "/status/hello",
								API_PREFIX + "/status/me"
								)
						.filters(f -> f
								.filter(authFilter.apply(new AuthenticationGatewayFilterFactory.Config()))
								.stripPrefix(2))
						.uri(securityServiceUri))

		//User Service
				.route("user-service-private", r -> r.path(API_PREFIX + "/user/**")
						.filters(f -> f
								.filter(authFilter.apply(new AuthenticationGatewayFilterFactory.Config()))
								.stripPrefix(2))
						.uri(userServiceUri))

		//Business Service
				.route("business-service-private", r -> r.path(API_PREFIX + "/projects/**")
						.filters(f -> f
								.filter(authFilter.apply(new AuthenticationGatewayFilterFactory.Config()))
								.stripPrefix(2))
						.uri(businessServiceUri))
		//Billing Service
				 //billing-service (tariffs - public GET)
                .route("billing-tariffs-public", r -> r
                        .path(API_PREFIX + "/tariffs",
								API_PREFIX + "/tariffs/**")
                        .filters(f -> f.stripPrefix(2))
                        .uri(billingServiceUri))

                //billing-service quota (authenticated)
                .route("billing-quota", r -> r
                        .path(API_PREFIX + "/quota/me",
								API_PREFIX + "/quota/me/**")
                        .filters(f -> f
                                .filter(authFilter.apply(new AuthenticationGatewayFilterFactory.Config()))
                                .stripPrefix(2))
                        .uri(billingServiceUri))

                //billing-service Admin
                .route("billing-admin", r -> r
                        .path(API_PREFIX + "/admin/billing/**")
                        .filters(f -> f
                                .filter(authFilter.apply(new AuthenticationGatewayFilterFactory.Config()))
                                .stripPrefix(2))
                        .uri(billingServiceUri))

		//Generative orchestration service
                .route("orchestration-private", r -> r
                        .path(API_PREFIX + "/orchestration/**")
                        .filters(f -> f
                                .filter(authFilter.apply(new AuthenticationGatewayFilterFactory.Config()))
                                .stripPrefix(2))
                        .uri(generativeOrchestrationServiceUri))

		//Admin Part
				//RabbitMQ
                .route("rabbitmq-ui-route", r -> r
                        .path("/admin/rabbit/**")
                        .filters(f -> f
                                .filter(adminAuthFilter.apply(new AdminAuthenticationGatewayFilterFactory.Config()))
                                .preserveHostHeader()
                                .removeResponseHeader("X-Frame-Options")
                                .removeResponseHeader("Content-Security-Policy"))
                        .uri(rabbitmqUri))

				//Minio
                .route("minio-ui-route", r -> r
                        .path("/admin/minio/**")
                        .filters(f -> f
                                .filter(adminAuthFilter.apply(new AdminAuthenticationGatewayFilterFactory.Config()))
                                .preserveHostHeader()
                                .stripPrefix(2)
                                .removeResponseHeader("X-Frame-Options")
                                .removeResponseHeader("Content-Security-Policy"))
                        .uri(minioUri))

                //Minio S3 (public read for images)
                .route("minio-s3-public", r -> r
                        .path("/s3/**")
                        .filters(f -> f.stripPrefix(1))
                        .uri(minioS3Uri))

				//PgAdmin
                .route("pgadmin-ui-route", r -> r
                        .path("/admin/pgadmin/**")
                        .filters(f -> f
                                .addRequestHeader("X-Script-Name", "/admin/pgadmin")
                                .removeResponseHeader("X-Frame-Options")
                                .removeResponseHeader("Content-Security-Policy"))
                        .uri(pgadminUri))

				//Dozzle
				.route("dozzle-monitoring", r -> r
                        .path("/admin/monitoring/**")
                        .filters(f -> f
                                .filter(adminAuthFilter.apply(new AdminAuthenticationGatewayFilterFactory.Config()))
                                .removeResponseHeader("X-Frame-Options")
                                .removeResponseHeader("Content-Security-Policy"))
                        .uri(dozzleUri))

				//Swagger
                .route("swagger-config-default-pass", r -> r
                        .path("/v3/api-docs/swagger-config")
                        .filters(f -> f
                                .filter(adminAuthFilter.apply(new AdminAuthenticationGatewayFilterFactory.Config())))
                        .uri(securityServiceUri))

				.route("swagger-ui-integrated", r -> r
                        .path("/admin/swagger/**")
                        .filters(f -> f
                                .filter(adminAuthFilter.apply(new AdminAuthenticationGatewayFilterFactory.Config()))
                                .rewritePath("/admin/swagger/(?<segment>.*)", "/swagger-ui/${segment}")
                                .removeResponseHeader("X-Frame-Options")
                                .removeResponseHeader("Content-Security-Policy"))
                        .uri(securityServiceUri))

				          //Security service Swagger
				.route("swagger-docs-security", r -> r
                        .path("/admin/api-docs/security-service")
                        .filters(f -> f
                                .filter(adminAuthFilter.apply(new AdminAuthenticationGatewayFilterFactory.Config()))
                                .rewritePath("/admin/api-docs/security-service", "/v3/api-docs"))
                        .uri(securityServiceUri))

				         //User service Swagger
                .route("swagger-docs-user", r -> r
                        .path("/admin/api-docs/user-service")
                        .filters(f -> f
                                .filter(adminAuthFilter.apply(new AdminAuthenticationGatewayFilterFactory.Config()))
                                .rewritePath("/admin/api-docs/user-service", "/v3/api-docs"))
                        .uri(userServiceUri))

                        //Business service Swagger
				.route("swagger-docs-business", r -> r
                        .path("/admin/api-docs/business-service")
                        .filters(f -> f
                                .filter(adminAuthFilter.apply(new AdminAuthenticationGatewayFilterFactory.Config()))
                                .rewritePath("/admin/api-docs/business-service", "/v3/api-docs"))
                        .uri(businessServiceUri))

				        //Billing service Swagger
				.route("swagger-docs-billing", r -> r
                        .path("/admin/api-docs/billing-service")
                        .filters(f -> f
                                .filter(adminAuthFilter.apply(new AdminAuthenticationGatewayFilterFactory.Config()))
                                .rewritePath("/admin/api-docs/billing-service", "/v3/api-docs"))
                        .uri(billingServiceUri))

				        //Generative Orchestration service Swagger
				.route("swagger-docs-generative-orchestration", r -> r
                        .path("/admin/api-docs/generative-orchestration-service")
                        .filters(f -> f
                                .filter(adminAuthFilter.apply(new AdminAuthenticationGatewayFilterFactory.Config()))
                                .rewritePath("/admin/api-docs/generative-orchestration-service", "/v3/api-docs"))
                        .uri(generativeOrchestrationServiceUri))


                .build();
	}
}