package com.n4d3sh1k4.business_service.controller;

import com.n4d3sh1k4.business_service.domain.model.project.support.Industry;
import com.n4d3sh1k4.business_service.domain.model.project.support.ToneOfVoice;
import com.n4d3sh1k4.business_service.dto.ProjectResponse;
import com.n4d3sh1k4.business_service.dto.UserPrincipal;
import com.n4d3sh1k4.business_service.service.ProjectService;
import com.n4d3sh1k4.common.exception.ContentNotFoundException;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.autoconfigure.web.DataWebAutoConfiguration;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.RequestPostProcessor;

import java.util.List;
import java.util.Set;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.authentication;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(excludeAutoConfiguration = DataWebAutoConfiguration.class)
@Import(ProjectController.class)
@AutoConfigureMockMvc(addFilters = true)
class ProjectControllerTest {

    private static final UUID PROJECT_ID = UUID.fromString("11111111-1111-1111-1111-111111111111");
    private static final UUID USER_ID = UUID.fromString("22222222-2222-2222-2222-222222222222");
    private static final String LOGO_PATH = "projects/11111111-1111-1111-1111-111111111111/logo_1a2b3c4d.png";

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private ProjectService projectService;

    private UserPrincipal principal() {
        return new UserPrincipal(USER_ID, "user@example.com", Set.of("ROLE_USER"));
    }

    private RequestPostProcessor authenticated() {
        UserPrincipal principal = principal();
        return authentication(new UsernamePasswordAuthenticationToken(
                principal, null, principal.getAuthorities()));
    }

    private ProjectResponse response() {
        return new ProjectResponse(
                PROJECT_ID, "Мой бизнес", Industry.CAFE_RESTAURANT, "Москва",
                "Описание деятельности", "Молодые специалисты", ToneOfVoice.FRIENDLY,
                null, null, USER_ID, "http://localhost:9020/business-service/" + LOGO_PATH);
    }

    private String validProjectJson() {
        return "{"
                + "\"name\": \"Мой бизнес\","
                + "\"industry\": \"CAFE_RESTAURANT\","
                + "\"city\": \"Москва\","
                + "\"description\": \"Описание деятельности\","
                + "\"targetAudience\": \"Молодые специалисты\","
                + "\"toneOfVoice\": \"FRIENDLY\","
                + "\"socialLinks\": {"
                + "  \"instagram\": \"https://instagram.com/mybusiness\","
                + "  \"telegram\": \"https://t.me/mybusiness\","
                + "  \"website\": \"https://mybusiness.ru\""
                + "},"
                + "\"businessHours\": {"
                + "  \"openTime\": \"09:00\","
                + "  \"closeTime\": \"18:00\","
                + "  \"offDays\": [\"SUNDAY\"]"
                + "}"
                + "}";
    }

