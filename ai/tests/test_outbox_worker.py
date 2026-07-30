import sys
import os
import asyncio
from datetime import datetime, timedelta
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from storage.db import Base
from storage.models import OutboxEvent
from publishers.outbox_worker import process_outbox_events, MAX_ATTEMPTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_outbox")


def test_outbox_worker_flow():
    # 1. Setup in-memory SQLite DB
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    session = Session()

    # 2. Add sample OutboxEvent
    event1 = OutboxEvent(
        job_id="job_test_1",
        target_platform="telegram",
        event_type="PROMO_POST",
        payload={"text": "Привет, мир! Промо-пост UCust.AI"},
        status="PENDING",
        attempts=0,
        next_attempt_at=datetime.utcnow(),
    )
    event2 = OutboxEvent(
        job_id="job_test_1",
        target_platform="yandex_maps",
        event_type="REVIEW_REPLY",
        payload={"author": "Иван П.", "text": "Спасибо за обратную связь!"},
        status="PENDING",
        attempts=0,
        next_attempt_at=datetime.utcnow(),
    )
    session.add_all([event1, event2])
    session.commit()

    logger.info("Created 2 PENDING OutboxEvents for job_test_1.")

    # 3. Process events asynchronously
    processed = asyncio.run(process_outbox_events(session))

    assert len(processed) == 2
    assert event1.status == "COMPLETED"
    assert event1.published_url is not None
    assert "t.me" in event1.published_url

    assert event2.status == "COMPLETED"
    assert event2.published_url is not None
    assert "yandex.ru/maps" in event2.published_url

    logger.info("Outbox worker integration test passed successfully!")


if __name__ == "__main__":
    test_outbox_worker_flow()
