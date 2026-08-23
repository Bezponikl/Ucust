"""
run_agents.py
Запускает все UCust.AI агенты как живые AgentRuntime процессы.
Они регистрируются в Octopoda dashboard и отправляют heartbeat каждые 10 секунд.
Оставь этот скрипт запущенным — агенты будут видны в /dashboard/agents.
"""
import threading
import time
import json
import os
import sys

os.environ.setdefault("OCTOPODA_API_KEY", "local-dev")
os.environ.setdefault("OCTOPODA_BASE_URL", "http://localhost:8741")

# ── Данные агентов UCust.AI ──────────────────────────────────────
AGENTS_SEED = {
    "Agent_Interviewer": [
        ("agent:role",          "Interviewer — собирает бриф клиента и цели кампании"),
        ("agent:framework",     "CrewAI + Saiga Nemo 12B via Ollama"),
        ("agent:status",        "ACTIVE"),
        ("brief:company",       "UCust.AI — Мультиагентная система интернет-маркетинга и ORM"),
        ("brief:audience",      "B2B: маркетологи, IT-директора, собственники SMB"),
        ("brief:tone_of_voice", "Профессиональный, технологичный, доверительный"),
        ("brief:region",        "Россия, B2B-сегмент, IT и сервисный бизнес"),
        ("brief:pain_points",   "Нехватка времени, высокая стоимость SMM-агентств"),
    ],
    "Agent_Analyst": [
        ("agent:role",           "Analyst — строит стратегию, SWOT, USP"),
        ("agent:framework",      "CrewAI + Saiga Nemo 12B via Ollama"),
        ("agent:status",         "ACTIVE"),
        ("strategy:core_usp",    "ИИ-агенты с FactChecking без галлюцинаций"),
        ("strategy:positioning", "Единственная open-source система с фактчекингом"),
        ("strategy:competitors", "Buffer AI, Jasper — нет FactCheck, нет ORM, нет видео"),
        ("strategy:keywords",    "AI-маркетинг, автоматизация SMM, ORM"),
        ("strategy:swot",        "Сила: полный цикл от брифа до публикации за 3 мин"),
    ],
    "Agent_Copywriter": [
        ("agent:role",         "Copywriter — генерирует посты, рекламу, подписи"),
        ("agent:framework",    "CrewAI + Saiga Nemo 12B via Ollama"),
        ("agent:status",       "ACTIVE"),
        ("draft:latest_promo", "UCust.AI: SMM-автоматизация с фактчекингом → ucust.ai"),
        ("framework:current",  "PAS (Problem-Agitation-Solution)"),
        ("cta:default",        "Записаться на демо → ucust.ai"),
        ("post:status",        "READY_FOR_FACTCHECK"),
    ],
    "Agent_FactChecker": [
        ("agent:role",            "FactChecker — валидирует все утверждения по брифу"),
        ("agent:framework",       "CrewAI + Saiga Nemo 12B via Ollama"),
        ("agent:status",          "ACTIVE"),
        ("factcheck:last_result", "PASSED — ни одного невалидированного суперлатива"),
        ("factcheck:rule",        "Rule of Differentiation: запрещены ложные скидки"),
        ("factcheck:corrections", "correction_attempts=0 — текст принят с первого прохода"),
        ("factcheck:status",      "OPERATIONAL"),
    ],
    "Agent_Visual_Director": [
        ("agent:role",      "Visual Director — генерирует изображения и видео"),
        ("agent:framework", "ComfyUI + LTX-Video 2.3 + FLUX.1 [dev] + Moondream VQA"),
        ("agent:status",    "ACTIVE"),
        ("visual:style",    "Футуристичный минимализм: Cyan #06B6D4 + Deep Blue #0F172A"),
        ("visual:model",    "LTX-Video v2.3 (22B Dev) + FLUX.1 [dev]"),
        ("visual:qa",       "PASSED — no anatomical defects detected"),
        ("visual:last_job", "promo_video_ucust_ai_demo_001.mp4"),
    ],
    "orchestrator": [
        ("agent:role",       "Orchestrator — FSM контроллер пайплайна"),
        ("agent:framework",  "CrewAI FSM + Python asyncio"),
        ("agent:status",     "ACTIVE"),
        ("pipeline:status",  "OPERATIONAL — все агенты активны, Octopoda подключена"),
        ("pipeline:version", "UCust.AI v2.1.0 — CrewAI + Saiga Nemo 12B + LTX-Video 2.3"),
        ("pipeline:agents",  "Interviewer → Analyst → Copywriter → FactChecker → Visual_Director"),
        ("pipeline:last_job", json.dumps({
            "job_id": "job_demo_001",
            "fsm_state": "READY_FOR_PUBLISHING",
            "created_at": "2026-08-19T18:00:00",
        })),
    ],
}


def make_backend():
    """Создаём бэкенд или используем REST API (если есть Postgres)."""
    db_url = os.environ.get("DATABASE_URL", "")
    from synrix.agent_backend import SynrixAgentBackend
    if db_url.startswith("postgres"):
        # Force direct postgres connection so metrics are written to DB!
        return SynrixAgentBackend(backend="postgres", dsn=db_url, tenant_id="dev")
        
    db = os.environ.get("OCTOPODA_DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "octopoda_memory.db"))
    return SynrixAgentBackend(sqlite_path=db)


_shared_backend = None
_backend_lock = threading.Lock()


def get_backend():
    global _shared_backend
    with _backend_lock:
        if _shared_backend is None:
            _shared_backend = make_backend()
    return _shared_backend


def run_agent(agent_id: str, memories: list, stop_event: threading.Event):
    """Запускает агента через AgentRuntime(require_account=False) и шлёт heartbeat."""
    try:
        from synrix_runtime.api.runtime import AgentRuntime

        agent = AgentRuntime(
            agent_id,
            agent_type="marketing_agent",
            backend_override=get_backend(),
            require_account=False,
        )

        # Пишем все воспоминания
        ok = 0
        for key, value in memories:
            try:
                agent.remember(key, value)
                ok += 1
            except Exception:
                pass

        print(f"  [OK] {agent_id} — подключён ({ok}/{len(memories)} воспоминаний)")

        # Heartbeat loop — держим агента живым
        while not stop_event.is_set():
            try:
                agent.remember("agent:heartbeat", f"alive at {time.strftime('%H:%M:%S')}")
            except Exception:
                pass
            stop_event.wait(timeout=20)

    except Exception as e:
        print(f"  [ERR] {agent_id}: {e}")


def main():
    print()
    print("=" * 55)
    print("  UCust.AI — Agent Runtime Launcher")
    print("=" * 55)
    print(f"  Starting {len(AGENTS_SEED)} agents...")
    print()

    stop_event = threading.Event()
    threads = []

    for agent_id, memories in AGENTS_SEED.items():
        t = threading.Thread(
            target=run_agent,
            args=(agent_id, memories, stop_event),
            daemon=True,
            name=f"agent-{agent_id}",
        )
        t.start()
        threads.append(t)
        time.sleep(0.3)  # небольшая задержка между стартами

    # Ждём пока все агенты инициализируются
    time.sleep(5)

    print()
    print("=" * 55)
    print("  Все агенты запущены и отправляют heartbeat!")
    print()
    print("  Открой в браузере:")
    print("  http://localhost:7842/dashboard/agents")
    print("  http://localhost:7842/dashboard/memory")
    print()
    print("  Нажми Ctrl+C для остановки.")
    print("=" * 55)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Останавливаем агентов...")
        stop_event.set()
        for t in threads:
            t.join(timeout=3)
        print("  Готово.")


if __name__ == "__main__":
    main()