    @Test
    void create_validRequest_returns200() throws Exception {
        when(projectService.create(any(), eq(USER_ID))).thenReturn(response());

        mockMvc.perform(post("/projects")
                        .with(authenticated())
                        .contentType("application/json")
                        .content(validProjectJson()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.id").value(PROJECT_ID.toString()))
                .andExpect(jsonPath("$.data.name").value("Мой бизнес"))
                .andExpect(jsonPath("$.data.industry").value("CAFE_RESTAURANT"))
                .andExpect(jsonPath("$.data.toneOfVoice").value("FRIENDLY"));

        verify(projectService).create(any(), eq(USER_ID));
    }

    @Test
    void create_whenNameBlank_returns400() throws Exception {
        mockMvc.perform(post("/projects")
                        .with(authenticated())
                        .contentType("application/json")
                        .content("{"
                                + "\"industry\": \"CAFE_RESTAURANT\","
                                + "\"city\": \"Москва\","
                                + "\"toneOfVoice\": \"FRIENDLY\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.error.code").value("VALIDATION_ERROR"));

        verify(projectService, org.mockito.Mockito.never()).create(any(), any());
    }

    @Test
    void create_whenCloseBeforeOpen_returns400() throws Exception {
        mockMvc.perform(post("/projects")
                        .with(authenticated())
                        .contentType("application/json")
                        .content("{"
                                + "\"name\": \"Мой бизнес\","
                                + "\"industry\": \"CAFE_RESTAURANT\","
                                + "\"city\": \"Москва\","
                                + "\"toneOfVoice\": \"FRIENDLY\","
                                + "\"businessHours\": {"
                                + "  \"openTime\": \"19:00\","
                                + "  \"closeTime\": \"09:00\""
                                + "}}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("VALIDATION_ERROR"));

        verify(projectService, org.mockito.Mockito.never()).create(any(), any());
    }

    @Test
    void create_whenSocialLinkNotHttps_returns400() throws Exception {
        mockMvc.perform(post("/projects")
                        .with(authenticated())
                        .contentType("application/json")
                        .content("{"
                                + "\"name\": \"Мой бизнес\","
                                + "\"industry\": \"CAFE_RESTAURANT\","
                                + "\"city\": \"Москва\","
                                + "\"toneOfVoice\": \"FRIENDLY\","
                                + "\"socialLinks\": {"
                                + "  \"instagram\": \"instagram.com/mybusiness\""
                                + "}}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("VALIDATION_ERROR"));

        verify(projectService, org.mockito.Mockito.never()).create(any(), any());
    }

    @Test
    void getById_returns200() throws Exception {
        when(projectService.getById(PROJECT_ID, USER_ID)).thenReturn(response());

        mockMvc.perform(get("/projects/{id}", PROJECT_ID).with(authenticated()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.id").value(PROJECT_ID.toString()))
                .andExpect(jsonPath("$.data.ownerId").value(USER_ID.toString()))
                .andExpect(jsonPath("$.data.logoUrl").value("http://localhost:9020/business-service/" + LOGO_PATH));

        verify(projectService).getById(PROJECT_ID, USER_ID);
    }

    @Test
    void getById_whenNotFound_returns404() throws Exception {
        when(projectService.getById(PROJECT_ID, USER_ID))
                .thenThrow(new ContentNotFoundException("Project not found."));

        mockMvc.perform(get("/projects/{id}", PROJECT_ID).with(authenticated()))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.error.code").value("NOT_FOUND"));

        verify(projectService).getById(PROJECT_ID, USER_ID);
    }

    @Test
    void getMyProjects_returns200List() throws Exception {
        when(projectService.getAllByOwner(USER_ID)).thenReturn(List.of(response(), response()));

        mockMvc.perform(get("/projects").with(authenticated()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data").isArray())
                .andExpect(jsonPath("$.data.length()").value(2))
                .andExpect(jsonPath("$.data[0].name").value("Мой бизнес"));

        verify(projectService).getAllByOwner(USER_ID);
    }

    @Test
    void update_returns200() throws Exception {
        when(projectService.update(eq(PROJECT_ID), any(), eq(USER_ID))).thenReturn(response());

        mockMvc.perform(patch("/projects/{id}", PROJECT_ID)
                        .with(authenticated())
                        .contentType("application/json")
                        .content("{\"name\": \"Обновлённый бизнес\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.name").value("Мой бизнес"));

        verify(projectService).update(eq(PROJECT_ID), any(), eq(USER_ID));
    }

    @Test
    void update_whenNotFound_returns404() throws Exception {
        when(projectService.update(eq(PROJECT_ID), any(), eq(USER_ID)))
                .thenThrow(new ContentNotFoundException("Project not found."));

        mockMvc.perform(patch("/projects/{id}", PROJECT_ID)
                        .with(authenticated())
                        .contentType("application/json")
                        .content("{\"name\": \"Обновлённый бизнес\"}"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.error.code").value("NOT_FOUND"));

        verify(projectService).update(eq(PROJECT_ID), any(), eq(USER_ID));
    }

    @Test
    void uploadLogo_returnsLogoPath() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file", "logo.png", "image/png", new byte[]{1, 2, 3});
        when(projectService.uploadLogo(eq(PROJECT_ID), any(), eq(USER_ID))).thenReturn(LOGO_PATH);

        mockMvc.perform(multipart("/projects/{id}/logo", PROJECT_ID)
                        .file(file)
                        .with(authenticated()))
                .andExpect(status().isOk())
                .andExpect(content().string(LOGO_PATH));

        verify(projectService).uploadLogo(eq(PROJECT_ID), any(), eq(USER_ID));
    }

    @Test
    void delete_returns200() throws Exception {
        mockMvc.perform(delete("/projects/{id}", PROJECT_ID).with(authenticated()))
                .andExpect(status().isOk());

        verify(projectService).delete(PROJECT_ID, USER_ID);
    }
}