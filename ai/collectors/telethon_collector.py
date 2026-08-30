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


def _get_proxy_config() -> Optional[dict]:
    """
    Формирует конфигурацию прокси для Telethon из .env (SOCKS5 / HTTP / MTProto).
    Поддерживает как TELETHON_PROXY_URL, так и раздельные параметры.
    """
    proxy_url = os.getenv("TELETHON_PROXY_URL", "").strip()
    proxy_type_env = os.getenv("TELETHON_PROXY_TYPE", "").strip().lower()
    proxy_host = os.getenv("TELETHON_PROXY_HOST", "").strip()
    proxy_port = os.getenv("TELETHON_PROXY_PORT", "").strip()
    proxy_user = os.getenv("TELETHON_PROXY_USER", "").strip() or None
    proxy_pass = os.getenv("TELETHON_PROXY_PASSWORD", "").strip() or None

    if proxy_url:
        import urllib.parse
        parsed = urllib.parse.urlparse(proxy_url)
        proxy_type_env = parsed.scheme.lower()
        proxy_host = parsed.hostname or ""
        proxy_port = str(parsed.port or 1080)
        proxy_user = parsed.username
        proxy_pass = parsed.password

    if not proxy_host or not proxy_port or not proxy_port.isdigit():
        return None

    # Определение типа прокси (1=SOCKS4, 2=SOCKS5, 3=HTTP)
    ptype = 2 if "socks5" in proxy_type_env else (1 if "socks4" in proxy_type_env else 3)
    
    proxy_dict = {
        'proxy_type': ptype,
        'addr': proxy_host,
        'port': int(proxy_port),
        'username': proxy_user,
        'password': proxy_pass,
        'rdns': True
    }
    print(f"[TelethonCollector] 🛡️ Использование прокси: {proxy_type_env or 'socks5'}://{proxy_host}:{proxy_port}")
    return proxy_dict


def _mock_payload(channel: str, limit: int) -> dict:
    """Возвращает фиктивные данные с анализом комментариев аудитории."""
    mock_comments = [
        {"id": 101, "author": "Алексей", "text": "А сколько времени уходит на запуск системы в реальный бизнес?", "likes": 4},
        {"id": 102, "author": "Елена", "text": "Работает ли это для сложных ниш и B2B услуг?", "likes": 7},
        {"id": 103, "author": "Михаил", "text": "Главное чтобы тексты были без шаблонной воды и отсекались клише.", "likes": 12},
    ]
    return {
        "channel": channel,
        "limit": limit,
        "fetched_at": datetime.utcnow().isoformat(),
        "mode": "mock",
        "messages": [
            {
                "id": i,
                "text": f"[MOCK] Пост {i} из {channel}. Опыт внедрения мульти-агентных систем для автоматизации контента.",
                "views": 100 + i * 25,
                "comments_count": len(mock_comments),
                "comments": mock_comments,
                "top_objections_from_comments": [
                    "Сроки запуска и окупаемость",
                    "Применимость для сложных ниш",
                    "Защита от шаблонных текстов"
                ]
            }
            for i in range(1, limit + 1)
        ],
    }


async def _fetch_channel_async(channel: str, limit: int) -> dict:
    """Асинхронно забирает посты и комментарии из Telegram-канала через Telethon."""
    from telethon import TelegramClient
    from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

    proxy = _get_proxy_config()
    client = TelegramClient(_SESSION, int(_API_ID), _API_HASH, proxy=proxy)

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

            # Сбор комментариев / ответов под постом
            comments = []
            comments_count = 0
            if getattr(message, "replies", None):
                comments_count = getattr(message.replies, "replies", 0) or 0
                if comments_count > 0:
                    try:
                        async for reply in client.iter_messages(channel, reply_to=message.id, limit=5):
                            if reply.text:
                                comments.append({
                                    "id": reply.id,
                                    "text": reply.text,
                                    "date": reply.date.isoformat() if reply.date else None,
                                    "sender_id": reply.sender_id
                                })
                    except Exception:
                        pass

            messages_data.append({
                "id": message.id,
                "text": message.text or "",
                "date": message.date.isoformat() if message.date else None,
                "views": getattr(message, "views", 0) or 0,
                "forwards": getattr(message, "forwards", 0) or 0,
                "comments_count": comments_count,
                "comments": comments,
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
