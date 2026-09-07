package com.n4d3sh1k4.generative_orchestration_service.controller;

import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.ContentType;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.GenerationMode;
import com.n4d3sh1k4.generative_orchestration_service.domain.model.content.PostStatus;
import com.n4d3sh1k4.generative_orchestration_service.dto.PostResponse;
import com.n4d3sh1k4.generative_orchestration_service.service.GenerationService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.autoconfigure.web.DataWebAutoConfiguration;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(excludeAutoConfiguration = DataWebAutoConfiguration.class)
@Import(GenerationController.class)
@AutoConfigureMockMvc(addFilters = true)
class GenerationControllerTest {

    private static final UUID POST_ID = UUID.fromString("11111111-1111-1111-1111-111111111111");
    private static final UUID PROJECT_ID = UUID.fromString("22222222-2222-2222-2222-222222222222");

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private GenerationService generationService;

    private PostResponse response(PostStatus status) {
        return new PostResponse(
                POST_ID, PROJECT_ID, "Текст поста", "http://img.example/post.jpg", "#маркетинг",
                "telegram", Instant.parse("2026-01-05T10:00:00Z"),
                status, ContentType.PROMOTIONAL, GenerationMode.AUTO,
                Instant.parse("2026-01-01T09:00:00Z"));
    }

    @Test
    void confirm_post_returns200() throws Exception {
        when(generationService.confirmPost(POST_ID)).thenReturn(response(PostStatus.CONFIRMED));

        mockMvc.perform(post("/orchestration/posts/{id}/confirm", POST_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.id").value(POST_ID.toString()))
                .andExpect(jsonPath("$.data.status").value("CONFIRMED"))
                .andExpect(jsonPath("$.data.contentType").value("PROMOTIONAL"))
                .andExpect(jsonPath("$.data.generationMode").value("AUTO"));

        verify(generationService).confirmPost(POST_ID);
    }

    @Test
    void confirm_post_whenNotFound_returns404() throws Exception {
        when(generationService.confirmPost(POST_ID))
                .thenThrow(new ContentNotFoundException("Post not found"));

        mockMvc.perform(post("/orchestration/posts/{id}/confirm", POST_ID))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.error.code").value("NOT_FOUND"));

        verify(generationService).confirmPost(POST_ID);
    }

    @Test
    void publish_post_returns200() throws Exception {
        when(generationService.publishPost(POST_ID)).thenReturn(response(PostStatus.PUBLISHED));

        mockMvc.perform(post("/orchestration/posts/{id}/publish", POST_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.id").value(POST_ID.toString()))
                .andExpect(jsonPath("$.data.status").value("PUBLISHED"));

        verify(generationService).publishPost(POST_ID);
    }

    @Test
    void publish_post_whenNotFound_returns404() throws Exception {
        when(generationService.publishPost(POST_ID))
                .thenThrow(new ContentNotFoundException("Post not found"));

        mockMvc.perform(post("/orchestration/posts/{id}/publish", POST_ID))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.error.code").value("NOT_FOUND"));

        verify(generationService).publishPost(POST_ID);
    }

    @Test
    void getPost_byId_returns200() throws Exception {
        when(generationService.getPostById(POST_ID)).thenReturn(response(PostStatus.DRAFT));

        mockMvc.perform(get("/orchestration/posts/{id}", POST_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.id").value(POST_ID.toString()))
                .andExpect(jsonPath("$.data.status").value("DRAFT"));

        verify(generationService).getPostById(POST_ID);
    }

    @Test
    void getPost_whenNotFound_returns404() throws Exception {
        when(generationService.getPostById(POST_ID))
                .thenThrow(new ContentNotFoundException("Post not found"));

        mockMvc.perform(get("/orchestration/posts/{id}", POST_ID))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.error.code").value("NOT_FOUND"));

        verify(generationService).getPostById(POST_ID);
    }

    @Test
    void getPosts_byProject_returns200List() throws Exception {
        when(generationService.getPostsByProject(PROJECT_ID))
                .thenReturn(List.of(response(PostStatus.DRAFT), response(PostStatus.CONFIRMED)));

        mockMvc.perform(get("/orchestration/projects/{projectId}/posts", PROJECT_ID))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data").isArray())
                .andExpect(jsonPath("$.data.length()").value(2))
                .andExpect(jsonPath("$.data[0].id").value(POST_ID.toString()))
                .andExpect(jsonPath("$.data[1].status").value("CONFIRMED"));

        verify(generationService).getPostsByProject(PROJECT_ID);
    }
}