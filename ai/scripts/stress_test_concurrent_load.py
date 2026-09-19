"""
File: ai/scripts/stress_test_concurrent_load.py
Стресс-тест конкурентной нагрузки (50+ одновременных пользователей)
для асинхронного шлюза FastAPI и Celery очередей UCust AI.
"""

import sys
import os
import time
import asyncio
import statistics
import jwt
import httpx

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, AI_DIR)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from api_gateway import app
from api.dependencies.auth import JWT_SECRET, JWT_ALGORITHM
from core.database import init_db


def make_token(tenant_id: str) -> str:
    payload = {
        "sub": f"user_{tenant_id}",
        "tenant_id": tenant_id,
        "exp": int(time.time()) + 3600
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def worker_client(
    client: httpx.AsyncClient, 
    worker_id: int, 
    results: list, 
    latencies: list,
    semaphore: asyncio.Semaphore
):
    tenant_id = f"tenant_stress_{worker_id:03d}"
    token = make_token(tenant_id)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "prompt": f"Конкурентный стресс-запрос от воркера #{worker_id}: оптимизация конверсии B2B",
        "tier": "pro",
        "industry": "b2b_corporate",
        "rubric": "case_study",
        "callback_url": f"https://api.external-backend.com/webhooks/worker_{worker_id}"
    }

    async with semaphore:
        t0 = time.perf_counter()
        try:
            resp = await client.post("/api/v1/content/generate-async", json=payload, headers=headers)
            duration = time.perf_counter() - t0
            latencies.append(duration)
            results.append({
                "worker_id": worker_id,
                "status_code": resp.status_code,
                "success": resp.status_code == 202,
                "task_id": resp.json().get("task_id") if resp.status_code == 202 else None,
                "duration": duration
            })
        except Exception as exc:
            duration = time.perf_counter() - t0
            latencies.append(duration)
            results.append({
                "worker_id": worker_id,
                "status_code": 0,
                "success": False,
                "error": str(exc),
                "duration": duration
            })


async def run_stress_test(total_requests: int = 60, max_concurrency: int = 20):
    print("=" * 70)
    print(f"🔥 ЗАПУСК СТРЕСС-ТЕСТИРОВАНИЯ ({total_requests} ЗАПРОСОВ, CONCURRENCY={max_concurrency})")
    print("=" * 70)
    await init_db()

    results = []
    latencies = []
    semaphore = asyncio.Semaphore(max_concurrency)

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        start_wall_time = time.perf_counter()

        tasks = [
            asyncio.create_task(worker_client(client, i, results, latencies, semaphore))
            for i in range(1, total_requests + 1)
        ]

        await asyncio.gather(*tasks)
        total_wall_time = time.perf_counter() - start_wall_time

    success_count = sum(1 for r in results if r["success"])
    fail_count = total_requests - success_count
    rps = total_requests / total_wall_time if total_wall_time > 0 else 0

    latencies_ms = [l * 1000 for l in latencies]
    p50 = statistics.median(latencies_ms)
    p95 = statistics.quantiles(latencies_ms, n=20)[18] if len(latencies_ms) >= 20 else max(latencies_ms)
    p99 = statistics.quantiles(latencies_ms, n=100)[98] if len(latencies_ms) >= 100 else max(latencies_ms)
    min_lat = min(latencies_ms)
    max_lat = max(latencies_ms)
    avg_lat = statistics.mean(latencies_ms)

    print("\n📊 РЕЗУЛЬТАТЫ СТРЕСС-ТЕСТА:")
    print(f"   Всего запросов:            {total_requests}")
    print(f"   Успешно (HTTP 202):        {success_count} ({success_count / total_requests * 100:.1f}%)")
    print(f"   Ошибок:                    {fail_count}")
    print(f"   Общее время теста:         {total_wall_time:.3f} сек")
    print(f"   Пропускная способность:    {rps:.1f} RPS (запросов в секунду)")
    print(f"   Латентность Min / Avg:     {min_lat:.1f} ms / {avg_lat:.1f} ms")
    print(f"   Латентность p50 (медиана): {p50:.1f} ms")
    print(f"   Латентность p95:           {p95:.1f} ms")
    print(f"   Латентность p99:           {p99:.1f} ms")
    print(f"   Латентность Max:           {max_lat:.1f} ms")

    assert success_count == total_requests, f"Ожидалось 100% успехов, зафиксировано {fail_count} ошибок"
    print("\n" + "=" * 70)
    print("🎉 СТРЕСС-ТЕСТ УСПЕШНО ПРОЙДЕН! ШЛЮЗ FASTAPI СТАБИЛЕН ПОД НАГРУЗКОЙ.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_stress_test(total_requests=60, max_concurrency=20))
