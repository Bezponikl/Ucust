# UCust AI & Data Service (Autonomous Multi-Agent Marketing Engine v2.5.0)

Выделенный высокопроизводительный AI & Data сервис для автономного мульти-агентного маркетинга, векторного RAG-поиска, генерации контента, визуального продакшна и омниканальной дистрибуции.

---

## 🏗️ Архитектура сервиса

Сервер функционирует как независимый AI-бэкенд и взаимодействует с внешними микросервисами и бэкендом через **Unified FastAPI Gateway (`ai/api_gateway.py`)** версии **2.5.0**.

```text
[ Java Backend / External Clients / WireGuard Tunnel (10.0.0.2) ] 
                     │ (REST API / Header: X-Internal-Secret)
                     ▼
           [ ai/api_gateway.py ] ──► [ UnifiedOrchestrator ]
                                          │
    ┌─────────────────────────────┬───────┴─────────────────────┬───────────────────────────┐
    ▼                             ▼                             ▼                           ▼
[ Market Intelligence ]     [ Saiga LLM & VQA ]        [ Visual & Studio ]        [ Smart Publishers ]
• WebsiteCollector          • SaigaLLMSkill (8B)       • ComfyUI / LTX-2.3        • Telegram Rich Publisher
• TrendCollector            • Moondream VQA            • Dynamic 2x2 Collage       • VK / OK / MAX Publishers
• EventHolidayCollector     • Charlie Munger Critic    • Vector DB / Chroma        • Edit Buttons without delete
• CompetitorParser          • SecurityGuard            • S3 / MinIO Media          • 100% Width Matching Album
```

---

## 🚀 Быстрый запуск

### 1. Автоматический запуск (Linux / Сервер)
Скрипт автоматически находит виртуальное окружение (`venv`), активирует его и поднимает шлюз:
```bash
git pull origin feature-ai
bash start_ai_service.sh
```

### 2. Запуск на Windows
```powershell
.\start_ai_service.bat
```

### 3. Ручной запуск
```bash
cd ai
source ../venv/bin/activate   # или venv/bin/activate
python3 api_gateway.py
```

* **Хост:** `http://0.0.0.0:8000` (в туннеле WireGuard: `http://10.0.0.2:8000`)
* **Интерактивная документация (Swagger UI):** `http://localhost:8000/docs`

---

## 📡 Основные API-эндпоинты (v2.5.0)

| Метод | Эндпоинт | Описание |
| :--- | :--- | :--- |
| `GET` | `/api/v1/ai/health` | Проверка здоровья шлюза, версии и списка активных агентов |
| `POST` | `/api/v1/orchestrator/execute` | **Главный сквозной запуск мульти-агентного оркестратора** |
| `POST` | `/api/v1/task/execute` | Алиас прямого выполнения маркетинговых и креативных задач |
| `POST` | `/api/v1/ai/tasks/async-generate` | Асинхронная генерация с регистрацией задачи в очереди |
| `GET` | `/api/v1/ai/tasks/{task_id}/status` | Получение статуса и результатов асинхронной задачи |
| `POST` | `/api/v1/collectors/analyze-brand` | Анализ бренда и сайта клиента |
| `POST` | `/api/v1/collectors/analyze-documents` | Парсинг и извлечение данных из клиентских документов |
| `POST` | `/api/v1/vision/quick-analyze` | Быстрый визуальный VQA-анализ референсов |

> **Авторизация:** Запросы к эндпоинтам оркестратора поддерживают заголовок `X-Internal-Secret: ucust-secret-key-2026`.

---

## 🎨 Стандарты Telegram-публикаций

* **1 изображение:** Публикация стандартным постом с фото (`sendPhoto`), полное сохранение пропорций (100% ширина) и прикрепление интерактивных inline/reply кнопок.
* **2 и более изображений:** Публикация **Единым альбомом (`sendMediaGroup`)** с размещением полного текста поста в подписи (caption) для 100% совпадения ширины.
* **Коллажи (2x2):** Генерируются **только при явном указании** в промпте/подсказках пользователя.
* **Обновление кнопок:** Поддерживается динамическое обновление кнопок (`edit_post_buttons`) без удаления и повторной отправки поста.

---

## 📂 Структура проекта

* `ai/api_gateway.py` — Единый FastAPI шлюз v2.5.0 с автоопределением клиентов и маршрутизацией.
* `ai/core/orchestrator.py` — Главный Мульти-Агентный Оркестратор (`UnifiedOrchestrator`).
* `ai/skills/telegram_rich_formatter.py` — Форматирование и вёрстка под стандарты Telegram (цитаты, спойлеры, альбомы, коллажи).
* `ai/publishers/telegram.py` — Паблишер Telegram (sendPhoto, sendMediaGroup, edit_post_buttons).
* `ai/skills/` — Навыки ИИ-агентов (`saiga_llm.py`, `moondream_vqa.py`, `photo_generator.py`, `critic_munger.py`).
* `ai/collectors/` — Парсеры веб-сайтов, трендов ниш и городских инфоповодов.
* `ai/rag/` & `ai/storage/` — Векторная база знаний (RAG), кэш Redis и БД SQLite/PostgreSQL.
* `start_ai_service.sh` / `start_ai_service.bat` — Кроссплатформенные лаунчеры с автопоиском venv.

