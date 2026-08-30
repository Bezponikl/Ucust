"""
Integration unit tests for storage/db.py module.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from storage.db import (
    create_task,
    get_task,
    init_db,
    update_task_status,
)

# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_storage_db")


async def run_db_storage_test():
    logger.info("=== Starting SQLAlchemy v2.0 Storage Async Test ===")

    # 1. Initialize DB tables
    await init_db()
    logger.info("[OK] init_db() successfully created tables.")

    # 2. Test create_task
    job_id = await create_task(user_id="async_user_007", status="PENDING")
    assert job_id > 0, "create_task failed to return a valid job_id"
    logger.info("[OK] create_task created task with job_id=%d", job_id)

    # 3. Test get_task
    task = await get_task(job_id=job_id)
    assert task is not None, f"get_task failed to retrieve task with job_id={job_id}"
    assert task.user_id == "async_user_007"
    assert task.status == "PENDING"
    logger.info("[OK] get_task retrieved task: user_id=%s, status=%s", task.user_id, task.status)

    # 4. Test update_task_status
    payload = {"post_text": "Async DB test post draft text", "approval_status": "APPROVED"}
    await update_task_status(
        job_id=job_id,
        status="COMPLETED",
        result_payload=payload,
    )
    logger.info("[OK] update_task_status executed.")

    # 5. Re-fetch task to verify updated payload and status
    updated_task = await get_task(job_id=job_id)
    assert updated_task is not None
    assert updated_task.status == "COMPLETED"
    assert updated_task.post_draft_json == payload
    assert updated_task.result_payload == payload
    logger.info(
        "[OK] Verified updated task status=%s, payload post_text='%.30s'",
        updated_task.status,
        updated_task.result_payload["post_text"],
    )

    logger.info("=== SQLAlchemy v2.0 Storage Async Test SUCCESSFUL ===")


if __name__ == "__main__":
    asyncio.run(run_db_storage_test())
