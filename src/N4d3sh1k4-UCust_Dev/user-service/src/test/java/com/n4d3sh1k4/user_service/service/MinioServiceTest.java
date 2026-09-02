package com.n4d3sh1k4.user_service.service;

import io.minio.GetObjectArgs;
import io.minio.GetObjectResponse;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import io.minio.RemoveObjectArgs;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class MinioServiceTest {

    private static final String BUCKET = "user-service";

    @Mock
    private MinioClient minioClient;

    @InjectMocks
    private MinioService minioService;

    private MultipartFile file;

    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(minioService, "bucketName", BUCKET);
        file = new MockMultipartFile("file", "avatar.jpg", "image/jpeg", new byte[]{1, 2, 3});
    }

    @Test
    void uploadFile_success_returnsPath() throws Exception {
        when(minioClient.putObject(any(PutObjectArgs.class))).thenReturn(null);

        String result = minioService.uploadFile(file, "avatars/uuid.jpg");

        ArgumentCaptor<PutObjectArgs> captor = ArgumentCaptor.forClass(PutObjectArgs.class);
        verify(minioClient).putObject(captor.capture());
        assertThat(captor.getValue().bucket()).isEqualTo(BUCKET);
        assertThat(captor.getValue().object()).isEqualTo("avatars/uuid.jpg");
        assertThat(result).isEqualTo("avatars/uuid.jpg");
    }

    @Test
    void uploadFile_whenMinioThrows_throwsRuntimeException() throws Exception {
        when(minioClient.putObject(any(PutObjectArgs.class)))
                .thenThrow(new IllegalStateException("connection refused"));

        assertThatThrownBy(() -> minioService.uploadFile(file, "avatars/uuid.jpg"))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("Ошибка при загрузке файла в хранилище");
    }

    @Test
    void downloadFile_success_returnsStream() throws Exception {
        GetObjectResponse response = mock(GetObjectResponse.class);
        when(minioClient.getObject(any(GetObjectArgs.class))).thenReturn(response);

        InputStream result = minioService.downloadFile("avatars/uuid.jpg");

        assertThat(result).isSameAs(response);
        ArgumentCaptor<GetObjectArgs> captor = ArgumentCaptor.forClass(GetObjectArgs.class);
        verify(minioClient).getObject(captor.capture());
        assertThat(captor.getValue().bucket()).isEqualTo(BUCKET);
        assertThat(captor.getValue().object()).isEqualTo("avatars/uuid.jpg");
    }

    @Test
    void downloadFile_whenMinioThrows_throwsRuntimeException() throws Exception {
        when(minioClient.getObject(any(GetObjectArgs.class)))
                .thenThrow(new IllegalStateException("not found"));

        assertThatThrownBy(() -> minioService.downloadFile("avatars/uuid.jpg"))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("Ошибка при скачивании файла");
    }

    @Test
    void deleteFile_success_callsRemoveObject() throws Exception {
        minioService.deleteFile("avatars/uuid.jpg");

        ArgumentCaptor<RemoveObjectArgs> captor = ArgumentCaptor.forClass(RemoveObjectArgs.class);
        verify(minioClient).removeObject(captor.capture());
        assertThat(captor.getValue().bucket()).isEqualTo(BUCKET);
        assertThat(captor.getValue().object()).isEqualTo("avatars/uuid.jpg");
    }

    @Test
    void deleteFile_whenMinioThrows_throwsRuntimeException() throws Exception {
        doThrow(new IllegalStateException("permission denied"))
                .when(minioClient).removeObject(any(RemoveObjectArgs.class));

        assertThatThrownBy(() -> minioService.deleteFile("avatars/uuid.jpg"))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("Не удалось удалить файл из MinIO");
    }
}