import sys
import os
os.environ["DATABASE_URL"] = "sqlite:///./ai_smm_dev.db"

import asyncio
from datetime import datetime
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from storage.db import Base
from storage.models import OutboxEvent
from publishers.worker import celery_app, trigger_outbox_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_celery")


def test_celery_outbox_task_flow():
    # 1. Setup DB via DatabaseFactory
    from storage.db import DatabaseFactory, get_async_engine
    eng = get_async_engine()
    sync_eng = eng.sync_engine if hasattr(eng, "sync_engine") else eng
    Base.metadata.create_all(bind=sync_eng)

    session_factory = DatabaseFactory.get_session_factory()
    session = session_factory()

    # 2. Add sample OutboxEvent
    evt = OutboxEvent(
        job_id="job_celery_1",
        target_platform="yandex_maps",
        event_type="REVIEW_REPLY",
        payload={"author": "Анна М.", "text": "Спасибо за отличный сервис!"},
        status="PENDING",
        attempts=0,
        next_attempt_at=datetime.utcnow(),
    )
    session.add(evt)
    session.commit()
    session.close()

    logger.info("Created OutboxEvent in DB.")

    # 3. Verify beat schedule is properly configured
    assert "outbox-fallback-every-3-mins" in celery_app.conf.beat_schedule
    assert celery_app.conf.beat_schedule["outbox-fallback-every-3-mins"]["schedule"] == 180.0

    # 4. Trigger Celery Task directly via .delay()
    res = trigger_outbox_task.delay()
    logger.info("Celery task execution result: %s", res)

    assert res.get("status") == "SUCCESS"
    logger.info("Celery worker test passed successfully!")

    logger.info("Celery worker test passed successfully!")


if __name__ == "__main__":
    test_celery_outbox_task_flow()
