# Карта интеграций и конфигурационный справочник «UCust.AI»

**Дата актуализации:** 29 июля 2026 г.  
**Версия подсистемы:** 2.1.0-MultiPlatform  
**Назначение документа:** Справочное руководство для разработчиков по местам подключения внешних API, конфигурационным переменным окружения (`.env`) и точкам инициализации клиентов.

---

## 1. Сводная таблица внешних сервисов и конфигураций

| Сервис / Платформа | Модуль и путь к файлу | Переменные окружения (.env) | Точка инициализации клиента в коде | Назначение |
| :--- | :--- | :--- | :--- | :--- |
| **PostgreSQL / Database** | `storage/db.py` | `DATABASE_URL`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `UCUST_DB_HOST`, `UCUST_DB_PORT` | `get_async_engine()`, `init_db()`, `DatabaseFactory.build()` | Персистентное хранение профилей клиентов, задач FSM и JSON-нагрузок |
| **ComfyUI (LTX-2.3 Engine)** | `skills/comfyui_local.py` | `COMFYUI_SERVER_ADDRESS` (default: `127.0.0.1:8188`), `COMFYUI_OUTPUT_DIR` | `ComfyUILocalSkill.__init__()` | Генерация мультимодальных видео+аудио графов LTX-2.3 |
| **Travity / Tavily Search API** | `skills/travity_search.py` | `TRAVITY_API_KEY`, `TAVILY_API_KEY` | `TravitySearchSkill.search()` | Живой поиск маркетинговых трендов и новостей из интернета |
| **Telegram Telethon (Parser)** | `collectors/telethon_collector.py` | `UCUST_TELEGRAM_API_ID`, `UCUST_TELEGRAM_API_HASH`, `UCUST_TELEGRAPH_SESSION`, `UCUST_TELETHON_CHANNEL` | `TelethonCollector.__init__()` | Сбор постов и сигналов из Telegram-каналов конкурентов |
| **Telegram UserBot (Publisher)** | `publishers/telegram.py` | `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_SESSION_NAME`, `TELEGRAM_TARGET_CHANNEL` | `TelegramPublisher._get_client()` | Отправка постов и `.mp4` медиафайлов от лица UserBot |
| **VK API (Parser & Publisher)** | `collectors/vk_collector.py`, `publishers/vk.py` | `UCUST_VK_ACCESS_TOKEN`, `VK_ACCESS_TOKEN`, `UCUST_VK_GROUP_ID`, `VK_GROUP_ID` | `VkApiCollector.__init__()`, `VkPublisher.__init__()` | Парсинг сообществ VK и публикация постов на стене (`wall.post`) |
| **Instagram Meta Graph API** | `publishers/instagram.py` | `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_ACCOUNT_ID` | `InstagramPublisher.__init__()` | Создание медиа-контейнеров и публикация видео/фото в Instagram |
| **Одноклассники (OK.ru API)** | `publishers/ok.py` | `OK_ACCESS_TOKEN`, `OK_APPLICATION_KEY`, `OK_GROUP_ID` | `OdnoklassnikiPublisher.__init__()` | Создание заметок `mediatopic.post` с прикрепленным медиа в группах OK |
| **МАКС Мессенджер (MAX Platform)** | `publishers/max.py` | `MAX_API_TOKEN`, `MAX_CHAT_ID`, `MAX_API_URL` (default: `https://platform-api2.max.ru/messages`) | `MaxPublisher.publish()` | Отправка сообщений и multipart медиафайлов через REST API МАКС |
| **Java Backend REST Bridge** | `integration/java_bridge.py` | `JAVA_BACKEND_URL`, `UCUST_JAVA_BACKEND_URL` (default: `http://localhost:8080/api/v1`) | `JavaBridgeClient.__init__()` | Передача готовых черновиков и LTX-2.3 воркфлоу на внешнюю Java-платформу |

---

## 2. Подробное описание точек подключения

---

### 2.1. Инфраструктурные сервисы

#### 1. PostgreSQL Database Storage
* **Файлы реализации:** `storage/db.py`, `storage/repository.py`, `storage/models.py`.
* **Переменные окружения:**
  * `DATABASE_URL`: Полная строка подключения SQLAlchemy (например, `postgresql+asyncpg://postgres:postgres@localhost:5432/ai_smm`).
  * `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `UCUST_DB_HOST`, `UCUST_DB_PORT`.
* **Точки инициализации:**
  * `get_async_engine()` в `storage/db.py` (строка 45) — создает `AsyncEngine` с автоматическим фолбэком на SQLite (`sqlite:///./ai_smm_dev.db`) при недоступности PostgreSQL.
  * `init_db()` в `storage/db.py` (строка 112) — асинхронная инициализация таблиц при старте FastAPI.

#### 2. ComfyUI Headless API (LTX-2.3 Multimodal Engine)
* **Файлы реализации:** `skills/comfyui_local.py`, `core/agents.py` (`Agent_Visual_Director`).
* **Переменные окружения:**
  * `COMFYUI_SERVER_ADDRESS`: Хост и порт ComfyUI сервера (по умолчанию `127.0.0.1:8188` или `host.docker.internal:8188` в контейнере).
  * `COMFYUI_OUTPUT_DIR`: Локальный путь к папке сгенерированных файлов ComfyUI (по умолчанию `./output`).
