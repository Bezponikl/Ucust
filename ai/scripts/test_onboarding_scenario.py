"""
File: ai/scripts/test_onboarding_scenario.py
Комплексный интеграционный тест 5-экранного сценария регистрации проекта (Onboarding)
через UnifiedOrchestrator (/api/v1/task/execute) с аутентификацией X-Internal-Secret.
"""

import sys
import os
import asyncio
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


def test_onboarding_end_to_end():
    print("=" * 70)
    print("🚀 ТЕСТИРОВАНИЕ 5-ЭКРАННОГО ОНБОРДИНГА ПРОЕКТА (UCUST AI)")
    print("=" * 70)

    # -------------------------------------------------------------
    # ШАГ 1: Запрос на первичный анализ бренда (task_type: "analyze_brand")
    # -------------------------------------------------------------
    print("\n[ШАГ 1] Вызов UnifiedOrchestrator: analyze_brand...", flush=True)
    project_id = "test_cafe_specialty_2026"
    request_body = {
        "task_type": "analyze_brand",
        "user_id": "usr_owner_42",
        "project_id": project_id,
        "sync_backend": False,
        "payload": {
            "source_url": "https://t.me/kofeina_aromat",
            "niche_hint": "Кофейня спешелти и крафтовая пекарня",
            "city": "Санкт-Петербург",
            "country": "Россия"
        }
    }

    resp = client.post("/api/v1/task/execute", json=request_body, headers=HEADERS)
    print(f"HTTP Status: {resp.status_code}", flush=True)
    assert resp.status_code == 200, f"Ошибка вызова: {resp.text}"

    data = resp.json()
    assert data["status"] == "success", f"Статус задачи не success: {data}"
    task_res = data.get("data", {})
    assert "project_profile_draft" in task_res or "project_profile_draft" in data, f"Отсутствует project_profile_draft в ответе: {data}"

    draft = task_res.get("project_profile_draft") or data.get("project_profile_draft")
    print("\n[ШАГ 2] Валидация структуры 5 экранов UI:", flush=True)
    
    # Экран 1: О проекте (about)
    assert "about" in draft, "Экран 1 (about) отсутствует"
    assert "name" in draft["about"]
    assert "niche" in draft["about"]
    assert "positioning" in draft["about"]
    print(f"  ✅ Экран 1 (about): Название='{draft['about']['name']}', Ниша='{draft['about']['niche']}'", flush=True)

    # Экран 2: Рынок (market)
    assert "market" in draft, "Экран 2 (market) отсутствует"
    assert "competitors" in draft["market"]
    assert "geography" in draft["market"]
    assert "audience_segment" in draft["market"]
    print(f"  ✅ Экран 2 (market): Конкурентов={len(draft['market']['competitors'])}, ЦА='{draft['market']['audience_segment'][:50]}...'", flush=True)

    # Экран 3: SWOT анализ (swot)
    assert "swot" in draft, "Экран 3 (swot) отсутствует"
    assert "strengths" in draft["swot"]
    assert "weaknesses" in draft["swot"]
    assert "opportunities" in draft["swot"]
    assert "threats" in draft["swot"]
    print(f"  ✅ Экран 3 (swot): Сильные={len(draft['swot']['strengths'])}, Возможности={len(draft['swot']['opportunities'])}", flush=True)

    # Экран 4: Услуги (services)
    assert "services" in draft, "Экран 4 (services) отсутствует"
    assert isinstance(draft["services"], list)
    print(f"  ✅ Экран 4 (services): Найдено услуг={len(draft['services'])}", flush=True)

    # Экран 5: Цели и ToV (goals)
    assert "goals" in draft, "Экран 5 (goals) отсутствует"
    assert "content_goals" in draft["goals"]
    assert "tone_of_voice" in draft["goals"]
    print(f"  ✅ Экран 5 (goals): Целей={len(draft['goals']['content_goals'])}, ToV={draft['goals']['tone_of_voice']}", flush=True)

    # -------------------------------------------------------------
    # ШАГ 3: Симуляция редактирования пользователем 5 экранов на фронтенде
    # -------------------------------------------------------------
    print("\n[ШАГ 3] Симуляция правок пользователя перед финальным сохранением...", flush=True)
    edited_profile = dict(draft)
    edited_profile["about"]["name"] = "Кофейня Аромат Зерен (СПб)"
    edited_profile["services"].append({
        "name": "Фирменный авторский латте Хвоя-Брусника",
        "description": "Эспрессо на зерне Эфиопия с сиропом из сосновых почек и брусничной пудрой",
        "price": "390 руб."
    })

    # -------------------------------------------------------------
    # ШАГ 4: Финальное индексирование в RAG (task_type: "rag_ingest")
    # -------------------------------------------------------------
    print("\n[ШАГ 4] Сохранение проекта и индексация в RAG: task_type='rag_ingest'...", flush=True)
    ingest_request = {
        "task_type": "rag_ingest",
        "user_id": "usr_owner_42",
        "project_id": project_id,
        "sync_backend": False,
        "payload": {
            "project_id": project_id,
            "data": edited_profile
        }
    }

    ingest_resp = client.post("/api/v1/task/execute", json=ingest_request, headers=HEADERS)
    print(f"HTTP Status: {ingest_resp.status_code}", flush=True)
    assert ingest_resp.status_code == 200, f"Ошибка индексации: {ingest_resp.text}"

    ingest_data = ingest_resp.json()
    assert ingest_data["status"] == "success"
    ingest_res = ingest_data.get("data", {})
    chunks_count = ingest_res.get("chunks_indexed", 0) or ingest_data.get("chunks_indexed", 0)
    assert chunks_count > 0, f"Чанки не проиндексированы: {ingest_data}"
    print(f"  ✅ Успешно проиндексировано {chunks_count} семантических чанков под tenant_id='{project_id}'", flush=True)

    # -------------------------------------------------------------
    # ШАГ 5: Проверка поиска по базе знаний (task_type: "rag_query")
    # -------------------------------------------------------------
    print("\n[ШАГ 5] Проверка поиска RAG по новому проекту: task_type='rag_query'...", flush=True)
    query_request = {
        "task_type": "rag_query",
        "user_id": "usr_owner_42",
        "project_id": project_id,
        "sync_backend": False,
        "payload": {
            "brand_id": project_id,
            "query": "Какой у нас авторский латте и его цена?",
            "top_k": 3
        }
    }

    query_resp = client.post("/api/v1/task/execute", json=query_request, headers=HEADERS)
    print(f"HTTP Status: {query_resp.status_code}", flush=True)
    assert query_resp.status_code == 200, f"Ошибка RAG Query: {query_resp.text}"

    query_data = query_resp.json()
    assert query_data["status"] == "success"
    query_res = query_data.get("data", {})
    print(f"  ✅ RAG вернул контекст. Скор: {query_res.get('top_score') or query_data.get('top_score')}", flush=True)

    print("\n" + "=" * 70)
    print("🎉 ВСЕ ШАГИ 5-ЭКРАННОГО ОНБОРДИНГА ПРОЙДЕНЫ НА 100% УСПЕШНО!")
    print("=" * 70)


if __name__ == "__main__":
    test_onboarding_end_to_end()
