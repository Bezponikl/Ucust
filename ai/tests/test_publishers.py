"""
Test suite for publishers package and Human-in-the-Loop export/publish endpoints.
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
    get_pending_posts,
    get_status,
    process_request,
    publish_post,
)
from publishers import (
    InstagramPublisher,
    OdnoklassnikiPublisher,
    TelegramPublisher,
    VkPublisher,
    get_publisher,
)
from schemas.models import PublishRequestSchema
from storage.db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_publishers")


class MockBackgroundTasks:
    """Mock BackgroundTasks runner."""

    def add_task(self, func, *args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            asyncio.create_task(func(*args, **kwargs))
        else:
            func(*args, **kwargs)


async def run_publishers_test():
    logger.info("=== Starting Multi-Platform Publishers Subsystem Integration Test ===")

    # 1. Test TelegramPublisher directly
    tg_pub = get_publisher("telegram")
    res_tg = await tg_pub.publish("Test Telegram Post", media_path="output/demo_video.mp4")
    assert res_tg is True
    logger.info("[OK] TelegramPublisher direct publish test passed.")

    # 2. Test VkPublisher directly
    vk_pub = get_publisher("vk")
    res_vk = await vk_pub.publish("Test VK Post", media_path="output/demo_video.mp4")
    assert res_vk is True
    logger.info("[OK] VkPublisher direct publish test passed.")

    # 3. Test InstagramPublisher directly
    ig_pub = get_publisher("instagram")
    # Instagram requires a media file (returns False if missing, True if valid file simulated)
    res_ig_no_file = await ig_pub.publish("Test IG Post", media_path=None)
    assert res_ig_no_file is False, "Instagram should reject text-only posts without media"
    logger.info("[OK] InstagramPublisher media validation test passed.")

    # 4. Test OdnoklassnikiPublisher directly
    ok_pub = get_publisher("ok")
    res_ok = await ok_pub.publish("Test OK Post", media_path="output/demo_video.mp4")
    assert res_ok is True
    logger.info("[OK] OdnoklassnikiPublisher direct publish test passed.")

    # 5. Test MaxPublisher directly
    max_pub = get_publisher("max")
    res_max = await max_pub.publish("Test MAX Post", media_path="output/demo_video.mp4")
    assert res_max is True
    logger.info("[OK] MaxPublisher direct publish test passed.")

    # 6. Test API Endpoint Lifecycle across all platforms (Telegram, VK, OK, MAX)
    await init_db()
    bg_tasks = MockBackgroundTasks()

    # Step A: Initiate background pipeline job
    proc_req = ProcessRequest(user_id="test_multi_publisher_user")
    proc_resp = await process_request(payload=proc_req, background_tasks=bg_tasks, session=None)
    job_id = proc_resp.job_id
    logger.info("[OK] Process request accepted with job_id=%d", job_id)

    # Allow task to reach AWAITING_USER_ACTION status
    await asyncio.sleep(0.3)

    # Step B: GET /api/v1/posts/pending export endpoint
    pending_posts = await get_pending_posts(session=None)
    assert len(pending_posts) >= 1, "Expected at least 1 pending post"
    matching_post = next((p for p in pending_posts if p.job_id == job_id), None)
    assert matching_post is not None, f"Expected pending post with job_id={job_id}"
    logger.info("[OK] GET /api/v1/posts/pending returned pending post with ID=%d", job_id)

    # Step C: POST /api/v1/posts/{post_id}/publish with all target platforms including MAX
    pub_req = PublishRequestSchema(
        target_platforms=["telegram", "vk", "ok", "max"],
        custom_caption="Финальный пост для публикации в TG, VK, OK и MAX",
    )
    pub_resp = await publish_post(post_id=job_id, payload=pub_req, session=None)

    assert pub_resp["status"] == "PUBLISHED"
    assert "telegram" in pub_resp["publish_results"]
    assert "vk" in pub_resp["publish_results"]
    assert "ok" in pub_resp["publish_results"]
    assert "max" in pub_resp["publish_results"]
    logger.info("[OK] POST /api/v1/posts/%d/publish successfully published across all requested platforms.", job_id)

    # Step D: Verify final status in DB
    final_status = await get_status(job_id=job_id, session=None)
    assert final_status.status == "PUBLISHED"
    logger.info("[OK] Final DB status verified as PUBLISHED.")

    logger.info("=== Multi-Platform Publishers Subsystem Integration Test SUCCESSFUL ===")


if __name__ == "__main__":
    asyncio.run(run_publishers_test())
