"""
Unit test for ComfyUILocalSkill and Single-Server ComfyUI integration.
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

from skills.comfyui_local import ComfyUILocalSkill

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_comfyui_local")


async def run_comfyui_local_test():
    logger.info("=== Starting ComfyUILocalSkill Single-Server Integration Test ===")

    skill = ComfyUILocalSkill(comfyui_url="http://127.0.0.1:8188")
    mock_workflow = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "ltx-2.3-22b-dev.safetensors"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "gemma_3_12B_it_fp4_mixed.safetensors"}},
    }

    # 1. Test workflow submission
    res = await skill.submit_workflow(mock_workflow)
    assert "prompt_id" in res, "Expected prompt_id in ComfyUI submission response"
    prompt_id = res["prompt_id"]
    logger.info("[OK] submit_workflow returned prompt_id=%s", prompt_id)

    # 2. Test fetching generated media paths
    media_info = await skill.fetch_generated_media(prompt_id)
    assert "video_path" in media_info, "Expected video_path in media info"
    assert "audio_path" in media_info, "Expected audio_path in media info"
    assert "video_url" in media_info, "Expected video_url in media info"
    assert "127.0.0.1:8188" in media_info["video_url"], "Expected local loopback 127.0.0.1:8188 in video URL"

    logger.info("[OK] fetch_generated_media resolved local paths: %s", media_info["video_path"])
    logger.info("[OK] Local URL resolved: %s", media_info["video_url"])
    logger.info("=== ComfyUILocalSkill Test SUCCESSFUL ===")


if __name__ == "__main__":
    asyncio.run(run_comfyui_local_test())
