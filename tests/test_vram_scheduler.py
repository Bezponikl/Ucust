import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import asyncio
import os
import time
import pytest

AI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai")
if AI_DIR not in sys.path:
    sys.path.insert(0, AI_DIR)

from core.vram_scheduler import VRAMScanner, AutoCalibratingVRAMScheduler


def test_vram_scanner_metrics():
    scanner = VRAMScanner()
    info = scanner.get_vram_info()
    
    assert "total_gb" in info
    assert "used_gb" in info
    assert "free_gb" in info
    assert "usage_percent" in info
    assert info["total_gb"] > 0
    assert info["free_gb"] >= 0


def test_scheduler_initialization_and_costs():
    scanner = VRAMScanner()
    scheduler = AutoCalibratingVRAMScheduler(scanner=scanner, safety_margin_gb=3.0)
    
    # Check default pessimistic costs
    assert scheduler.get_task_estimated_cost("generate_image") >= 14.0
    assert scheduler.get_task_estimated_cost("generate_post") >= 2.0
    assert scheduler.get_task_estimated_cost("parse_website") == 0.0
    assert scheduler.get_task_estimated_cost("parse_vk") == 0.0


def test_non_blocking_io_dispatch():
    async def _run():
        scanner = VRAMScanner()
        scheduler = AutoCalibratingVRAMScheduler(scanner=scanner, safety_margin_gb=3.0)

        # I/O task with 0.0 cost
        async def mock_parser(url: str):
            await asyncio.sleep(0.05)
            return {"parsed_url": url, "status": "success"}

        t0 = time.time()
        # Run 5 parallel I/O tasks simultaneously
        tasks = [
            scheduler.schedule_and_run(f"io_{i}", "parse_website", mock_parser, f"https://site{i}.com")
            for i in range(5)
        ]
        results = await asyncio.gather(*tasks)
        duration = time.time() - t0

        assert len(results) == 5
        assert all(r["status"] == "success" for r in results)
        assert duration < 0.25

    asyncio.run(_run())


def test_spike_tracker_and_ema_calibration():
    async def _run():
        scanner = VRAMScanner()
        scheduler = AutoCalibratingVRAMScheduler(scanner=scanner, safety_margin_gb=3.0)

        async def mock_critic_task():
            await asyncio.sleep(0.1)
            return {"score": 9.5}

        # Execute task with spike tracking
        res = await scheduler.schedule_and_run("test_task_1", "critic_review", mock_critic_task)
        assert res["score"] == 9.5

        # Check history
        assert len(scheduler.history) > 0
        last_exec = scheduler.history[-1]
        assert last_exec["task_type"] == "critic_review"
        assert "calibrated_cost_gb" in last_exec

    asyncio.run(_run())


def test_warmup_routine():
    async def _run():
        scanner = VRAMScanner()
        scheduler = AutoCalibratingVRAMScheduler(scanner=scanner, safety_margin_gb=3.0)
        
        # Warmup should complete cleanly
        await scheduler.warmup_gpu_pipelines(orchestrator=None)
        assert scheduler._is_warmed_up is True

    asyncio.run(_run())


def test_diagnostics_structure():
    scanner = VRAMScanner()
    scheduler = AutoCalibratingVRAMScheduler(scanner=scanner, safety_margin_gb=3.0)
    diag = scheduler.get_diagnostics()

    assert diag["status"] == "healthy"
    assert "gpu_device" in diag
    assert "vram" in diag
    assert "total_gb" in diag["vram"]
    assert "free_gb" in diag["vram"]
    assert "active_workers" in diag
    assert "learned_task_costs" in diag


def test_gpu_status_http_endpoint():
    scanner = VRAMScanner()
    scheduler = AutoCalibratingVRAMScheduler(scanner=scanner, safety_margin_gb=3.0)
    data = scheduler.get_diagnostics()
    assert data["status"] == "healthy"
    assert "vram" in data
    assert "learned_task_costs" in data
    assert "active_workers" in data
    assert "safety_margin_gb" in data["vram"]



if __name__ == "__main__":
    print("▶ Running test_vram_scanner_metrics()...")
    test_vram_scanner_metrics()
    print("✅ test_vram_scanner_metrics() PASSED")

    print("▶ Running test_scheduler_initialization_and_costs()...")
    test_scheduler_initialization_and_costs()
    print("✅ test_scheduler_initialization_and_costs() PASSED")

    print("▶ Running test_non_blocking_io_dispatch()...")
    test_non_blocking_io_dispatch()
    print("✅ test_non_blocking_io_dispatch() PASSED")

    print("▶ Running test_spike_tracker_and_ema_calibration()...")
    test_spike_tracker_and_ema_calibration()
    print("✅ test_spike_tracker_and_ema_calibration() PASSED")

    print("▶ Running test_warmup_routine()...")
    test_warmup_routine()
    print("✅ test_warmup_routine() PASSED")

    print("▶ Running test_diagnostics_structure()...")
    test_diagnostics_structure()
    print("✅ test_diagnostics_structure() PASSED")

    print("▶ Running test_gpu_status_http_endpoint()...")
    test_gpu_status_http_endpoint()
    print("✅ test_gpu_status_http_endpoint() PASSED")

    print("\n🎉 ALL 7 VRAM SCHEDULER TESTS COMPLETED SUCCESSFULLY!")

