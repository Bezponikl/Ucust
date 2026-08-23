from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from storage.models import OutboxEvent

logger = logging.getLogger("outbox_worker")

MAX_ATTEMPTS = 4


class RateLimitException(Exception):
    """Исключение превышения лимитов API платформы (429 Too Many Requests / Rate Limit)."""
    pass


class GeoPublisherAdapter:
    """Адаптер для ответа на отзывы в геосервисах (Яндекс.Карты / 2GIS)."""

    def __init__(self, platform_name: str) -> None:
        self.platform_name = platform_name

    async def publish(self, payload: Dict[str, Any]) -> str:
        author = payload.get("author", "Пользователь")
        reply_text = payload.get("text") or payload.get("reply_text") or "Спасибо за отзыв!"
        logger.info(
            "GeoPublisherAdapter [%s]: публикация ответа бренду для автора '%s'...",
            self.platform_name,
            author,
        )
        await asyncio.sleep(0.1)  # Имитация запроса к API геосервиса
        if self.platform_name == "yandex_maps":
            return f"https://yandex.ru/maps/org/review_reply/{abs(hash(author)) % 10000}"
        return f"https://2gis.ru/firm/review_reply/{abs(hash(author)) % 10000}"


class MockSocialPublisherAdapter:
    """Адаптер публикации для соцсетей (Telegram, VK API)."""

    def __init__(self, platform_name: str) -> None:
        self.platform_name = platform_name

    async def publish(self, payload: Dict[str, Any]) -> str:
        text = payload.get("text", "")
        media_path = payload.get("media_path")
        logger.info(
            "MockSocialPublisherAdapter [%s]: публикация поста (media=%s)...",
            self.platform_name,
            media_path or "нет",
        )
        await asyncio.sleep(0.1)
        if self.platform_name == "telegram":
            return f"https://t.me/ucust_official/{abs(hash(text)) % 1000}"
        return f"https://vk.com/wall-2000123_{abs(hash(text)) % 1000}"


def get_publisher_adapter(platform_name: str) -> Any:
    """Фабрика адаптеров публикации по имени целевой платформы."""
    platform = platform_name.lower()
    if platform in ("yandex_maps", "twogis"):
        return GeoPublisherAdapter(platform)
    return MockSocialPublisherAdapter(platform)


async def process_outbox_events(db_session: Session) -> List[OutboxEvent]:
    """
    Разгребатель очереди Transactional Outbox Pattern.
    Берет PENDING записи с наступившим временем next_attempt_at и выполняет их отправку с экспоненциальными ретраями.
    """
    now = datetime.utcnow()
    # Запрос необработанных событий
    stmt = (
        select(OutboxEvent)
        .where(
            OutboxEvent.status == "PENDING",
            OutboxEvent.next_attempt_at <= now,
        )
        .with_for_update()
    )
    events = list(db_session.scalars(stmt).all())

    if not events:
        return []

    processed_events: List[OutboxEvent] = []

    for event in events:
        event.status = "PROCESSING"
        event.updated_at = datetime.utcnow()
        db_session.commit()

        try:
            adapter = get_publisher_adapter(event.target_platform)
            published_url = await adapter.publish(event.payload)

            event.status = "COMPLETED"
            event.published_url = published_url
            event.error_message = None
            event.updated_at = datetime.utcnow()
            logger.info(
                "OutboxWorker: Успешно опубликовано в [%s] для job_id='%s'. URL: %s",
                event.target_platform,
                event.job_id,
                published_url,
            )

        except Exception as exc:
            event.attempts += 1
            event.updated_at = datetime.utcnow()
            if event.attempts >= MAX_ATTEMPTS:
                event.status = "FAILED"
                event.error_message = f"Max retries reached ({MAX_ATTEMPTS}). Error: {exc}"
                logger.error(
                    "OutboxWorker: Достигнут лимит ретраев (%d) для [%s] (job_id='%s'). Ошибка: %s",
                    MAX_ATTEMPTS,
                    event.target_platform,
                    event.job_id,
                    exc,
                )
            else:
                event.status = "PENDING"
                # Экспоненциальная задержка: 2^attempts минут (2, 4, 8, 16...)
                delay_minutes = 2 ** event.attempts
                event.next_attempt_at = datetime.utcnow() + timedelta(minutes=delay_minutes)
                event.error_message = str(exc)
                logger.warning(
                    "OutboxWorker: Ошибка публикации в [%s] (job_id='%s'). Попытка %d/%d. Следующий ретрай через %d мин. Ошибка: %s",
                    event.target_platform,
                    event.job_id,
                    event.attempts,
                    MAX_ATTEMPTS,
                    delay_minutes,
                    exc,
                )

        db_session.commit()
        processed_events.append(event)

    return processed_events


async def start_outbox_worker_loop(db_session_factory: Any, poll_interval_seconds: int = 10) -> None:
    """Фоновый воркер-цикл для постоянной выгрузки очереди публикаций Outbox."""
    logger.info("OutboxWorker loop запущен (poll_interval=%d сек)...", poll_interval_seconds)
    while True:
        try:
            with db_session_factory() as session:
                await process_outbox_events(session)
        except Exception as exc:
            logger.error("OutboxWorker loop error: %s", exc)
        await asyncio.sleep(poll_interval_seconds)
