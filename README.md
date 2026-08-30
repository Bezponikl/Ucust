# UCust AI & Data Service (Autonomous Multi-Agent Marketing Engine)

Выделенный высокопроизводительный AI & Data сервис для автономного мульти-агентного маркетинга, векторного RAG-поиска, генерации контента, визуального продакшна и дистрибуции.

---

## 🏗️ Архитектура сервиса

Сервер функционирует как независимый AI-бэкенд и взаимодействует с внешними приложениями (бэкендом/фронтендом) через **FastAPI Gateway (`ai/api_gateway.py`)**.

```text
[ External Backend / Frontend ] 
             │ (REST API / WebSocket)
             ▼
   [ ai/api_gateway.py ] ──► [ UnifiedOrchestrator ]
                                  │
    ┌─────────────────────────────┼─────────────────────────────┐
    ▼                             ▼                             ▼
[ Market Intelligence ]     [ Saiga LLM & VQA ]        [ Visual & Storage ]
• WebsiteCollector          • SaigaLLMSkill (8B)       • ComfyUI / SDXL
• TrendCollector            • Moondream VQA            • Vector DB / Chroma
• EventHolidayCollector     • Charlie Munger Critic    • SQLite / Redis Cache
• CompetitorParser          • SecurityGuard            • Social Publishers
```

---

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
pip install -r ai/requirements.txt
```

### 2. Запуск API-шлюза
```bash
python ai/api_gateway.py
# Шлюз доступен на http://0.0.0.0:8000
# Документация Swagger UI: http://localhost:8000/docs
```

### 3. Запуск тестов сквозного пайплайна
```bash
# Сквозной пайплайн онбординга нового аккаунта:
python ai/scripts/test_orchestrator_backend_pipeline.py --no-gen

# Тест универсальности для всех ниш (медицина, стрит-ритейл, creator economy):
python ai/scripts/test_universal_niches_orchestrator.py

# Тест живого парсинга и генерации для бьюти-сферы:
python ai/scripts/test_crocus_beauty_pipeline.py
```

---

## 📂 Структура проекта

* `ai/core/orchestrator.py` — Главный Мульти-Агентный Оркестратор (`UnifiedOrchestrator`).
* `ai/api_gateway.py` — FastAPI шлюз для взаимодействия с основным сервером.
* `ai/skills/` — Навыки ИИ-агентов (`saiga_llm.py`, `moondream_vqa.py`, `photo_generator.py`, `critic_munger.py`).
* `ai/collectors/` — Парсеры веб-сайтов, трендов ниш и городских инфоповодов.
* `ai/rag/` & `ai/storage/` — Векторная база знаний (RAG), кэш Redis и персистентная БД SQLite/PostgreSQL.
* `ai/publishers/` — Омниканальная дистрибуция контента в Telegram, VK, OK, MAX.
* `ai/scripts/` — Набор сквозных тестовых сценариев и утилит.
