# File: test_async_queue.py
"""
Тест асинхронной очереди FastAPI Native Queue Manager и механизма Push-коллбеков.
"""

import asyncio
import httpx
import json
import time
from datetime import datetime

from fastapi.testclient import TestClient
from api_gateway import app, queue_manager


def test_async_queue_lifecycle():
    print("=" * 60)
    print("🧪 ТЕСТ АСИНХРОННОЙ ОЧЕРЕДИ FASTAPI NATIVE QUEUE MANAGER")
    print("=" * 60)

    client = TestClient(app)

    # 1. Проверка статистики очереди (должна быть пустой)
    stats_res = client.get("/api/v1/ai/queue/stats")
    assert stats_res.status_code == 200, f"Stats failed: {stats_res.text}"
    stats_data = stats_res.json()
    print(f"📊 1. Статистика очереди: {stats_data}")
    assert stats_data["status"] == "online"

    # 2. Отправка асинхронной задачи генерации
    task_payload = {
        "topic": "Тестовый кофе с латте-артом",
        "company_name": "Test Cafe",
        "niche": "Кофейня",
        "aspect_ratio": "9:16",
        "variation_index": 0,
        "callback_url": "http://127.0.0.1:8080/api/v1/ai/callback"
    }

    print("\n⚡ 2. Отправка асинхронной задачи (POST /api/v1/ai/tasks/async-generate)...")
    t0 = time.time()
    submit_res = client.post("/api/v1/ai/tasks/async-generate", json=task_payload)
    submit_duration = round((time.time() - t0) * 1000, 2)

    assert submit_res.status_code == 202, f"Submit failed: {submit_res.text}"
    submit_data = submit_res.json()
    task_id = submit_data.get("task_id")
    print(f"✅ Задача мгновенно принята за {submit_duration} мс!")
    print(f"   • Task ID: {task_id}")
    print(f"   • Позиция в очереди: {submit_data.get('queue_position')}")
    print(f"   • Расчетное время: {submit_data.get('estimated_wait_seconds')} сек")
    print(f"   • Статус: {submit_data.get('status')}")

    # 3. Проверка статуса задачи (GET /api/v1/ai/tasks/{task_id}/status)
    print(f"\n🔍 3. Проверка статуса задачи '{task_id}'...")
    status_res = client.get(f"/api/v1/ai/tasks/{task_id}/status")
    assert status_res.status_code == 200, f"Status failed: {status_res.text}"
    status_data = status_res.json().get("task", {})
    print(f"   • Текущий статус: {status_data.get('status')}")
    print(f"   • Callback URL: {status_data.get('callback_url')}")
    assert status_data.get("status") in ["QUEUED", "PROCESSING", "COMPLETED"]

    print("\n" + "=" * 60)
    print("🎉 ВСЕ ТЕСТЫ АСИНХРОННОЙ ОЧЕРЕДИ УСПЕШНО ПРОЙДЕНЫ!")
    print("=" * 60)


if __name__ == "__main__":
    test_async_queue_lifecycle()
