"""
Media Retention & Auto-Archiving Manager for UCust.AI.
Управление жизненным циклом медиафайлов:
- Автоматическая очистка временного кэша и устаревших файлов (> 30 дней)
- Архивация старых генераций для экономии дискового пространства
"""

from __future__ import annotations

import os
import sys
import time
import shutil
import zipfile
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("media_retention")

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MediaRetentionManager:
    """
    Менеджер ротации и очистки файлов на диске.
    Обеспечивает контролируемый TTL (по умолчанию 30 дней).
    """

    def __init__(self, base_output_dir: Optional[str] = None):
        self.output_dir = base_output_dir or os.path.join(AI_ROOT, "output")
        self.temp_cache_dir = os.path.join(self.output_dir, "temp_cache")
        self.photos_dir = os.path.join(self.output_dir, "photos")
        self.videos_dir = os.path.join(self.output_dir, "videos")
        self.archive_dir = os.path.join(self.output_dir, "archive")

        os.makedirs(self.temp_cache_dir, exist_ok=True)
        os.makedirs(self.photos_dir, exist_ok=True)
        os.makedirs(self.videos_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)

    def cleanup_expired_files(
        self,
        retention_days: int = 30,
        temp_cache_retention_hours: float = 5.0,
        archive_generations: bool = True
    ) -> Dict[str, Any]:
        """
        Сканирует директории и удаляет/архивирует файлы:
        - temp_cache: удаляется, если старше temp_cache_retention_hours (по умолчанию 5 часов)
        - photos/videos: архивируются в zip-архив месяца, если старше retention_days (по умолчанию 30 дней)
        """
        now = time.time()
        generations_cutoff = retention_days * 86400
        temp_cutoff = temp_cache_retention_hours * 3600

        deleted_temp_count = 0
        archived_files_count = 0
        freed_bytes = 0
        files_to_archive: List[str] = []

        # 1. Быстрая очистка временного кэша парсинга (TTL 5 часов)
        if os.path.exists(self.temp_cache_dir):
            for filename in os.listdir(self.temp_cache_dir):
                file_path = os.path.join(self.temp_cache_dir, filename)
                if os.path.isfile(file_path):
                    file_age = now - os.path.getmtime(file_path)
                    if file_age > temp_cutoff:
                        size = os.path.getsize(file_path)
                        try:
                            os.remove(file_path)
                            deleted_temp_count += 1
                            freed_bytes += size
                        except Exception as e:
                            logger.warning(f"Error removing temp file {file_path}: {e}")

        # 2. Поиск устаревших генераций (photos & videos, TTL 30 дней)
        for target_dir in [self.photos_dir, self.videos_dir]:
            if os.path.exists(target_dir):
                for filename in os.listdir(target_dir):
                    file_path = os.path.join(target_dir, filename)
                    if os.path.isfile(file_path):
                        file_age = now - os.path.getmtime(file_path)
                        if file_age > generations_cutoff:
                            files_to_archive.append(file_path)

        # 3. Архивация в zip-архив
        if files_to_archive and archive_generations:
            month_str = datetime.utcnow().strftime("%Y_%m")
            zip_filename = f"archive_expired_{month_str}.zip"
            zip_path = os.path.join(self.archive_dir, zip_filename)

            try:
                with zipfile.ZipFile(zip_path, "a", zipfile.ZIP_DEFLATED) as zip_f:
                    for fpath in files_to_archive:
                        arcname = os.path.relpath(fpath, self.output_dir)
                        zip_f.write(fpath, arcname)
                        size = os.path.getsize(fpath)
                        freed_bytes += size
                        os.remove(fpath)
                        archived_files_count += 1
                print(f"[MediaRetention] 📦 Успешно заархивировано {archived_files_count} файлов в {zip_filename}")
            except Exception as ex:
                logger.error(f"[MediaRetention] Ошибка архивации: {ex}")
        elif files_to_archive and not archive_generations:
            for fpath in files_to_archive:
                try:
                    freed_bytes += os.path.getsize(fpath)
                    os.remove(fpath)
                    deleted_temp_count += 1
                except Exception as ex:
                    logger.warning(f"Error removing file {fpath}: {ex}")

        result = {
            "status": "success",
            "retention_days": retention_days,
            "deleted_temp_files": deleted_temp_count,
            "archived_media_files": archived_files_count,
            "freed_megabytes": round(freed_bytes / (1024 * 1024), 2)
        }

        if deleted_temp_count > 0 or archived_files_count > 0:
            print(f"[MediaRetention] 🧹 Очистка завершена: удалено {deleted_temp_count} временных файлов, заархивировано {archived_files_count} генераций. Освобождено {result['freed_megabytes']} МБ.")
        
        return result
