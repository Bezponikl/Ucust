"""
Integration test suite for bridge/api_controller.py endpoints with database storage.
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

from bridge.api_controller import (
    ProcessRequest,
    UserActionRequest,
    get_status,
    process_request,
    submit_user_action,
)
from integration.java_bridge import JavaBridgeClient
from storage.db import init_db

# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_api_controller")


class MockBackgroundTasks:
    """Mock FastAPI BackgroundTasks for direct execution during testing."""

    def __init__(self):
        self.tasks = []

    def add_task(self, func, *args, **kwargs):
        self.tasks.append((func, args, kwargs))
        # Handle async function execution if needed
        if asyncio.iscoroutinefunction(func):
            asyncio.create_task(func(*args, **kwargs))
        else:
            func(*args, **kwargs)


class MockJavaBridgeClient(JavaBridgeClient):
    """Mock JavaBridgeClient for recording calls without making network requests."""

    def __init__(self):
        super().__init__(base_url="http://mock-java:8080/api/v1")
        self.sent_drafts = []
        self.sent_prompts = []

    async def send_post_draft(self, job_id, draft):
        self.sent_drafts.append((job_id, draft))
        logger.info("[MockJavaBridgeClient] Recorded send_post_draft for job_id=%d", job_id)
        return True

    async def send_ltx23_prompts(self, job_id, prompts):
        self.sent_prompts.append((job_id, prompts))
        logger.info("[MockJavaBridgeClient] Recorded send_ltx23_prompts for job_id=%d", job_id)
        return True


async def run_api_lifecycle_test():
    logger.info("=== Starting API Controller Database Integration Lifecycle Test ===")

    # 1. Initialize database tables
    await init_db()

    mock_java_bridge = MockJavaBridgeClient()
    bg_tasks = MockBackgroundTasks()

    # 2. Test process_request (POST /api/v1/process)
    req = ProcessRequest(user_id="test_db_user_999")
    resp = await process_request(payload=req, background_tasks=bg_tasks, session=None)
    assert resp.status == "accepted"
    assert resp.job_id > 0
    job_id = resp.job_id
    logger.info("[OK] process_request accepted. job_id=%d", job_id)

    # Allow async background task to complete orchestrator steps
    await asyncio.sleep(0.2)

    # 3. Test get_status (GET /api/v1/status/{job_id})
    status_resp = await get_status(job_id=job_id, session=None)
    assert status_resp.status == "AWAITING_USER_ACTION"
    assert status_resp.action_required is True
    assert status_resp.result is not None
    logger.info("[OK] get_status returned status=%s", status_resp.status)

    # 4. Test submit_user_action EDIT (POST /api/v1/action/{job_id})
    edit_req = UserActionRequest(
        action="EDIT",
        event_type="gratitude",
        context="Спасибо нашим постоянным клиентам!",
    )
    edit_resp = await submit_user_action(job_id=job_id, payload=edit_req, session=None, java_bridge=mock_java_bridge)
    assert edit_resp.status == "AWAITING_USER_ACTION"
    assert "Gratitude Post" in edit_resp.result
    logger.info("[OK] submit_user_action EDIT successful.")

    # 5. Test submit_user_action APPROVED (POST /api/v1/action/{job_id})
    approve_req = UserActionRequest(action="APPROVED")
    approve_resp = await submit_user_action(job_id=job_id, payload=approve_req, session=None, java_bridge=mock_java_bridge)
    assert approve_resp.status == "COMPLETED"
    logger.info("[OK] submit_user_action APPROVED successful.")

    # 6. Verify JavaBridgeClient dispatching
    assert len(mock_java_bridge.sent_drafts) == 1, "Expected 1 post draft sent to Java bridge"
    assert len(mock_java_bridge.sent_prompts) == 1, "Expected 1 set of Kandinsky prompts sent to Java bridge"
    logger.info("[OK] Verified JavaBridgeClient received draft & prompts.")

    logger.info("=== API Controller Lifecycle Test SUCCESSFUL ===")


if __name__ == "__main__":
    asyncio.run(run_api_lifecycle_test())
