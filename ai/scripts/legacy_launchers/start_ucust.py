"""
start_ucust.py
Универсальный стартовый скрипт UCust.AI:
1. Запускает Octopoda сервер (Flask dashboard :7842 + Uvicorn API :8741)
2. Заполняет память агентов через SQLite backend
3. Запускает прокси с авто-авторизацией на :7843
4. Открывает браузер на http://localhost:7843/dashboard
"""
import os, sys, json, time, threading, webbrowser, subprocess
import http.server, urllib.request, urllib.error

# ── Настройки ────────────────────────────────────────────────────
UPSTREAM_PORT  = 7842   # Flask Dashboard
API_PORT       = 8741   # Uvicorn FastAPI
PROXY_PORT     = 7843   # Наш прокси
API_KEY        = "local-dev"
TENANT_ID      = "dev"
EMAIL          = "dev@ucust.local"
DB_PATH        = os.path.join(os.path.dirname(os.path.abspath(__file__)), "octopoda_memory.db")

# ── Данные агентов UCust.AI ──────────────────────────────────────
AGENTS = [
    ("Agent_Interviewer", {
        "brief:company":       "UCust.AI - Multiagent Internet Marketing & ORM System",
        "brief:audience":      "B2B: marketers, IT directors, SMB owners",
        "brief:tone_of_voice": "Professional, tech-savvy, trustworthy",
        "brief:region":        "Russia, B2B segment, IT and service business",
        "brief:pain_points":   "Lack of time, high SMM agency costs",
        "agent:role":          "Interviewer — collects client brief and goals",
        "agent:status":        "ACTIVE",
    }),
    ("Agent_Analyst", {
        "strategy:core_usp":    "AI agents with FactChecking — no hallucinations or fake promotions",
        "strategy:positioning": "Only open-source system with native multiagent factchecking",
        "strategy:competitors": "Supa Social, Buffer AI, Jasper — no FactCheck, no ORM, no video",
        "strategy:keywords":    "AI marketing, SMM automation, AI content generation",
        "agent:role":           "Analyst — builds strategy, SWOT, USP",
        "agent:status":         "ACTIVE",
    }),
    ("Agent_Copywriter", {
        "draft:latest_promo":   "UCust.AI: SMM automation without hallucinations -> ucust.ai",
        "framework:current":    "PAS (Problem-Agitation-Solution)",
        "cta:default":          "Book a demo -> ucust.ai",
        "post:instagram_draft": "Your competitors already automated SMM. Time for UCust.AI",
        "agent:role":           "Copywriter — generates posts, ads, captions",
        "agent:status":         "ACTIVE",
    }),
    ("Agent_FactChecker", {
        "factcheck:last_result": "PASSED — zero unvalidated superlatives",
        "factcheck:rule":        "Rule of Differentiation: no fake discounts without brief confirmation",
        "factcheck:corrections": "correction_attempts=0 — text accepted on first pass",
        "factcheck:status":      "OPERATIONAL",
        "agent:role":            "FactChecker — validates all claims against brief",
        "agent:status":          "ACTIVE",
    }),
    ("Agent_Visual_Director", {
        "visual:style":       "Futuristic minimalism: Cyan #06B6D4 + Deep Blue #0F172A",
        "visual:model":       "LTX-Video v2.3 (22B Dev) + FLUX.1 [dev] + Moondream VQA",
        "visual:moondream_qa": "PASSED — no anatomical defects detected",
        "visual:last_render": "promo_video_ucust_ai_demo_001.mp4",
        "agent:role":         "Visual Director — generates images and videos",
        "agent:status":       "ACTIVE",
    }),
    ("orchestrator", {
        "pipeline:status":  "OPERATIONAL — all agents active, Octopoda connected",
        "pipeline:version": "UCust.AI v2.1.0 — CrewAI + Saiga Nemo 12B + LTX-Video 2.3",
        "pipeline:agents":  "Interviewer, Analyst, Copywriter, FactChecker, Visual_Director",
        "agent:role":       "Orchestrator — FSM pipeline controller",
        "agent:status":     "ACTIVE",
        "snapshot:last_job": json.dumps({
            "job_id": "job_demo_001", "fsm_state": "READY_FOR_PUBLISHING",
            "agents_done": ["Interviewer", "Analyst", "Copywriter", "FactChecker", "Visual_Director"],
            "created_at": "2026-08-19T18:00:00",
        }),
    }),
]

