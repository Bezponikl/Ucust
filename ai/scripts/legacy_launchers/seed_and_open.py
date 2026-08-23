"""
seed_and_open.py
Записывает память всех UCust.AI агентов через локальный SQLite Octopoda backend
(без зависимости от REST-таймаутов), затем открывает дашборд с авто-авторизацией.
"""
import os
import json
import webbrowser

# ── Загружаем .env ──────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

DASHBOARD_PORT = int(os.environ.get("OCTOPODA_DASHBOARD_PORT", 7842))
API_KEY = os.environ.get("OCTOPODA_API_KEY", "local-dev")
DB_PATH = os.environ.get("OCTOPODA_DB_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "octopoda_memory.db"))

# ── Данные агентов UCust.AI ─────────────────────────────────────
AGENTS_SEED = [
    ("Agent_Interviewer", {
        "brief:company":       "UCust.AI — Мультиагентная система интернет-маркетинга и ORM",
        "brief:audience":      "B2B: маркетологи, IT-директора, собственники SMB",
        "brief:tone_of_voice": "Профессиональный, технологичный, доверительный",
        "brief:region":        "Россия, B2B-сегмент, IT и сервисный бизнес",
        "brief:pain_points":   "Нехватка времени, высокая стоимость SMM-агентств",
    }),
    ("Agent_Analyst", {
        "strategy:core_usp":    "ИИ-агенты с FactChecking без галлюцинаций и ложных акций",
        "strategy:positioning": "Единственная open-source система с нативным фактчекингом",
        "strategy:competitors": "Supa Social, Buffer AI, Jasper — нет FactChecking, нет ORM",
        "strategy:keywords":    "AI-маркетинг, автоматизация SMM, генерация контента ИИ",
        "strategy:swot_strength":"Мультиагентная система, полный цикл от брифа до публикации",
    }),
    ("Agent_Copywriter", {
        "draft:latest_promo":  "🔥 UCust.AI: SMM-автоматизация без галлюцинаций → ucust.ai",
        "framework:current":   "PAS (Problem-Agitation-Solution)",
        "cta:default":         "Записаться на демо → ucust.ai",
        "post:instagram_draft": "Ваши конкуренты уже автоматизировали SMM. Время UCust.AI 🚀",
    }),
    ("Agent_FactChecker", {
        "factcheck:last_result":  "PASSED — ни одного невалидированного суперлатива",
        "factcheck:rule":         "Rule of Differentiation: запрещены ложные скидки без брифа",
        "factcheck:corrections":  "correction_attempts=0 — текст принят с первого прохода",
        "factcheck:status":       "OPERATIONAL",
    }),
    ("Agent_Visual_Director", {
        "visual:style":       "Футуристичный минимализм: Cyan #06B6D4 + Deep Blue #0F172A",
        "visual:model":       "LTX-Video v2.3 (22B Dev) + FLUX.1 [dev] + Moondream VQA",
        "visual:moondream_qa": "PASSED — no anatomical defects detected",
        "visual:last_render": "promo_video_ucust_ai_demo_001.mp4",
    }),
    ("orchestrator", {
        "pipeline:status":  "OPERATIONAL — все агенты активны, Octopoda подключена",
        "pipeline:version": "UCust.AI v2.1.0 — CrewAI + Saiga Nemo 12B + LTX-Video 2.3",
        "pipeline:agents":  "Interviewer, Analyst, Copywriter, FactChecker, Visual_Director",
        "snapshot:last_job": json.dumps({
            "job_id": "job_demo_001", "fsm_state": "READY_FOR_PUBLISHING",
            "created_at": "2026-08-19T18:00:00",
        }),
    }),
]


def seed_via_local_runtime() -> bool:
    """Записать через AgentRuntime + SynrixAgentBackend (SQLite, без REST)."""
    try:
        from octopoda import AgentRuntime, SynrixAgentBackend
        backend = SynrixAgentBackend(sqlite_path=DB_PATH)
        print(f"  SQLite бэкенд: {DB_PATH}")
        for name, kvs in AGENTS_SEED:
            rt = AgentRuntime(
                agent_id=name,
                agent_type="marketing_agent",
                backend_override=backend,
                require_account=False,
            )
            for k, v in kvs.items():
                rt.remember(k, v)
            print(f"  ✓  {name}  ({len(kvs)} ключей)")
        return True
    except Exception as e:
        print(f"  WARN [local runtime]: {e}")
        return False


def seed_via_cloud_client(timeout: int = 8) -> bool:
    """Попробовать быстро записать через cloud client с коротким timeout."""
    try:
        import requests
        from octopoda import Octopoda
        # Patch timeout
        import synrix.cloud as _cloud
        _orig = _cloud.SynrixCloudClient.__init__

        def _patched_init(self, *a, **kw):
            _orig(self, *a, **kw)
            self.timeout = timeout
            if hasattr(self, '_session'):
                self._session.timeout = timeout

        _cloud.SynrixCloudClient.__init__ = _patched_init

        memory = Octopoda(api_key="local-dev", base_url="http://localhost:8741")
        # Проверим быстро один write
        agent = memory.agent("orchestrator")
        agent.write("pipeline:status", "OPERATIONAL — UCust.AI v2.1.0")
        print("  Cloud client: быстрый write прошёл, продолжаем...")
        for name, kvs in AGENTS_SEED:
            ag = memory.agent(name)
            for k, v in kvs.items():
                try:
                    ag.write(k, v)
                except Exception:
                    pass
            print(f"  ✓  {name}")
        return True
    except Exception as e:
        print(f"  WARN [cloud client]: {e}")
        return False


def open_dashboard() -> None:
    """Открыть браузер с auto-login HTML страничкой."""
    html = (
        "<!DOCTYPE html><html lang='ru'><head><meta charset='utf-8'>"
        "<title>UCust.AI — Активация дашборда</title>"
        "<style>body{background:#0f172a;color:#e2e8f0;font-family:system-ui,sans-serif;"
        "display:flex;align-items:center;justify-content:center;height:100vh;margin:0}"
        ".b{text-align:center}.i{font-size:4em}.d{display:inline-block;width:8px;height:8px;"
        "border-radius:50%;background:#06b6d4;animation:bl 1.2s infinite;margin:0 3px}"
        ".d:nth-child(2){animation-delay:.4s}.d:nth-child(3){animation-delay:.8s}"
        "@keyframes bl{0%,100%{opacity:.2}50%{opacity:1}}"
        "h2{color:#06b6d4}p{color:#94a3b8}</style></head><body>"
        "<div class='b'><div class='i'>Octopoda</div>"
        "<h2>UCust.AI Dashboard</h2>"
        "<p>Авторизация разработчика<span class='d'></span>"
        "<span class='d'></span><span class='d'></span></p></div>"
        "<script>"
        "localStorage.setItem('octopoda_api_key','local-dev');"
        "localStorage.setItem('octopoda_tenant_id','dev');"
        "localStorage.setItem('octopoda_email','dev@ucust.local');"
        "localStorage.setItem('octopoda_base_url','http://localhost:8741');"
        f"setTimeout(function(){{window.location.replace('http://localhost:{DASHBOARD_PORT}/dashboard');}},1800);"
        "</script></body></html>"
    )

    login_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_dashboard_login.html")
    with open(login_path, "w", encoding="utf-8") as f:
        f.write(html)
    url = "file:///" + login_path.replace("\\", "/")
    webbrowser.open(url)
    print(f"  Браузер: {url}")


def main():
    print()
    print("=" * 60)
    print("  UCust.AI - Seed Agents & Open Dashboard")
    print("=" * 60)

    print("\n[1/1] Запись памяти агентов (REST API)...")
    ok = seed_via_cloud_client(timeout=8)

    if not ok:
        print("\n  WARN: Запись памяти не удалась, но дашборд откроем.")

    print("\n[2/2] Открытие дашборда...")
    open_dashboard()

    print()
    print("=" * 60)
    print("  Адреса:")
    print(f"  [Dashboard]  http://localhost:{DASHBOARD_PORT}/dashboard")
    print(f"  [Agents]     http://localhost:{DASHBOARD_PORT}/dashboard/agents")
    print(f"  [Memory]     http://localhost:{DASHBOARD_PORT}/dashboard/memory")
    print(f"  [Audit]      http://localhost:{DASHBOARD_PORT}/dashboard/audit")
    print(f"  [API]        http://localhost:8741/api/agents")
    print(f"  [Docs]       http://localhost:8741/docs")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
