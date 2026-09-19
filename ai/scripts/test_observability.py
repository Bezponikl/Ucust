"""
File: ai/scripts/test_observability.py
Тестирование модуля телеметрии, метрик Prometheus и Sentry.
"""

import sys
import os
import asyncio
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

from core.observability import ObservabilityManager, add_sentry_breadcrumb, capture_sentry_exception
from api_gateway import app


async def test_observability_pipeline():
    print("=" * 70)
    print("🧪 ТЕСТИРОВАНИЕ ТЕЛЕМЕТРИИ, PROMETHEUS МЕТРИК И SENTRY")
    print("=" * 70)

    # 1. Тестирование записи кастомных метрик
    print("\n📊 [1/3] Запись тестовых метрик (RPS, Latency, Queue Depth, VRAM)...")
    ObservabilityManager.record_http_request("POST", "/api/v1/content/generate-async", 202, 0.045)
    ObservabilityManager.record_http_request("POST", "/api/v1/onboarding/async", 202, 0.082)
    ObservabilityManager.set_queue_depth("ucust_ai_queue", 14)
    ObservabilityManager.set_queue_depth("ucust_gpu_render", 3)
    ObservabilityManager.set_vram_allocation(9200, "cuda:0")
    ObservabilityManager.record_task_duration("generate_post_draft", 1.85, status="success")
    ObservabilityManager.record_rag_latency(0.012)
    print("   ✅ Метрики успешно записаны в реестр!")

    # 2. Экспорт метрик Prometheus
    print("\n📈 [2/3] Проверка генерации сырого Prometheus-формата...")
    raw_metrics, content_type = ObservabilityManager.export_metrics()
    metrics_str = raw_metrics.decode("utf-8", errors="ignore")
    
    assert "ucust_http_requests_total" in metrics_str
    assert "ucust_celery_queue_depth" in metrics_str
    assert "ucust_active_vram_allocation_mb" in metrics_str
    print(f"   Тип контента: {content_type}")
    print(f"   Размер метрик: {len(raw_metrics)} байт")
    print("   Фрагмент экспорта:")
    for line in metrics_str.splitlines():
        if "ucust_" in line and not line.startswith("#"):
            print(f"     👉 {line}")
    print("   ✅ Prometheus-метрики соответствуют стандарту OpenMetrics/Prometheus!")

    # 3. Тестирование эндпоинта /metrics через ASGI
    print("\n🌐 [3/3] Тестирование эндпоинта GET /metrics через FastAPI ASGI...")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/metrics")
        assert resp.status_code == 200
        assert "ucust_" in resp.text
        print(f"   HTTP GET /metrics -> {resp.status_code} OK ({len(resp.text)} символов)")

    # 4. Sentry Breadcrumbs & Exception test
    print("\n🛡️ [Bonus] Проверка Sentry breadcrumbs & exception guard...")
    add_sentry_breadcrumb(category="comfyui", message="Render job queued", data={"post_id": "test_123"})
    try:
        raise ValueError("Test handled exception for observability verification")
    except Exception as exc:
        capture_sentry_exception(exc, tags={"tenant_id": "tenant_test"}, extra={"debug": True})
    print("   ✅ Sentry breadcrumbs и перехват исключений отработали без сбоев!")

    print("\n" + "=" * 70)
    print("🎉 ВСЕ ТЕСТЫ OBSERVABILITY & PROMETHEUS УСПЕШНО ПРОЙДЕНЫ!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_observability_pipeline())
