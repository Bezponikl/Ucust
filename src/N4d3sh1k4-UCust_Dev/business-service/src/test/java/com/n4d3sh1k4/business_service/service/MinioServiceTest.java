package com.n4d3sh1k4.business_service.service;

import io.minio.GetObjectArgs;
import io.minio.GetObjectResponse;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import io.minio.RemoveObjectArgs;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.util.ReflectionTestUtils;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class MinioServiceTest {

    private static final String BUCKET = "business-service";
    private static final String PATH = "projects/123/logo.png";

    @Mock
    private MinioClient minioClient;

    @InjectMocks
    private MinioService minioService;

    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(minioService, "bucketName", BUCKET);
    }

    @Test
    void uploadFile_returnsPath() throws Exception {
        MockMultipartFile file = new MockMultipartFile("file", "logo.png", "image/png", new byte[]{1, 2, 3});

        String result = minioService.uploadFile(file, PATH);

        assertThat(result).isEqualTo(PATH);
        verify(minioClient).putObject(any(PutObjectArgs.class));
    }

    @Test
    void uploadFile_whenMinioThrows_throwsRuntime() throws Exception {
        MockMultipartFile file = new MockMultipartFile("file", "logo.png", "image/png", new byte[]{1});
        doThrow(new RuntimeException("boom")).when(minioClient).putObject(any(PutObjectArgs.class));

        assertThatThrownBy(() -> minioService.uploadFile(file, PATH))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("Ошибка при загрузке файла");
    }

    @Test
    void downloadFile_returnsInputStream() throws Exception {
        GetObjectResponse response = mock(GetObjectResponse.class);
        when(minioClient.getObject(any(GetObjectArgs.class))).thenReturn(response);

        assertThat(minioService.downloadFile(PATH)).isSameAs(response);
    }

    @Test
    void downloadFile_whenMinioThrows_throwsRuntime() throws Exception {
        doThrow(new RuntimeException("boom")).when(minioClient).getObject(any(GetObjectArgs.class));

        assertThatThrownBy(() -> minioService.downloadFile(PATH))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("Ошибка при скачивании");
    }

    @Test
    void deleteFile_deletes() throws Exception {
        minioService.deleteFile(PATH);

        verify(minioClient).removeObject(any(RemoveObjectArgs.class));
    }

    @Test
    void deleteFile_whenMinioThrows_throwsRuntime() throws Exception {
        doThrow(new RuntimeException("boom")).when(minioClient).removeObject(any(RemoveObjectArgs.class));

        assertThatThrownBy(() -> minioService.deleteFile(PATH))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("Не удалось удалить файл");
    }
}