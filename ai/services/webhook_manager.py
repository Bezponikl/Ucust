"""
File: ai/services/webhook_manager.py
Webhook Callback Manager с экспоненциальным backoff, повторными попытками
и HMAC-подписью для уведомления внешнего бэкенда (Java/Node.js).
"""

from __future__ import annotations

import os
import time
import json
import hmac
import hashlib
import logging
import asyncio
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger("WebhookManager")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "ucust_webhook_hmac_secret_2026")
MAX_RETRIES = int(os.getenv("WEBHOOK_MAX_RETRIES", "3"))
BASE_BACKOFF_SECONDS = float(os.getenv("WEBHOOK_BASE_BACKOFF", "1.0"))


class WebhookCallbackManager:
    """
    Менеджер исходящих вебхуков:
    - Отправляет структурированный payload на callback_url
    - Автоматически применяет Exponential Backoff (1s -> 2s -> 4s)
    - Добавляет X-UCust-Signature (HMAC-SHA256) и X-UCust-Timestamp
    """

    @classmethod
    def generate_signature(cls, payload_bytes: bytes, secret: str = WEBHOOK_SECRET) -> str:
        """Генерация HMAC-SHA256 подписи тела запроса."""
        return hmac.new(
            secret.encode("utf-8"),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()

    @classmethod
    async def send_callback_async(
        cls,
        callback_url: str,
        event_type: str,
        tenant_id: str,
        task_id: str,
        status: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        """
        Асинхронная отправка вебхука с повторными попытками и экспоненциальным backoff.
        """
        if not callback_url:
            return False

        timestamp = int(time.time())
        payload = {
            "event": event_type,
            "status": status,
            "tenant_id": tenant_id,
            "task_id": task_id,
            "timestamp": timestamp,
            "data": data or {},
            "error": error
        }

        payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        signature = cls.generate_signature(payload_bytes)

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "UCust-AI-Webhook-Dispatcher/2.5",
            "X-UCust-Event": event_type,
            "X-UCust-Tenant-Id": tenant_id,
            "X-UCust-Task-Id": task_id,
            "X-UCust-Timestamp": str(timestamp),
            "X-UCust-Signature": signature
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    logger.info(f"📡 [Webhook] Отправка {event_type} на {callback_url} (Попытка {attempt}/{MAX_RETRIES})...")
                    response = await client.post(str(callback_url), content=payload_bytes, headers=headers)
                    
                    if 200 <= response.status_code < 300:
                        logger.info(f"✅ [Webhook] Успешно доставлен (HTTP {response.status_code}) на {callback_url}")
                        return True
                    else:
                        logger.warning(f"⚠️ [Webhook] Сервер вернул HTTP {response.status_code}: {response.text[:150]}")
                except Exception as exc:
                    logger.warning(f"⚠️ [Webhook] Ошибка соединения при попытке {attempt}/{MAX_RETRIES}: {exc}")

                if attempt < MAX_RETRIES:
                    backoff = BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
                    logger.info(f"⏳ [Webhook] Ожидание {backoff}с перед повторной отправкой...")
                    await asyncio.sleep(backoff)

        logger.error(f"❌ [Webhook] Не удалось доставить уведомление на {callback_url} после {MAX_RETRIES} попыток.")
        return False

    @classmethod
    def send_callback_sync(
        cls,
        callback_url: str,
        event_type: str,
        tenant_id: str,
        task_id: str,
        status: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        """Синхронная обертка для вызова из синхронных Celery-воркеров."""
        if not callback_url:
            return False

        coro = cls.send_callback_async(
            callback_url=callback_url,
            event_type=event_type,
            tenant_id=tenant_id,
            task_id=task_id,
            status=status,
            data=data,
            error=error
        )

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                return executor.submit(asyncio.run, coro).result()
        else:
            new_loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(new_loop)
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()

