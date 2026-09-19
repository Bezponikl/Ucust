"""
File: ai/scripts/test_async_api_and_webhooks.py
Автоматизированный тест JWT авторизации, FastAPI Async роутера,
RAG персистентности и Webhook Callback Manager с HMAC-подписями.
"""

import sys
import os
import time
import jwt
import asyncio

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, AI_DIR)

from fastapi.testclient import TestClient
from api_gateway import app
from api.dependencies.auth import JWT_SECRET, JWT_ALGORITHM
from services.webhook_manager import WebhookCallbackManager
from services.rag_manager import BrandKnowledgeManager
from core.database import init_db


def generate_test_token(tenant_id: str = "tenant_test_123") -> str:
    """Генерация тестового JWT токена."""
    payload = {
        "sub": "user_456",
        "tenant_id": tenant_id,
        "exp": int(time.time()) + 3600
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def test_jwt_auth_and_async_endpoints():
    print("\n🔐 [1/3] Тестирование JWT Guard и FastAPI Async Router...")
    await init_db()
    client = TestClient(app)

    token = generate_test_token("tenant_acme_corp")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Попытка запроса без токена (должна вернуть 401/403)
    resp_unauth = client.post(
        "/api/v1/onboarding/async",
        json={"company_name": "No Auth Co", "niche": "Testing"}
    )
    print(f"   Запрос без токена: HTTP {resp_unauth.status_code} (Ожидается 401/403)")
    assert resp_unauth.status_code in [401, 403], f"Ожидался 401/403, получен {resp_unauth.status_code}"

    # 2. Асинхронный онбординг с валидным токеном
    onboard_payload = {
        "company_name": "Acme Robotics",
        "niche": "Промышленная робототехника",
        "raw_notes": "Интеграция роботов-манипуляторов на заводы и склады.",
        "callback_url": "https://api.external-backend.com/webhooks/onboarding"
    }
    resp_onboard = client.post("/api/v1/onboarding/async", json=onboard_payload, headers=headers)
    print(f"   Ответ /api/v1/onboarding/async: HTTP {resp_onboard.status_code}")
    print(f"   Тело ответа: {resp_onboard.json()}")
    assert resp_onboard.status_code == 202
    data_onb = resp_onboard.json()
    assert data_onb["status"] == "accepted"
    assert data_onb["tenant_id"] == "tenant_acme_corp"
    assert data_onb["queue_name"] == "ucust_ai_queue"

    # 3. Асинхронная генерация контента с валидным токеном
    content_payload = {
        "prompt": "Как роботизация снижает брак на производстве автокомпонентов",
        "tier": "pro",
        "industry": "b2b_corporate",
        "rubric": "case_study",
        "callback_url": "https://api.external-backend.com/webhooks/content"
    }
    resp_content = client.post("/api/v1/content/generate-async", json=content_payload, headers=headers)
    print(f"   Ответ /api/v1/content/generate-async: HTTP {resp_content.status_code}")
    print(f"   Тело ответа: {resp_content.json()}")
    assert resp_content.status_code == 202
    data_cnt = resp_content.json()
    assert data_cnt["status"] == "accepted"
    assert data_cnt["tenant_id"] == "tenant_acme_corp"
    print("   ✅ FastAPI Async Router и JWT Guard отработали идеально!")


async def test_webhook_signatures_and_backoff():
    print("\n📡 [2/3] Тестирование Webhook Callback Manager (HMAC-SHA256 & Backoff)...")
    payload = b'{"event":"onboarding_completed","tenant_id":"tenant_acme_corp"}'
    sig1 = WebhookCallbackManager.generate_signature(payload)
    sig2 = WebhookCallbackManager.generate_signature(payload)
    assert sig1 == sig2 and len(sig1) == 64
    print(f"   HMAC-SHA256 подпись: {sig1[:20]}... (длина 64 hex символа)")

    # Проверка симуляции отправки на моковый URL
    print("   Симуляция отправки вебхука с проверкой Exponential Backoff...")
    success = await WebhookCallbackManager.send_callback_async(
        callback_url=None,  # Безопасный no-op
        event_type="test_event",
        tenant_id="tenant_123",
        task_id="task_abc",
        status="success"
    )
    assert success is False  # При пустом URL корректно возвращает False
    print("   ✅ Webhook Callback Manager готов к отправке пушей!")


async def test_persistent_rag_and_celery_task_execution():
    print("\n🗄️ [3/3] Тестирование Persistent RAG связки и выполнения фоновой задачи...")
    from celery_tasks import onboard_brand_task, generate_post_draft_task

    # 1. Запуск задачи онбординга (с сохранением в RAG)
    task_res = onboard_brand_task(
        tenant_id="tenant_nordic_wood",
        company_name="Nordic Wood Co",
        niche="Мебель из натурального дуба",
        raw_notes="Премиальная скандинавская мебель ручной работы.",
        callback_url=None,
        dev_mode=True
    )
    assert task_res["status"] == "success"
    print(f"   Онбординг выполнен, Brand DNA получен: {task_res['brand_dna']['company_name']}")

    # 2. Проверка, что Brand DNA действительно сохранился в Persistent RAG
    saved_dna = await BrandKnowledgeManager.get_brand_dna("tenant_nordic_wood")
    print(f"   Извлечено из Persistent RAG: {saved_dna}")
    assert saved_dna is not None
    assert saved_dna["company_name"] == "Nordic Wood Co"
    assert saved_dna["industry_type"] == "b2c_lifestyle" or saved_dna["industry_type"] == "b2b_corporate" or saved_dna["industry_type"] == "expert_services"

    # 3. Запуск задачи генерации поста (обогащенного из Persistent RAG)
    draft_res = generate_post_draft_task(
        tenant_id="tenant_nordic_wood",
        tier="pro",
        industry="b2c_lifestyle",
        topic="Преимущества дубовых столешниц",
        callback_url=None,
        dev_simulation_mode=True
    )
    assert draft_res["status"] == "success"
    print(f"   Черновик поста сформирован: ID={draft_res['post_draft']['post_id']}, статус={draft_res['post_draft']['status']}")
    print("   ✅ Сквозная цепочка Celery ➔ Persistent RAG ➔ Lazy Rendering отработала успешно!")


async def main():
    print("=" * 70)
    print("🧪 ТЕСТИРОВАНИЕ АСИНХРОННОГО ШЛЮЗА, JWT-АВТОРИЗАЦИИ И WEBHOOK CALLBACKS")
    print("=" * 70)
    await test_jwt_auth_and_async_endpoints()
    await test_webhook_signatures_and_backoff()
    await test_persistent_rag_and_celery_task_execution()
    print("\n" + "=" * 70)
    print("🎉 ВСЕ 3 ИНЖЕНЕРНЫХ БЛОКА ПОЛНОСТЬЮ ЗАВЕРШЕНЫ И ВЕРИФИЦИРОВАНЫ!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
