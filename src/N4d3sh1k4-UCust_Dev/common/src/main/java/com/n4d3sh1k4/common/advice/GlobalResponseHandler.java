package com.n4d3sh1k4.common.advice;

import com.n4d3sh1k4.common.dto.ApiResponse;
import org.springframework.core.MethodParameter;
import org.springframework.http.MediaType;
import org.springframework.http.converter.json.MappingJackson2HttpMessageConverter;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.http.server.ServerHttpResponse;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.mvc.method.annotation.ResponseBodyAdvice;

@RestControllerAdvice
public class GlobalResponseHandler implements ResponseBodyAdvice<Object> {

    @Override
    public boolean supports(MethodParameter returnType, Class converterType) {
        if (!MappingJackson2HttpMessageConverter.class.isAssignableFrom(converterType)) {
            return false;
        }

        String packageName = returnType.getContainingClass().getPackageName();
        if (packageName.startsWith("org.springdoc") ||
                packageName.startsWith("org.springframework")) {
            return false;
        }

        return true;
    }

    @Override
    public Object beforeBodyWrite(Object body, MethodParameter returnType, MediaType selectedContentType,
                                  Class selectedConverterType, ServerHttpRequest request, ServerHttpResponse response) {

        if (body == null) {
            return com.n4d3sh1k4.common.dto.ApiResponse.success(null);
        }

        if (body instanceof com.n4d3sh1k4.common.dto.ApiResponse || body instanceof String) {
            return body;
        }

        return com.n4d3sh1k4.common.dto.ApiResponse.success(body);
    }
}