* **Точки инициализации:**
  * `ComfyUILocalSkill.__init__()` в `skills/comfyui_local.py` (строка 30) — подключается к локальному сетевому шлейфу ComfyUI.

---

### 2.2. Сервисы внешних данных и парсеры

#### 1. Travity / Tavily Search API
* **Файлы реализации:** `skills/travity_search.py`, `core/agents.py` (`Agent_Analyst`).
* **Переменные окружения:**
  * `TRAVITY_API_KEY` / `TAVILY_API_KEY`: API ключ доступа к веб-поиску Travity.
* **Точки инициализации:**
  * `TravitySearchSkill.search()` в `skills/travity_search.py` (строка 40) — делает асинхронный HTTP POST-запрос к `https://api.tavily.com/search`.

#### 2. Telegram Telethon Parser
* **Файлы реализации:** `collectors/telethon_collector.py`, `core/agents.py` (`Agent_Analyst`).
* **Переменные окружения:**
  * `UCUST_TELEGRAM_API_ID`, `UCUST_TELEGRAM_API_HASH`, `UCUST_TELEGRAPH_SESSION`, `UCUST_TELETHON_CHANNEL`.
* **Точки инициализации:**
  * `TelethonCollector.__init__()` в `collectors/telethon_collector.py` (строка 25) — парсер постов Telegram.

#### 3. VK API Collector
* **Файлы реализации:** `collectors/vk_collector.py`, `core/agents.py` (`Agent_Analyst`).
* **Переменные окружения:**
  * `UCUST_VK_ACCESS_TOKEN`, `UCUST_VK_GROUP_ID`.
* **Точки инициализации:**
  * `VkApiCollector.__init__()` в `collectors/vk_collector.py` (строка 22) — сбор постов сообществ ВКонтакте.

---

### 2.3. Мультиплатформенные паблишеры соцсетей (`publishers/`)

#### 1. Telegram Publisher (Telethon UserBot)
* **Файлы реализации:** `publishers/telegram.py`.
* **Переменные окружения:**
  * `TELEGRAM_API_ID`: Идентификатор приложения Telegram.
  * `TELEGRAM_API_HASH`: Хэш приложения Telegram.
  * `TELEGRAM_SESSION_NAME`: Имя файла сессии UserBot.
  * `TELEGRAM_TARGET_CHANNEL`: Целевой канал/чат (по умолчанию `@ucust_official`).
* **Точки инициализации:**
  * `TelegramPublisher._get_client()` в `publishers/telegram.py` (строка 40) — ленивая инициализация `TelegramClient`.

#### 2. VK Publisher (VK API Wall Posting)
* **Файлы реализации:** `publishers/vk.py`.
* **Переменные окружения:**
  * `VK_ACCESS_TOKEN` / `UCUST_VK_ACCESS_TOKEN`: Сервисный ключ доступа VK API.
  * `VK_GROUP_ID` / `UCUST_VK_GROUP_ID`: Идентификатор группы ВКонтакте.
* **Точки инициализации:**
  * `VkPublisher.publish()` в `publishers/vk.py` (строка 30) — вызов API `wall.post`.

#### 3. Instagram Publisher (Meta Graph API)
* **Файлы реализации:** `publishers/instagram.py`.
* **Переменные окружения:**
  * `INSTAGRAM_ACCESS_TOKEN`: Маркер доступа Meta Graph API.
  * `INSTAGRAM_ACCOUNT_ID`: Идентификатор бизнес-аккаунта Instagram.
* **Точки инициализации:**
  * `InstagramPublisher.publish()` в `publishers/instagram.py` (строка 35) — создание медиа-контейнеров и публикация.

#### 4. Одноклассники Publisher (OK.ru API)
* **Файлы реализации:** `publishers/ok.py`.
* **Переменные окружения:**
  * `OK_ACCESS_TOKEN`: Сессионный токен OK.ru.
  * `OK_APPLICATION_KEY`: Публичный ключ приложения OK.
  * `OK_GROUP_ID`: Идентификатор группы Одноклассников.
* **Точки инициализации:**
  * `OdnoklassnikiPublisher.publish()` в `publishers/ok.py` (строка 35) — метод `mediatopic.post`.

#### 5. МАКС Мессенджер Publisher (MAX Platform API)
* **Файлы реализации:** `publishers/max.py`.
* **Переменные окружения:**
  * `MAX_API_TOKEN`: Токен авторизации платформы МАКС.
  * `MAX_CHAT_ID`: Идентификатор целевого чата МАКС.
  * `MAX_API_URL`: Эндпоинт API (по умолчанию `https://platform-api2.max.ru/messages`).
* **Точки инициализации:**
  * `MaxPublisher.publish()` в `publishers/max.py` (строка 50) — отправка сообщений и multipart-файлов через `httpx.AsyncClient`.

---

## 3. Инструкция по смене ключей и конфигурации

Для изменения любого API-ключа или подключения нового окружения:
1. Создайте файл `.env` в корне каталога `ai/` на основе шаблона `.env.example`.
2. Внесите необходимые значения (например, `TRAVITY_API_KEY=tvly-new-key` или `MAX_API_TOKEN=your_token`).
3. При замене параметров перезапустите контейнеры через `docker compose restart api` или перезапустите процесс FastAPI.
