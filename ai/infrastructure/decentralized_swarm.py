import os
import time
import threading
from typing import Any, Dict

# Force Postgres
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@127.0.0.1:5432/ai_smm"
os.environ["SYNRIX_BACKEND"] = "postgres"

from synrix_runtime.api.runtime import AgentRuntime
from synrix.agent_backend import SynrixAgentBackend

def get_backend():
    db_url = os.environ.get("DATABASE_URL", "")
    return SynrixAgentBackend(backend="postgres", dsn=db_url, tenant_id="dev")

def make_agent(agent_id: str) -> AgentRuntime:
    return AgentRuntime(
        agent_id=agent_id,
        agent_type="worker",
        backend_override=get_backend(),
        require_account=False
    )

def orchestrator_loop(stop_event: threading.Event):
    agent = make_agent("orchestrator")
    print("[Orchestrator] Запускаю децентрализованный процесс! Рассылаю бриф (brief_ready).")
    
    # Broadcast the brief
    agent.broadcast(
        message={"product": "UCust AI SMM", "audience": "B2B Tech"}, 
        message_type="brief_ready"
    )
    
    # Listen for final completion
    while not stop_event.is_set():
        broadcasts = agent.read_broadcasts(since_seconds=10)
        for b in broadcasts:
            msg_type = b.get("message_type")
            if msg_type == "content_ready":
                print("[Orchestrator]  Получен сигнал content_ready от Visual_Director! Пайплайн завершен!")
                stop_event.set()
                return
        time.sleep(1)

def analyst_loop(stop_event: threading.Event):
    agent = make_agent("Agent_Analyst")
    processed_briefs = set()
    
    while not stop_event.is_set():
        broadcasts = agent.read_broadcasts(since_seconds=10)
        for b in broadcasts:
            msg_id = b.get("id", str(b.get("timestamp")))
            if b.get("message_type") == "brief_ready" and msg_id not in processed_briefs:
                processed_briefs.add(msg_id)
                data = b.get("message", {})
                print(f"[Analyst]  Получил бриф на продукт '{data.get('product')}'. Делаю SWOT-анализ...")
                time.sleep(2) # Имитация работы
                
                strategy = f"Стратегия продвижения {data.get('product')}: упор на инновации."
                agent.broadcast(
                    message={"strategy": strategy},
                    message_type="swot_ready"
                )
                print("[Analyst]  SWOT готов. Разослал (swot_ready).")
        time.sleep(1)

def copywriter_loop(stop_event: threading.Event):
    agent = make_agent("Agent_Copywriter")
    processed_swots = set()
    attempt = 1
    
    while not stop_event.is_set():
        # 1. Сначала проверяем личные сообщения (критика от Фактчекера)
        messages = agent.read_messages(unread_only=True)
        for m in messages:
            if m.get("message_type") == "factcheck_failed":
                print(f"[Copywriter]  Получил критику от Фактчекера: {m.get('message')}. Переписываю текст! (Попытка {attempt+1})")
                time.sleep(2)
                attempt += 1
                new_draft = "UCust AI  надежное решение для автоматизации SMM." # Исправленный текст (без 100%)
                agent.broadcast(
                    message={"draft": new_draft, "attempt": attempt},
                    message_type="draft_ready"
                )
                print("[Copywriter]  Отправил исправленный черновик (draft_ready).")
                
                # Mark as read
                if "id" in m:
                    try:
                        agent.mark_read(m["id"])
                    except Exception:
                        pass
        
        # 2. Проверяем общие броадкасты (новые стратегии от Аналитика)
        broadcasts = agent.read_broadcasts(since_seconds=10)
        for b in broadcasts:
            msg_id = b.get("id", str(b.get("timestamp")))
            if b.get("message_type") == "swot_ready" and msg_id not in processed_swots:
                processed_swots.add(msg_id)
                print("[Copywriter]  Получил SWOT. Пишу первый черновик...")
                time.sleep(2)
                
                # Специально делаем "ошибку" (100% гарантия) для проверки взаимодействия агентов
                bad_draft = "UCust AI дает 100% гарантию роста конверсии! Покупайте!"
                agent.broadcast(
                    message={"draft": bad_draft, "attempt": attempt},
                    message_type="draft_ready"
                )
                print("[Copywriter]  Отправил первый черновик с ошибкой (draft_ready).")
                
        time.sleep(1)

def factchecker_loop(stop_event: threading.Event):
    agent = make_agent("Agent_FactChecker")
    processed_drafts = set()
    
    while not stop_event.is_set():
        broadcasts = agent.read_broadcasts(since_seconds=10)
        for b in broadcasts:
            msg_id = str(b.get("timestamp")) + b.get("message_type", "")
            if b.get("message_type") == "draft_ready" and msg_id not in processed_drafts:
                processed_drafts.add(msg_id)
                draft = b.get("message", {}).get("draft", "")
                attempt = b.get("message", {}).get("attempt", 1)
                
                print(f"[FactChecker]  Проверяю черновик: '{draft}'")
                time.sleep(1)
                
                if "100%" in draft:
                    print(f"[FactChecker]  НАЙДЕНА ОШИБКА! Незаконная гарантия '100%'. Отправляю Copywriter на доработку.")
                    # ПРЯМОЕ сообщение агенту-копирайтеру!
                    agent.send_message(
                        to_agent="Agent_Copywriter",
                        message={"error": "Убери ложную гарантию про 100%, это незаконно."},
                        message_type="factcheck_failed"
                    )
                else:
                    print(f"[FactChecker]  Ошибок нет. Текст чист. Одобряю (factcheck_passed).")
                    agent.broadcast(
                        message={"verified_draft": draft},
                        message_type="factcheck_passed"
                    )
        time.sleep(1)

def visual_director_loop(stop_event: threading.Event):
    agent = make_agent("Agent_Visual_Director")
    processed_texts = set()
    
    while not stop_event.is_set():
        broadcasts = agent.read_broadcasts(since_seconds=10)
        for b in broadcasts:
            msg_id = b.get("id", str(b.get("timestamp")))
            if b.get("message_type") == "factcheck_passed" and msg_id not in processed_texts:
                processed_texts.add(msg_id)
                text = b.get("message", {}).get("verified_draft", "")
                
                print(f"[Visual_Director]  Фактчекинг пройден. Генерирую видео-креативы для текста: '{text}'...")
                time.sleep(3) # "Долгая" работа
                print("[Visual_Director]  Видео готово! Разослал (content_ready).")
                
                agent.broadcast(
                    message={"video_url": "mock_video_001.mp4"},
                    message_type="content_ready"
                )
        time.sleep(1)

def main():
    print("=" * 70)
    print(" Запуск Децентрализованного Роя Агентов (Decentralized Swarm)")
    print("Агенты общаются друг с другом через Octopoda Messaging Bus!")
    print("=" * 70)
    
    stop_event = threading.Event()
    threads = []
    
    funcs = [
        analyst_loop, 
        copywriter_loop, 
        factchecker_loop, 
        visual_director_loop,
        orchestrator_loop # Оркестратор запускается последним, чтобы все уже слушали
    ]
    
    for f in funcs:
        t = threading.Thread(target=f, args=(stop_event,), daemon=True)
        t.start()
        threads.append(t)
        
    try:
        # Ждем пока Оркестратор не выставит stop_event (когда получит content_ready)
        while not stop_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nОстановка...")
        stop_event.set()
        
    print("=" * 70)
    print(" Все агенты завершили работу и остановились.")
    
if __name__ == "__main__":
    main()
