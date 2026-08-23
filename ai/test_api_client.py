"""
Тест интеграции Бэкенд <-> Шлюз Агентов (FastAPI TestClient + WebSocket).
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import json
from fastapi.testclient import TestClient
from api_gateway import app

client = TestClient(app)

def test_full_gateway_integration():
    print("===================================================================")
    print("🌐 ТЕСТ ИНТЕГРАЦИИ: FRONTEND / BACKEND <-> AI SERVICE GATEWAY")
    print("===================================================================\n")
    
    # 1. Health Check
    print("--- 1. HEALTH CHECK ---")
    resp = client.get("/api/v1/ai/health")
    print("Статус код:", resp.status_code)
    print("Ответ сервера:", resp.json())
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
    
    # 2. Выполнение задачи копирайтера (REST API)
    print("\n--- 2. ВЫПОЛНЕНИЕ ЗАДАЧИ ЧЕРЕЗ REST (POST /api/v1/ai/task) ---")
    task_payload = {
        "user_id": "client_b2b_01",
        "session_id": "test_sess_01",
        "task_type": "prepare_holiday_greeting",
        "payload": {
            "company_name": "Кофейня 'Бодрый День'",
            "niche": "Рестораны и Кофейни",
            "city": "Казань",
            "country": "Россия"
        }
    }
    resp = client.post("/api/v1/ai/task", json=task_payload)
    print("Статус код:", resp.status_code)
    data = resp.json()
    print("Статус ответа:", data["status"])
    print("Текст поздравления:\n", data["data"]["prepared_greeting"]["post_text"])
    assert resp.status_code == 200
    assert data["status"] == "success"
    
    # 3. Мгновенная отдача трендов недели (Redis кэш)
    print("\n--- 3. ПОЛУЧЕНИЕ ТРЕНДОВ НЕДЕЛИ (GET /api/v1/ai/trends) ---")
    resp = client.get("/api/v1/ai/trends?niche=Рестораны и Кофейни")
    print("Статус код:", resp.status_code)
    print("Тренды:", resp.json()["trends"])
    assert resp.status_code == 200

    # 4. Безопасные графики для фронтенда (GET /api/v1/ai/analytics/graphs)
    print("\n--- 4. БЕЗОПАСНЫЕ ДАННЫЕ ДЛЯ ГРАФИКОВ ФРОНТЕНДА ---")
    resp = client.get("/api/v1/ai/analytics/graphs")
    print("Графы (без PII):", resp.json()["data"])
    assert resp.status_code == 200

    # 5. Clean RAG Query
    print("\n--- 5. CLEAN RAG QUERY (POST /api/v1/ai/rag/query) ---")
    rag_payload = {"query": "Сколько стоит тариф Pro?", "top_k": 3}
    resp = client.post("/api/v1/ai/rag/query", json=rag_payload)
    print("RAG результат:", resp.json())
    assert resp.status_code == 200

    # 6. Живой WebSocket стриминг онбординга для Фронтенда
    print("\n--- 6. WEBSOCKET REAL-TIME ОНБОРДИНГ (WS /ws/ai/session/...) ---")
    with client.websocket_connect("/ws/ai/session/front_session_99") as ws:
        # Приветствие от Интервьюера
        greeting_event = json.loads(ws.receive_text())
        print(f"📥 [WS Событие 1]: Step='{greeting_event['step']}' | Message='{greeting_event['payload']['message']}'")
        assert greeting_event["step"] == "interviewer_greeting"
        
        # Фронтенд отправляет заполненную форму онбординга
        user_form_msg = {
            "company_name": "UCust AI Platform",
            "niche": "IT и Автоматизация",
            "raw_social_input": "@ucust_ai https://vk.com/ucust",
            "goals": "Автоматизировать постинг в соцсети",
            "pain_points": "Рутина при генерации постов"
        }
        print("📤 [WS Отправка формы от фронтенда] -> Шлюз...")
        ws.send_text(json.dumps(user_form_msg))
        
        # Получаем стриминг шагов
        step2 = json.loads(ws.receive_text())
        print(f"📥 [WS Событие 2]: Step='{step2['step']}' | Status='{step2['payload'].get('status')}'")
        
        step3 = json.loads(ws.receive_text())
        print(f"📥 [WS Событие 3]: Step='{step3['step']}' | Progress={step3['payload'].get('progress')}% | Status='{step3['payload'].get('status')}'")
        
        step4 = json.loads(ws.receive_text())
        print(f"📥 [WS Событие 4]: Step='{step4['step']}' | Progress={step4['payload'].get('progress')}% | Status='{step4['payload'].get('status')}'")

        step5 = json.loads(ws.receive_text())
        print(f"📥 [WS Финал]: Step='{step5['step']}' | Progress={step5['payload'].get('progress')}% | Result={step5['payload']['result']['status']}")
        assert step5["step"] == "pipeline_completed"

    print("\n===================================================================")
    print("🎉 ВСЕ ТЕСТЫ ИНТЕГРАЦИИ (REST + WEBSOCKETS) УСПЕШНО ПРОЙДЕНЫ!")
    print("===================================================================")

if __name__ == "__main__":
    test_full_gateway_integration()
