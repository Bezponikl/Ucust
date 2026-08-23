# File: skills/run_comfy_cli.py | Module: skills | Part of Intellectual Property Submission.
"""
CLI entrypoint script for executing ComfyUI LTX-2.3 video generation from terminal.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from skills.comfy_cli_runner import ComfyCLIRunner

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("run_comfy_cli")


async def main():
    parser = argparse.ArgumentParser(description="UCust.AI ComfyUI LTX-2.3 Headless CLI Video Generator")
    parser.add_argument(
        "--workflow",
        type=str,
        default=r"C:\Users\Metal\Desktop\Ltx_generations.json",
        help="Path to ComfyUI workflow JSON graph (default: C:/Users/Metal/Desktop/Ltx_generations.json)",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="Cinematic SMM commercial video for fitness brand, 4k ultra-detailed, smooth motion",
        help="Positive prompt text for video generation",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed for generation")
    parser.add_argument("--url", type=str, default="http://127.0.0.1:8188", help="ComfyUI server URL")

    args = parser.parse_args()

    logger.info("=== Starting ComfyUI LTX-2.3 CLI Video Generation ===")
    runner = ComfyCLIRunner(comfyui_url=args.url, workflow_template_path=args.workflow)

    raw_workflow = runner.load_workflow()
    logger.info("Loaded workflow graph containing %d top-level keys/nodes.", len(raw_workflow))

    result = await runner.execute_workflow(
        workflow_graph=raw_workflow,
        video_prompt=args.prompt,
        seed=args.seed,
    )

    logger.info("=== CLI Generation Completed Successfully ===")
    logger.info("Local Video File: %s", result.get("video_path"))
    logger.info("Local Audio File: %s", result.get("audio_path"))
    logger.info("Video Stream URL: %s", result.get("video_url"))


if __name__ == "__main__":
    asyncio.run(main())
