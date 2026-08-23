import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add ai directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bridge.api_controller import app

client = TestClient(app)

def test_unified_ai_task_post():
    payload = {
        "user_id": "usr_test_123",
        "session_id": "sess_test_abc",
        "task_type": "generate_post",
        "payload": {
            "city": "Казань",
            "company_name": "Бодрый День",
            "niche": "Рестораны и Кофейни",
            "prompt": "Анонс сезонного меню"
        }
    }
    response = client.post("/api/v1/ai/task", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "post_text" in data["data"]
    assert "Бодрый День" in data["data"]["post_text"]
    assert data["data"]["confidence_score"] >= 0.9

def test_ai_trends():
    response = client.get("/api/v1/ai/trends?niche=SMM")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["trends"]) > 0

def test_ai_analytics_graphs():
    response = client.get("/api/v1/ai/analytics/graphs")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "reach" in data
    assert "engagement" in data

def test_websocket_session():
    with client.websocket_connect("/ws/ai/session/test-sess-1") as websocket:
        init_data = websocket.receive_json()
        assert init_data["step"] == "connected"
        
        # Send prompt
        websocket.send_text('{"prompt": "Новое меню", "company_name": "Кофеман"}')
        
        # Step 1: interviewer
        step1 = websocket.receive_json()
        assert step1["step"] == "interviewer"
        
        # Step 2: analyst
        step2 = websocket.receive_json()
        assert step2["step"] == "analyst"
        
        # Step 3: copywriter
        step3 = websocket.receive_json()
        assert step3["step"] == "copywriter"
        
        # Step 4: completed
        step4 = websocket.receive_json()
        assert step4["step"] == "completed"
        assert "post_text" in step4["result"]
