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
from schemas.models import KandinskyPromptSchema, PostDraftSchema

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
    )
    result = await custom_client.send_post_draft(job_id=101, draft=draft)
    assert result is False, "Expected False due to unreachable mock server"
    logger.info("[OK] send_post_draft error handling verified.")

    # 4. Test sending Kandinsky prompts (should catch connection error and return False gracefully)
    prompts = [
        KandinskyPromptSchema(
            prompt_text="Minimalist visual for tech brand",
            style="corporate",
            aspect_ratio="1:1",
        ),
        KandinskyPromptSchema(
            prompt_text="Case study infographics banner",
            style="vector",
            aspect_ratio="16:9",
        ),
    ]
    prompts_result = await custom_client.send_kandinsky_prompts(job_id=101, prompts=prompts)
    assert prompts_result is False, "Expected False due to unreachable mock server"
    logger.info("[OK] send_kandinsky_prompts error handling verified.")

    logger.info("=== JavaBridgeClient Tests Completed Successfully ===")


if __name__ == "__main__":
    asyncio.run(run_java_bridge_test())
