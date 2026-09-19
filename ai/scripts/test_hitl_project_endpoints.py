"""
File: ai/scripts/test_hitl_project_endpoints.py
Интеграционный тест прямых REST-эндпоинтов Human-in-the-Loop регистрации проекта:
- Phase 1: POST /api/v1/projects/analyze
- Phase 2: POST /api/v1/projects/{project_id}/knowledge
"""

import sys
import os
from fastapi.testclient import TestClient

# Добавляем корневой путь ai в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api_gateway import app

client = TestClient(app)
INTERNAL_SECRET = "ucust-super-secret-service-token-2026"
HEADERS = {
    "X-Internal-Secret": INTERNAL_SECRET,
    "Content-Type": "application/json"
}


def test_hitl_project_lifecycle():
    print("=" * 70, flush=True)
    print("🚀 ТЕСТИРОВАНИЕ HITL ЭНДПОИНТОВ ОНБОРДИНГА ПРОЕКТА (2 ФАЗЫ)", flush=True)
    print("=" * 70, flush=True)

    # -------------------------------------------------------------
    # ФАЗА 1: Анализ и предзаполнение черновика (POST /api/v1/projects/analyze)
    # -------------------------------------------------------------
    print("\n[ФАЗА 1] Вызов POST /api/v1/projects/analyze...", flush=True)
    analyze_payload = {
        "source_url": "https://t.me/kofeina_aromat",
        "niche_hint": "Кофейня спешелти",
        "city": "Санкт-Петербург"
    }

    resp1 = client.post("/api/v1/projects/analyze", json=analyze_payload, headers=HEADERS)
    print(f"HTTP Status Phase 1: {resp1.status_code}", flush=True)
    assert resp1.status_code == 200, f"Ошибка фазы 1: {resp1.text}"

    data1 = resp1.json()
    assert data1["status"] == "success"
    assert "project_profile_draft" in data1
    draft = data1["project_profile_draft"]

    # Проверка структуры 5 экранов
    assert "about" in draft and "name" in draft["about"]
    assert "market" in draft and "competitors" in draft["market"]
    assert "swot" in draft and "strengths" in draft["swot"]
    assert "services" in draft and isinstance(draft["services"], list)
    assert "goals" in draft and "content_goals" in draft["goals"]
    print(f"  ✅ Фаза 1 успешна! Получен черновик для '{draft['about']['name']}' ({draft['about']['niche']})", flush=True)

    # -------------------------------------------------------------
    # Симуляция правок человека на 5 экранах
    # -------------------------------------------------------------
    print("\n[SMM EDIT] Человек редактирует данные на экранах в UI...", flush=True)
    edited_draft = dict(draft)
    edited_draft["about"]["name"] = "Specialty Coffee Lab"
    edited_draft["services"].append({
        "name": "Авторский фильтр-кофе Колумбия Кастильо",
        "description": "Анаэробная ферментация 72 часа, ноты манго и карамели",
        "price": "320 руб."
    })

    # -------------------------------------------------------------
    # ФАЗА 2: Утверждение и сохранение в pgvector (POST /api/v1/projects/{project_id}/knowledge)
    # -------------------------------------------------------------
    project_id = "proj_specialty_lab_spb"
    print(f"\n[ФАЗА 2] Вызов POST /api/v1/projects/{project_id}/knowledge...", flush=True)
    commit_payload = {
        "data": edited_draft
    }

    resp2 = client.post(f"/api/v1/projects/{project_id}/knowledge", json=commit_payload, headers=HEADERS)
    print(f"HTTP Status Phase 2: {resp2.status_code}", flush=True)
    assert resp2.status_code == 200, f"Ошибка фазы 2: {resp2.text}"

    data2 = resp2.json()
    assert data2["status"] == "success"
    assert data2["project_id"] == project_id
    assert data2["chunks_indexed"] > 0
    print(f"  ✅ Фаза 2 успешна! Векторизовано {data2['chunks_indexed']} чанков для project_id='{project_id}'", flush=True)

    print("\n" + "=" * 70, flush=True)
    print("🎉 ДВУХФАЗНЫЙ СЦЕНАРИЙ ОНБОРДИНГА ПРОЕКТА ПОЛНОСТЬЮ РАБОТОСПОСОБЕН!", flush=True)
    print("=" * 70, flush=True)


if __name__ == "__main__":
    test_hitl_project_lifecycle()
