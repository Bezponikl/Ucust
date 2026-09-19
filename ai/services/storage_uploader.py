"""
File: ai/services/storage_uploader.py
Сервис загрузки медиа-файлов в объектное хранилище S3 (MinIO / Yandex Cloud)
с автоматическим fallback на локальную раздачу статики.
"""

from __future__ import annotations

import os
import logging
import asyncio
from typing import Optional

logger = logging.getLogger("StorageUploader")

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "ucust-media")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_PUBLIC_DOMAIN = os.getenv("S3_PUBLIC_DOMAIN", "https://s3.ucust.ai/media")
LOCAL_OUTPUT_DIR = os.getenv("MEDIA_OUTPUT_DIR", os.path.abspath("./output/photos"))


class StorageUploader:
    """
    Унифицированный загрузчик файлов:
    1. При наличии S3 учетных данных: загружает в бакет через boto3/aiobotocore.
    2. В dev-режиме / без S3: сохраняет в локальный каталог output/photos и отдает относительный URL.
    """

    def __init__(self):
        self.has_s3 = bool(S3_ENDPOINT_URL and S3_ACCESS_KEY and S3_SECRET_KEY)
        os.makedirs(LOCAL_OUTPUT_DIR, exist_ok=True)

    async def upload_bytes(self, data: bytes, destination_key: str, content_type: str = "image/jpeg") -> str:
        """
        Загружает байты и возвращает публичный URL.
        """
        if self.has_s3:
            try:
                # Асинхронный вызов S3 PutObject через ThreadPool
                return await self._upload_to_s3(data, destination_key, content_type)
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки в S3: {e}. Сохраняем локально...")

        # Локальное сохранение
        return await self._save_locally(data, destination_key)

    async def _upload_to_s3(self, data: bytes, destination_key: str, content_type: str) -> str:
        import boto3
        loop = asyncio.get_running_loop()

        def _sync_put():
            client = boto3.client(
                "s3",
                endpoint_url=S3_ENDPOINT_URL,
                aws_access_key_id=S3_ACCESS_KEY,
                aws_secret_access_key=S3_SECRET_KEY,
            )
            client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=destination_key,
                Body=data,
                ContentType=content_type
            )
            return f"{S3_PUBLIC_DOMAIN.rstrip('/')}/{destination_key.lstrip('/')}"

        return await loop.run_in_executor(None, _sync_put)

    async def _save_locally(self, data: bytes, destination_key: str) -> str:
        filename = os.path.basename(destination_key)
        local_path = os.path.join(LOCAL_OUTPUT_DIR, filename)
        
        loop = asyncio.get_running_loop()
        def _sync_write():
            with open(local_path, "wb") as f:
                f.write(data)
            return f"/output/photos/{filename}"

        return await loop.run_in_executor(None, _sync_write)


# Глобальный инстанс
default_storage_uploader = StorageUploader()


async def upload_media_bytes(data: bytes, destination_key: str) -> str:
    """Хелпер для использования в качестве uploader функции."""
    return await default_storage_uploader.upload_bytes(data, destination_key)
