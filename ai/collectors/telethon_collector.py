"""
Telethon Collector — реальный парсер Telegram-каналов.

Читает API-ключи из переменных окружения (.env):
  TELETHON_API_ID    — числовой App api_id с my.telegram.org
  TELETHON_API_HASH  — строковый App api_hash с my.telegram.org
  TELETHON_SESSION   — имя файла сессии (по умолчанию: ucust_session)

При первом запуске попросит ввести номер телефона и код из Telegram.
После авторизации сессия сохраняется в файл .session и больше не спрашивается.
"""

from __future__ import annotations

import os
import asyncio
from datetime import datetime
from typing import Optional

from schemas.models import CollectorDataSchema

# Флаг: если ключи не заданы — работаем в mock-режиме без ошибок
_API_ID = os.getenv("TELETHON_API_ID", "").strip()
_API_HASH = os.getenv("TELETHON_API_HASH", "").strip()
_SESSION = os.getenv("TELETHON_SESSION", "ucust_session").strip()

_IS_CONFIGURED = bool(_API_ID and _API_HASH and _API_ID.isdigit())


def _mock_payload(channel: str, limit: int) -> dict:
    """Возвращает фиктивные данные когда ключи не настроены."""
    return {
        "channel": channel,
        "limit": limit,
        "fetched_at": datetime.utcnow().isoformat(),
        "mode": "mock",
        "messages": [
            {"id": i, "text": f"[MOCK] Пост {i} из {channel}", "views": 100 + i}
            for i in range(1, limit + 1)
        ],
    }


async def _fetch_channel_async(channel: str, limit: int) -> dict:
    """Асинхронно забирает посты из Telegram-канала через Telethon."""
    from telethon import TelegramClient
    from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

    client = TelegramClient(_SESSION, int(_API_ID), _API_HASH)

    messages_data = []
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print(f"[TelethonCollector] ℹ️ Сессия '{_SESSION}' не авторизована. Переключение в безопасный mock-режим для {channel}.")
            return _mock_payload(channel, limit)
            
        async for message in client.iter_messages(channel, limit=limit):
            # Пропускаем рекламные сообщения (forwarded + без текста)
            if message.fwd_from and not message.text:
                continue
            media_type = None
            media_path = None
            if message.media:
                if isinstance(message.media, MessageMediaPhoto):
                    media_type = "photo"
                    try:
                        if not os.path.exists("temp_media"):
                            os.makedirs("temp_media")
                        filepath = await client.download_media(message, file="temp_media/")
                        media_path = filepath
                    except Exception as e:
                        print(f"Failed to download photo: {e}")
                elif isinstance(message.media, MessageMediaDocument):
                    media_type = "document"

            messages_data.append({
                "id": message.id,
                "text": message.text or "",
                "date": message.date.isoformat() if message.date else None,
                "views": getattr(message, "views", 0) or 0,
                "forwards": getattr(message, "forwards", 0) or 0,
                "media_type": media_type,
                "media_path": media_path,
                "is_forwarded": message.fwd_from is not None,
            })

    finally:
        await client.disconnect()

    return {
        "channel": channel,
        "limit": limit,
        "fetched_at": datetime.utcnow().isoformat(),
        "mode": "real",
        "messages": messages_data,
    }


class TelethonCollector:
    """
    Коллектор постов из Telegram-каналов через Telethon.

    Если TELETHON_API_ID и TELETHON_API_HASH не заданы в .env,
    автоматически переключается в mock-режим без падения пайплайна.
    """

    def collect(self, channel: str, limit: int = 10) -> CollectorDataSchema:
        """
        Синхронная обёртка для вызова из нересинхронного кода.

        :param channel: username канала (например @durov или https://t.me/durov)
        :param limit: максимальное количество постов
        :return: CollectorDataSchema с собранными данными
        """
        if not _IS_CONFIGURED:
            print(
                "[TelethonCollector] TELETHON_API_ID/HASH не заданы в .env — "
                "работаю в mock-режиме."
            )
            payload = _mock_payload(channel, limit)
        else:
            try:
                # Запускаем async-код из sync-контекста
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Уже в async-контексте — создаём новый поток
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as pool:
                            future = pool.submit(
                                asyncio.run, _fetch_channel_async(channel, limit)
                            )
                            payload = future.result(timeout=60)
                    else:
                        payload = loop.run_until_complete(
                            _fetch_channel_async(channel, limit)
                        )
                except RuntimeError:
                    payload = asyncio.run(_fetch_channel_async(channel, limit))

                print(
                    f"[TelethonCollector] Собрано {len(payload['messages'])} "
                    f"постов из {channel}."
                )
            except Exception as exc:
                print(f"[TelethonCollector] Ошибка парсинга: {exc}. Fallback на mock.")
                payload = _mock_payload(channel, limit)

        return CollectorDataSchema(source="telethon", payload=payload)

    async def collect_async(self, channel: str, limit: int = 10) -> CollectorDataSchema:
        """
        Нативный async-метод для вызова из async-контекста (onboarding_pipeline и т.д.).

        :param channel: username канала
        :param limit: максимальное количество постов
        :return: CollectorDataSchema
        """
        if not _IS_CONFIGURED:
            print(
                "[TelethonCollector] TELETHON_API_ID/HASH не заданы — mock-режим."
            )
            payload = _mock_payload(channel, limit)
        else:
            try:
                payload = await _fetch_channel_async(channel, limit)
                print(
                    f"[TelethonCollector] Собрано {len(payload['messages'])} "
                    f"постов из {channel}."
                )
            except Exception as exc:
                print(f"[TelethonCollector] Ошибка: {exc}. Fallback на mock.")
                payload = _mock_payload(channel, limit)

        return CollectorDataSchema(source="telethon", payload=payload)
