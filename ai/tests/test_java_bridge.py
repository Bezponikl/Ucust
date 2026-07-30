"""
Unit tests for integration.java_bridge module.
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

from integration.java_bridge import JavaBridgeClient, get_java_bridge_client
from schemas.models import LTX23PromptSchema, PostDraftSchema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_java_bridge")


async def run_java_bridge_test():
    logger.info("=== Testing JavaBridgeClient Integration Module ===")

    # 1. Test Singleton & Dependency Injection provider
    client1 = get_java_bridge_client()
    client2 = get_java_bridge_client()
    assert client1 is client2, "get_java_bridge_client() did not return a singleton instance"
    logger.info("[OK] Singleton instance verified.")

    # 2. Test initialization with custom parameters
    custom_client = JavaBridgeClient(base_url="http://mock-java-server:9090/api/v1", timeout=5.0)
    assert custom_client.base_url == "http://mock-java-server:9090/api/v1"
    assert custom_client.timeout == 5.0
    logger.info("[OK] Custom initialization verified.")

    # 3. Test sending post draft (should catch connection error and return False gracefully)
    draft = PostDraftSchema(
        text="Test post draft content for integration test.",
        uniqueness_score=0.95,
        duplicates_found=False,
        video_url="http://media-server/video1.mp4",
        audio_url="http://media-server/audio1.mp3",
    )
    result = await custom_client.send_post_draft(job_id=101, draft=draft)
    assert result is False, "Expected False due to unreachable mock server"
    logger.info("[OK] send_post_draft error handling verified.")

    # 4. Test sending LTX-2.3 prompts (should catch connection error and return False gracefully)
    prompts = [
        LTX23PromptSchema(
            video_prompt="Cinematic motion visual for tech brand",
            audio_prompt="Ambient corporate soundscape",
            aspect_ratio="16:9",
        ),
        LTX23PromptSchema(
            video_prompt="Case study motion graphics video",
            audio_prompt="Upbeat synth pads and audio effects",
            aspect_ratio="16:9",
        ),
    ]
    prompts_result = await custom_client.send_ltx23_prompts(job_id=101, prompts=prompts)
    assert prompts_result is False, "Expected False due to unreachable mock server"
    logger.info("[OK] send_ltx23_prompts error handling verified.")

    logger.info("=== JavaBridgeClient Tests Completed Successfully ===")


if __name__ == "__main__":
    asyncio.run(run_java_bridge_test())
