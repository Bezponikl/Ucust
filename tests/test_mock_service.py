"""
Comprehensive Integration Test Suite for UCust AI Mock Server.
Verifies all 37 endpoints, auth, orchestrator single entry point, collectors, and async queue.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ai_mock.mock_server import app

client = TestClient(app)
SECRET_HEADER = {"X-Internal-Secret": "ucust-super-secret-service-token-2026"}


def test_health_checks():
    r1 = client.get("/health")
    assert r1.status_code == 200
    assert r1.json()["status"] == "healthy"

    r2 = client.get("/api/v1/ai/health")
    assert r2.status_code == 200
    assert r2.json()["status"] == "healthy"

    r3 = client.get("/")
    assert r3.status_code == 200


def test_auth_rejection():
    # Test forbidden secret
    bad_headers = {"X-Internal-Secret": "wrong-token"}
    resp = client.post(
        "/api/v1/task/execute",
        json={"task_type": "generate_post", "payload": {"topic": "test"}},
        headers=bad_headers
    )
    assert resp.status_code == 403


def test_orchestrator_single_entry_point():
    # 1. generate_post
    resp = client.post(
        "/api/v1/task/execute",
        json={
            "task_type": "generate_post",
            "user_id": "usr_test1",
            "payload": {
                "topic": "Анонс нового меню",
                "company_name": "Coffee Craft",
                "niche": "Кофейня",
                "rubric": "PRODUCT"
            }
        },
        headers=SECRET_HEADER
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "post_text" in data["data"]
    assert "image_url" in data["data"]
    assert data["data"]["critic_score"] >= 9.0

    # 2. parse_telegram
    resp_tg = client.post(
        "/api/v1/task/execute",
        json={
            "task_type": "parse_telegram",
            "payload": {"channel": "@loft_coffee_spb", "limit": 5}
        },
        headers=SECRET_HEADER
    )
    assert resp_tg.status_code == 200
    assert resp_tg.json()["data"]["source_type"] == "telegram"


def test_direct_generation_with_project_context():
    resp = client.post(
        "/orchestration/generate",
        json={
            "prompt": "Акция на раф 20%",
            "rubric": "PROMO",
            "promoCode": "RAF20",
            "projectContext": {
                "companyName": "Specialty Coffee Roasters",
                "niche": "Кофейня",
                "city": "Москва",
                "toneOfVoice": "FRIENDLY",
                "visualDna": {"brandColors": ["#4A2E18", "#E8D8C8"]}
            }
        },
        headers=SECRET_HEADER
    )
    assert resp.status_code == 200
    res = resp.json()
    assert res["status"] == "success"
    assert "post_text" in res
    assert "image_url" in res


def test_all_collectors():
    # 1. Universal Hub
    r_hub = client.post(
        "/api/v1/ai/parse",
        json={"target": "https://t.me/loft_coffee_spb", "source_type": "auto"},
        headers=SECRET_HEADER
    )
    assert r_hub.status_code == 200
    assert r_hub.json()["status"] == "success"

    # 2. Telegram Dedicated
    r_tg = client.post(
        "/api/v1/ai/telegram/analyze",
        json={"channel": "@UcustAi", "limit": 3},
        headers=SECRET_HEADER
    )
    assert r_tg.status_code == 200

    # 3. VK Dedicated
    r_vk = client.post(
        "/api/v1/ai/vk/analyze",
        json={"group_id": "ucust_ai", "limit": 5},
        headers=SECRET_HEADER
    )
    assert r_vk.status_code == 200

    # 4. Geo Maps (2GIS)
    r_geo = client.post(
        "/api/v1/ai/geo/analyze",
        json={"url": "https://2gis.ru/moscow/firm/12345"},
        headers=SECRET_HEADER
    )
    assert r_geo.status_code == 200
    assert "rating" in r_geo.json()

    # 5. Website Deep Analyzer
    r_web = client.post(
        "/api/v1/ai/website/analyze",
        json={"url": "https://ucust.ai"},
        headers=SECRET_HEADER
    )
    assert r_web.status_code == 200
    assert "detected_palette" in r_web.json()

    # 6. Competitor Analyzer
    r_comp = client.post(
        "/api/v1/ai/competitor/analyze",
        json={"url": "https://competitor.com", "niche": "IT"},
        headers=SECRET_HEADER
    )
    assert r_comp.status_code == 200
    assert "swot_matrix" in r_comp.json()

    # 7. Document Analyzer
    r_doc = client.post(
        "/api/v1/ai/documents/analyze",
        json={"target": "price_list.pdf"},
        headers=SECRET_HEADER
    )
    assert r_doc.status_code == 200

    # 8. Quick Vision
    r_vis = client.post(
        "/api/v1/vision/quick-analyze",
        json={"image": "base64mock"},
        headers=SECRET_HEADER
    )
    assert r_vis.status_code == 200


def test_marketing_skills():
    # 1. Image Gen
    r_img = client.post(
        "/api/v1/ai/generate-image",
        json={"prompt": "Кофе и круассан", "aspect_ratio": "1:1"},
        headers=SECRET_HEADER
    )
    assert r_img.status_code == 200
    assert "image_url" in r_img.json()

    # 2. Strategy
    r_strat = client.post(
        "/api/v1/ai/strategy/generate",
        json={"company_name": "UCust", "niche": "SMM Автоматизация"},
        headers=SECRET_HEADER
    )
    assert r_strat.status_code == 200
    assert "funnel" in r_strat.json()

    # 3. Critic Review
    r_crit = client.post(
        "/api/v1/ai/critic/review",
        json={"text": "Лучшие цены в городе, покупайте только у нас!"},
        headers=SECRET_HEADER
    )
    assert r_crit.status_code == 200
    assert r_crit.json()["score"] >= 9.0

    # 4. Trends
    r_trends = client.get("/api/v1/ai/trends?niche=Бизнес")
    assert r_trends.status_code == 200
    assert len(r_trends.json()["trends"]) > 0


def test_async_queue():
    # Enqueue
    r_post = client.post(
        "/api/v1/ai/tasks/async-generate",
        json={"topic": "Тренды маркетинга 2026", "company_name": "UCust"},
        headers=SECRET_HEADER
    )
    assert r_post.status_code == 202
    task_id = r_post.json()["task_id"]

    # Poll status
    r_status = client.get(f"/api/v1/ai/tasks/{task_id}/status")
    assert r_status.status_code == 200
    assert r_status.json()["status"] in ["QUEUED", "PROCESSING", "COMPLETED"]


def test_rag_knowledge_base():
    # Ingest
    r_ingest = client.post(
        "/api/v1/ai/rag/ingest",
        json={"documents": [{"id": "kb_doc_1", "text": "Условия гарантии 2026"}]}
    )
    assert r_ingest.status_code == 200
    assert r_ingest.json()["status"] == "success"

    # Query
    r_q = client.post(
        "/api/v1/ai/rag/query",
        json={"query": "Каковы условия гарантии?"}
    )
def test_publish_and_broadcast():
    # 1. Achievement broadcast
    r_broad = client.post(
        "/api/v1/ai/broadcast/achievement",
        json={"title": "Релиз 2.5.0", "description": "Запуск мок-сервера", "channel": "@UcustAi"},
        headers=SECRET_HEADER
    )
    assert r_broad.status_code == 200
    assert r_broad.json()["status"] == "success"

    # 2. Publish
    r_pub = client.post(
        "/api/v1/ai/publish",
        json={"platforms": ["telegram", "vk"], "post_text": "Привет мир!"},
        headers=SECRET_HEADER
    )
    assert r_pub.status_code == 200
    assert r_pub.json()["published"] is True


def test_websocket_stream():
    with client.websocket_connect("/ws/ai/session/test_sess_123") as ws:
        msg = ws.receive_json()
        assert msg["session_id"] == "test_sess_123"
        assert "step" in msg
def test_tariffs_and_quotas():
    # 1. Get tariffs
    r_tariffs = client.get("/api/v1/ai/tariffs")
    assert r_tariffs.status_code == 200
    tariffs = r_tariffs.json()["tariffs"]
    assert "START" in tariffs
    assert "BUSINESS" in tariffs
    assert "ENTERPRISE" in tariffs
    assert tariffs["BUSINESS"]["monthly_post_limit"] == 20

    # 2. Get client quota
    r_quota = client.get("/api/v1/ai/clients/client_dentallux_101/subscription-quota?tier=BUSINESS")
    assert r_quota.status_code == 200
    q = r_quota.json()
    assert q["monthly_post_limit"] == 20
    assert len(q["calendar_slots"]) == 20


if __name__ == "__main__":
    pytest.main(["-v", __file__])
