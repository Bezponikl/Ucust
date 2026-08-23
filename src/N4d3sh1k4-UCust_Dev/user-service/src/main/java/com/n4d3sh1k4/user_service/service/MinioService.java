package com.n4d3sh1k4.user_service.service;

import io.minio.*;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;

@Service
@RequiredArgsConstructor
public class MinioService {
    private final MinioClient minioClient;

    @Value("${minio.bucket}")
    private String bucketName;

    public String uploadFile(MultipartFile file, String path) {
        try {
            // Загружаем объект
            minioClient.putObject(
                PutObjectArgs.builder()
                    .bucket(bucketName)
                    .object(path)
                    .stream(file.getInputStream(), file.getSize(), (long) -1)
                    .contentType(file.getContentType()) // Позволяет браузеру сразу отображать фото
                    .build()
            );

            // Возвращаем путь (или можно сразу генерировать временную ссылку)
            return path;

        } catch (Exception e) {
            throw new RuntimeException("Ошибка при загрузке файла в хранилище: " + e.getMessage());
        }
    }

    public InputStream downloadFile(String filename) {
        try {
            return minioClient.getObject(
                GetObjectArgs.builder()
                    .bucket(bucketName)
                    .object(filename)
                    .build());
        } catch (Exception e) {
            throw new RuntimeException("Ошибка при скачивании файла: " + e.getMessage());
        }
    }

    public void deleteFile(String filename) {
    try {
        minioClient.removeObject(
            RemoveObjectArgs.builder()
                .bucket(bucketName)
                .object(filename)
                .build()
        );
    } catch (Exception e) {
        // Логируем ошибку или пробрасываем кастомное исключение
        throw new RuntimeException("Не удалось удалить файл из MinIO: " + e.getMessage());
    }
}
}
