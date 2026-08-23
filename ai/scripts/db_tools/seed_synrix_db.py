"""
seed_synrix_db.py
Напрямую записывает данные UCust.AI агентов в synrix.db (nodes таблица),
минуя медленный REST API. Формат совместим с тем, что пишет AgentRuntime.
"""
import sqlite3, json, time, random, os

DB_PATH = r'C:\Users\Metal\.synrix\data\synrix.db'

AGENTS_DATA = {
    "Agent_Interviewer": {
        "agent:role":          "Interviewer — собирает бриф клиента и цели кампании",
        "agent:status":        "ACTIVE",
        "agent:framework":     "CrewAI + Saiga Nemo 12B (Ollama)",
        "brief:company":       "UCust.AI — Мультиагентная система интернет-маркетинга и ORM",
        "brief:audience":      "B2B: маркетологи, IT-директора, собственники SMB",
        "brief:tone_of_voice": "Профессиональный, технологичный, доверительный",
        "brief:region":        "Россия, B2B-сегмент, IT и сервисный бизнес",
        "brief:pain_points":   "Нехватка времени, высокая стоимость SMM-агентств",
    },
    "Agent_Analyst": {
        "agent:role":           "Analyst — строит стратегию, SWOT, USP",
        "agent:status":         "ACTIVE",
        "agent:framework":      "CrewAI + Saiga Nemo 12B (Ollama)",
        "strategy:core_usp":    "ИИ-агенты с FactChecking без галлюцинаций и ложных акций",
        "strategy:positioning": "Единственная open-source система с нативным фактчекингом",
        "strategy:competitors": "Supa Social, Buffer AI, Jasper — нет FactCheck, нет ORM",
        "strategy:keywords":    "AI-маркетинг, автоматизация SMM, генерация контента ИИ",
        "strategy:swot":        "Сила: полный цикл от брифа до публикации за 3 минуты",
    },
    "Agent_Copywriter": {
        "agent:role":          "Copywriter — генерирует посты, рекламу, подписи",
        "agent:status":        "ACTIVE",
        "agent:framework":     "CrewAI + Saiga Nemo 12B (Ollama)",
        "draft:latest_promo":  "UCust.AI: SMM-автоматизация с фактчекингом → ucust.ai",
        "framework:current":   "PAS (Problem-Agitation-Solution)",
        "cta:default":         "Записаться на демо → ucust.ai",
        "post:status":         "READY_FOR_FACTCHECK",
    },
    "Agent_FactChecker": {
        "agent:role":             "FactChecker — валидирует утверждения по брифу",
        "agent:status":           "ACTIVE",
        "agent:framework":        "CrewAI + Saiga Nemo 12B (Ollama)",
        "factcheck:last_result":  "PASSED — ни одного невалидированного суперлатива",
        "factcheck:rule":         "Rule of Differentiation: запрещены ложные скидки без брифа",
        "factcheck:corrections":  "correction_attempts=0 — текст принят с первого прохода",
        "factcheck:status":       "OPERATIONAL",
    },
    "Agent_Visual_Director": {
        "agent:role":       "Visual Director — генерирует изображения и видео",
        "agent:status":     "ACTIVE",
        "agent:framework":  "ComfyUI + LTX-Video 2.3 + FLUX.1 [dev]",
        "visual:style":     "Футуристичный минимализм: Cyan #06B6D4 + Deep Blue #0F172A",
        "visual:model":     "LTX-Video v2.3 (22B Dev) + FLUX.1 [dev] + Moondream VQA",
        "visual:qa_result": "PASSED — no anatomical defects detected",
        "visual:last_job":  "promo_video_ucust_ai_demo_001.mp4",
    },
    "orchestrator": {
        "agent:role":       "Orchestrator — FSM контроллер пайплайна",
        "agent:status":     "ACTIVE",
        "agent:framework":  "CrewAI FSM + Python asyncio",
        "pipeline:status":  "OPERATIONAL — все агенты активны, Octopoda подключена",
        "pipeline:version": "UCust.AI v2.1.0 — CrewAI + Saiga Nemo 12B + LTX-Video 2.3",
        "pipeline:agents":  "Interviewer → Analyst → Copywriter → FactChecker → Visual_Director",
        "pipeline:last_job": json.dumps({
            "job_id": "job_demo_001",
            "fsm_state": "READY_FOR_PUBLISHING",
            "created_at": "2026-08-19T18:00:00",
        }),
    },
}


def make_node_id() -> str:
    return str(random.randint(10**14, 10**15 - 1))


def write_nodes(db: sqlite3.Connection, agent_id: str, kvs: dict) -> int:
    now = str(time.time())
    written = 0
    for key, value in kvs.items():
        node_name = f"memory:{agent_id}:{key}"
        data = json.dumps({"value": value, "metadata": {"agent_id": agent_id, "key": key}})
        node_id = make_node_id()

        # Upsert: если такой узел уже есть — обновляем, иначе вставляем
        existing = db.execute(
            "SELECT id FROM nodes WHERE collection='agent_memory' AND name=?",
            (node_name,)
        ).fetchone()

        if existing:
            db.execute(
                "UPDATE nodes SET data=?, updated_at=?, version=version+1 WHERE id=?",
                (data, now, existing['id'])
            )
        else:
            db.execute(
                """INSERT INTO nodes (id, collection, name, data, node_type, created_at, updated_at,
                   embedding, valid_from, valid_until, version)
                   VALUES (?, 'agent_memory', ?, ?, 'primitive', ?, ?, NULL, ?, NULL, 1)""",
                (node_id, node_name, data, now, now, now)
            )
        written += 1
    db.commit()
    return written


def main():
    print()
    print("=" * 55)
    print("  UCust.AI — Direct DB Seed (synrix.db)")
    print("=" * 55)

    if not os.path.exists(DB_PATH):
        print(f"  ERROR: {DB_PATH} not found!")
        return

    db = sqlite3.connect(DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row

    total = 0
    for agent_id, kvs in AGENTS_DATA.items():
        n = write_nodes(db, agent_id, kvs)
        total += n
        print(f"  OK  {agent_id}  ({n} nodes)")

    db.close()
    print()
    print(f"  Total: {total} memory nodes written to synrix.db")
    print()

    # Проверка через Flask API
    try:
        import urllib.request
        r = urllib.request.urlopen("http://localhost:7842/api/agents", timeout=4)
        agents = __import__('json').loads(r.read())
        ucust_agents = [a for a in agents if "Agent_" in a.get("agent_id","") or a.get("agent_id") == "orchestrator"]
        print(f"  Flask /api/agents: {len(agents)} total, {len(ucust_agents)} UCust.AI agents")
        for a in ucust_agents:
            print(f"    {a['agent_id']:30s} memories={a.get('memory_node_count',0)}")
    except Exception as e:
        print(f"  API check skipped: {e}")

    print()
    print("  Refresh the dashboard:")
    print("  http://localhost:7842/dashboard/agents")
    print("  http://localhost:7842/dashboard/memory")
    print("=" * 55)


if __name__ == "__main__":
    main()
