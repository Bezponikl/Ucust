"""
Celery Worker & Celery Beat Scheduler for Transactional Outbox Pattern in UCust.AI.
Uses Redis as Broker and Result Backend.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

try:
    from celery import Celery
except ImportError:
    # Мок-адаптер Celery для окружений, где пакет celery не установлен
    class Celery:  # type: ignore
        def __init__(self, name: str, broker: str = None, backend: str = None):
            self.name = name
            self.broker = broker
            self.backend = backend
            self.conf = type("Conf", (), {"beat_schedule": {}, "timezone": "UTC"})()

        def task(self, *args, **kwargs):
            def decorator(func):
                def delay(*dargs, **dkwargs):
                    logger.info("Celery Mock: синхронный триггер таски '%s' (fallback).", func.__name__)
                    # Создаем мок-объект self с методом retry
                    class MockTaskSelf:
                        def retry(self, exc=None, countdown=60):
                            raise exc or RuntimeError("Celery Mock retry")
                    return func(MockTaskSelf(), *dargs, **dkwargs)
                func.delay = delay
                return func
            return decorator

from publishers.outbox_worker import process_outbox_events
from storage.db import DatabaseFactory

logger = logging.getLogger("celery_worker")

# 1. Инициализация экземпляра Celery с Redis брокером и бэкендом
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "ucust_outbox_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# 2. Настройка Celery Beat подстраховки (периодический запуск раз в 3 минуты)
celery_app.conf.beat_schedule = {
    "outbox-fallback-every-3-mins": {
        "task": "tasks.trigger_outbox",
        "schedule": 180.0,  # Запуск раз в 3 минуты (180 сек)
    },
}
celery_app.conf.timezone = "UTC"


# 3. Определение Celery Таски
@celery_app.task(name="tasks.trigger_outbox", bind=True, max_retries=3)
def trigger_outbox_task(self: Any) -> dict[str, Any]:
    """
    Celery Таска для разгребания очереди OutboxEvent.
    Вызывается реактивно сразу после session.commit() или подстраховочно по расписанию Celery Beat.
    """
    logger.info("Celery Task 'tasks.trigger_outbox' запущена...")
    session_factory = DatabaseFactory.get_session_factory()
    db_session = session_factory()

    try:
        # Вызов асинхронного разгребателя очереди outbox через asyncio.run()
        processed = asyncio.run(process_outbox_events(db_session))
        logger.info("Celery Task 'tasks.trigger_outbox' успешно завершена. Обработано событий: %d", len(processed))
        return {"status": "SUCCESS", "processed_count": len(processed)}
    except Exception as exc:
        logger.error("Celery Task 'tasks.trigger_outbox' ошибка: %s. Вызов retry...", exc)
        try:
            db_session.rollback()
        except Exception:
            pass
        # Повторная попытка таски при сбое брокера с задержкой 60 сек
        if hasattr(self, "retry"):
            raise self.retry(exc=exc, countdown=60)
        raise exc
    finally:
        db_session.close()
