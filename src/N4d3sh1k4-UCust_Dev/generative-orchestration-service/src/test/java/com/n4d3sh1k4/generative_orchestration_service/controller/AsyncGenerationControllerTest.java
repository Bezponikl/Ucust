package com.n4d3sh1k4.generative_orchestration_service.controller;

import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.TaskStatus;
import com.n4d3sh1k4.generative_orchestration_service.dto.AsyncGenerateResponse;
import com.n4d3sh1k4.generative_orchestration_service.dto.TaskStatusResponse;
import com.n4d3sh1k4.generative_orchestration_service.dto.request_dto.GenerateRequest;
import com.n4d3sh1k4.generative_orchestration_service.service.AsyncGenerationService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.autoconfigure.web.DataWebAutoConfiguration;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.RequestPostProcessor;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.authentication;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(excludeAutoConfiguration = DataWebAutoConfiguration.class)
@Import(AsyncGenerationController.class)
@AutoConfigureMockMvc(addFilters = true)
class AsyncGenerationControllerTest {

    private static final UUID USER_ID = UUID.fromString("33333333-3333-3333-3333-333333333333");
    private static final UUID TASK_ID = UUID.fromString("44444444-4444-4444-4444-444444444444");
    private static final UUID PROJECT_ID = UUID.fromString("22222222-2222-2222-2222-222222222222");
    private static final UUID POST_ID = UUID.fromString("11111111-1111-1111-1111-111111111111");

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private AsyncGenerationService asyncGenerationService;

    private RequestPostProcessor authenticated() {
        return authentication(new UsernamePasswordAuthenticationToken(
                USER_ID.toString(), null, List.of()));
    }

    @Test
    void submitAsync_validRequest_returns202() throws Exception {
        when(asyncGenerationService.submitAsync(any(GenerateRequest.class), eq(USER_ID)))
                .thenReturn(new AsyncGenerateResponse(TASK_ID, TaskStatus.PROCESSING));

        mockMvc.perform(post("/orchestration/generate/async")
                        .with(authenticated())
                        .contentType("application/json")
                        .content("{"
                                + "\"projectId\": \"" + PROJECT_ID + "\","
                                + "\"mode\": \"AUTO\","
                                + "\"count\": 2,"
                                + "\"prompt\": \"Тема для поста\"}"))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.taskId").value(TASK_ID.toString()))
                .andExpect(jsonPath("$.data.status").value("PROCESSING"));

        verify(asyncGenerationService).submitAsync(any(GenerateRequest.class), eq(USER_ID));
    }

    @Test
    void submitAsync_whenProjectIdMissing_returns400() throws Exception {
        mockMvc.perform(post("/orchestration/generate/async")
                        .with(authenticated())
                        .contentType("application/json")
                        .content("{\"mode\": \"AUTO\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.error.code").value("VALIDATION_ERROR"));

        verify(asyncGenerationService, never()).submitAsync(any(), any());
    }

    @Test
    void submitAsync_whenModeMissing_returns400() throws Exception {
        mockMvc.perform(post("/orchestration/generate/async")
                        .with(authenticated())
                        .contentType("application/json")
                        .content("{\"projectId\": \"" + PROJECT_ID + "\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("VALIDATION_ERROR"));

        verify(asyncGenerationService, never()).submitAsync(any(), any());
    }

    @Test
    void submitAsync_whenCountZero_returns400() throws Exception {
        mockMvc.perform(post("/orchestration/generate/async")
                        .with(authenticated())
                        .contentType("application/json")
                        .content("{"
                                + "\"projectId\": \"" + PROJECT_ID + "\","
                                + "\"mode\": \"AUTO\","
                                + "\"count\": 0}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("VALIDATION_ERROR"));

        verify(asyncGenerationService, never()).submitAsync(any(), any());
    }

    @Test
    void checkTask_returns200() throws Exception {
        when(asyncGenerationService.checkTask(TASK_ID)).thenReturn(new TaskStatusResponse(
                TASK_ID, "ext-1", TaskStatus.COMPLETED, POST_ID, null,
                Instant.parse("2026-01-01T09:00:00Z"), Instant.parse("2026-01-01T09:05:00Z")));

        mockMvc.perform(get("/orchestration/tasks/{taskId}", TASK_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.taskId").value(TASK_ID.toString()))
                .andExpect(jsonPath("$.data.externalTaskId").value("ext-1"))
                .andExpect(jsonPath("$.data.status").value("COMPLETED"))
                .andExpect(jsonPath("$.data.resultPostId").value(POST_ID.toString()));

        verify(asyncGenerationService).checkTask(TASK_ID);
    }

    @Test
    void checkTask_whenNotFound_returns404() throws Exception {
        when(asyncGenerationService.checkTask(TASK_ID))
                .thenThrow(new ContentNotFoundException("Task not found"));

        mockMvc.perform(get("/orchestration/tasks/{taskId}", TASK_ID))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.error.code").value("NOT_FOUND"));

        verify(asyncGenerationService).checkTask(TASK_ID);
    }
}