# ── Прокси с авто-инжекцией авторизации ─────────────────────────
AUTH_SCRIPT = f"""
<script>
(function(){{
  var d = {{
    'octopoda_api_key':   '{API_KEY}',
    'octopoda_tenant_id': '{TENANT_ID}',
    'octopoda_email':     '{EMAIL}',
    'octopoda_base_url':  'http://localhost:{API_PORT}'
  }};
  for (var k in d) localStorage.setItem(k, d[k]);
  if (window.location.pathname === '/login' || window.location.pathname === '/') {{
    window.location.replace('/dashboard');
  }}
}})();
</script>
"""

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # тихий режим

    def _proxy(self, method):
        url = f"http://127.0.0.1:{UPSTREAM_PORT}{self.path}"
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b""
        hdrs = {k: v for k, v in self.headers.items()
                if k.lower() not in ("host", "connection", "transfer-encoding")}
        hdrs["Host"] = f"127.0.0.1:{UPSTREAM_PORT}"
        req = urllib.request.Request(url, data=body or None, headers=hdrs, method=method)
        try:
            resp = urllib.request.urlopen(req, timeout=10)
        except urllib.error.HTTPError as e:
            resp = e
        raw = resp.read()
        ct = resp.headers.get("Content-Type", "")
        if "text/html" in ct:
            try:
                html = raw.decode("utf-8")
                inject = AUTH_SCRIPT
                if "</head>" in html:
                    html = html.replace("</head>", inject + "</head>", 1)
                elif "<body" in html:
                    html = html.replace("<body", inject + "<body", 1)
                else:
                    html = inject + html
                raw = html.encode("utf-8")
            except Exception:
                pass
        code = resp.status if hasattr(resp, "status") else resp.code
        self.send_response(code)
        skip = {"transfer-encoding", "content-encoding", "content-length", "connection"}
        for k, v in resp.headers.items():
            if k.lower() not in skip:
                self.send_header(k, v)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):     self._proxy("GET")
    def do_POST(self):    self._proxy("POST")
    def do_PUT(self):     self._proxy("PUT")
    def do_DELETE(self):  self._proxy("DELETE")
    def do_OPTIONS(self): self._proxy("OPTIONS")
    def do_PATCH(self):   self._proxy("PATCH")


def run_proxy():
    server = http.server.HTTPServer(("127.0.0.1", PROXY_PORT), ProxyHandler)
    server.serve_forever()


def wait_dashboard(timeout=40):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{UPSTREAM_PORT}/api/agents", timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False


def seed_agents():
    try:
        from octopoda import AgentRuntime, SynrixAgentBackend
        backend = SynrixAgentBackend(sqlite_path=DB_PATH)
        for name, kvs in AGENTS:
            rt = AgentRuntime(
                agent_id=name,
                agent_type="marketing_agent",
                backend_override=backend,
                require_account=False,
            )
            for k, v in kvs.items():
                rt.remember(k, v)
            print(f"  [seed] {name} OK ({len(kvs)} keys)")
        return True
    except Exception as e:
        print(f"  [seed] WARN: {e}")
        return False


def main():
    print("[UCust.AI] Starting...")

    # 1. Проверяем есть ли уже сервер
    server_up = False
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{UPSTREAM_PORT}/api/agents", timeout=2)
        server_up = True
        print(f"[OK] Octopoda server already running on :{UPSTREAM_PORT}")
    except Exception:
        pass

    if not server_up:
        print("[..] Starting Octopoda server...")
        subprocess.Popen(
            [sys.executable, "-m", "synrix_runtime.start"],
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
        )
        print("[..] Waiting for server to be ready...")
        if wait_dashboard(timeout=40):
            print(f"[OK] Server ready on :{UPSTREAM_PORT}")
        else:
            print("[!!] Server timeout — check Octopoda manually")

    # 2. Seed агентов
    print("[..] Seeding agent memories...")
    seed_agents()

    # 3. Запускаем прокси в фоновом потоке
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{PROXY_PORT}", timeout=1)
        print(f"[OK] Proxy already running on :{PROXY_PORT}")
    except Exception:
        t = threading.Thread(target=run_proxy, daemon=True)
        t.start()
        time.sleep(0.5)
        print(f"[OK] Proxy started on :{PROXY_PORT}")

    # 4. Открываем браузер
    url = f"http://localhost:{PROXY_PORT}/dashboard"
    print(f"[OK] Opening browser: {url}")
    webbrowser.open(url)

    print()
    print("=" * 50)
    print(f"  Dashboard: http://localhost:{PROXY_PORT}/dashboard")
    print(f"  Agents:    http://localhost:{PROXY_PORT}/dashboard/agents")
    print(f"  Memory:    http://localhost:{PROXY_PORT}/dashboard/memory")
    print(f"  REST API:  http://localhost:{API_PORT}/v1/agents")
    print(f"  Swagger:   http://localhost:{API_PORT}/docs")
    print("=" * 50)
    print("  Press Ctrl+C to stop proxy.")
    print()

    # Держим прокси живым
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[..] Stopped.")


if __name__ == "__main__":
    main()
