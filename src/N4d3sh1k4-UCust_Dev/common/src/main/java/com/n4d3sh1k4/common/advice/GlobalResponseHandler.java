package com.n4d3sh1k4.common.advice;

import jakarta.annotation.Nonnull;
import org.springframework.core.MethodParameter;
import org.springframework.http.MediaType;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.http.server.ServerHttpResponse;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.mvc.method.annotation.ResponseBodyAdvice;

@RestControllerAdvice
public class GlobalResponseHandler implements ResponseBodyAdvice<Object> {

    @Override
    public boolean supports(MethodParameter returnType, @Nonnull Class converterType) {
        String packageName = returnType.getContainingClass().getPackageName();
        if (packageName.startsWith("org.springdoc") || packageName.startsWith("org.springframework")) {
            return false;
        }
        return true;
    }

    @Override
    public Object beforeBodyWrite(Object body, @Nonnull MethodParameter returnType, @Nonnull MediaType selectedContentType,
                                  @Nonnull Class selectedConverterType, @Nonnull ServerHttpRequest request, @Nonnull ServerHttpResponse response) {
        if (body == null || body instanceof com.n4d3sh1k4.common.dto.ApiResponse || body instanceof byte[] || body instanceof String) {
            return body;
        }
        if (body instanceof org.springframework.core.io.Resource) {
            return body;
        }
        return com.n4d3sh1k4.common.dto.ApiResponse.success(body);
    }
}