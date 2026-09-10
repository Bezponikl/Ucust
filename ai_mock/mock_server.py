"""
UCust AI Service Gateway — Standalone Mock Server (FastAPI)
Provides 100% API-compatible mock replicas for all 37 REST endpoints, WebSockets, background tasks, and reverse webhooks.
Runs instantaneously with zero GPU/CUDA dependencies.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import asyncio
import json
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ai_mock.mock_orchestrator import MockUnifiedOrchestrator, MockSecurityGuard
from ai_mock.mock_queue import MockAsyncGenerationQueueManager
from ai_mock.mock_rag import MockCleanRAGPipeline


# -------------------------------------------------------------------
# 1. Pydantic Models (Matching production v2.5.0 contract)
# -------------------------------------------------------------------

class OrchestratorTaskRequest(BaseModel):
    task_type: str = Field(
        ...,
        example="generate_post",
        description="Тип задачи: 'generate_post', 'quick_vision', 'analyze_documents', 'quick_scan', 'onboard_user', 'parse_telegram', 'parse_vk', 'parse_geo', 'parse_website', 'plan_content', 'feedback_loop', 'rag_query', 'rag_ingest'"
    )
    user_id: str = Field("default_user", example="usr_94812", description="Идентификатор пользователя")
    session_id: Optional[str] = Field(None, example="sess_abc123", description="ID сессии диалога / трейса")
    callback_url: Optional[str] = Field(None, example="http://10.0.0.1:8080/api/v1/ai/callback", description="Динамический URL вебхука для авто-пуша")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Полезная нагрузка")
    sync_backend: bool = Field(default=True, description="Флаг авто-пуша результата в бэкенд")


class OrchestratorTaskResponse(BaseModel):
    status: str = Field(..., example="success")
    task_type: str
    user_id: str
    session_id: str
    data: Dict[str, Any] = Field(default_factory=dict)
    timings: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class BrandGuidelines(BaseModel):
    addressingStyle: Optional[str] = "YOU_PLURAL"
    forbiddenWords: Optional[List[str]] = Field(default_factory=list)
    mandatoryPhrases: Optional[List[str]] = Field(default_factory=list)
    emojiPolicy: Optional[str] = "MINIMAL"
    brandKeywords: Optional[List[str]] = Field(default_factory=list)


class VisualDna(BaseModel):
    brandColors: Optional[List[str]] = Field(default_factory=list)
    visualStyle: Optional[str] = "PHOTOREALISTIC"
    moodKeywords: Optional[List[str]] = Field(default_factory=list)
    logoUrl: Optional[str] = None
    watermarkPosition: Optional[str] = "BOTTOM_RIGHT"
    aspectRatio: Optional[str] = "1:1"


class ProductItem(BaseModel):
    name: str
    price: Optional[str] = None
    description: Optional[str] = None
    flavorNotes: Optional[str] = None
    category: Optional[str] = None
    ctaUrl: Optional[str] = None


class LocationBranch(BaseModel):
    address: str
    city: Optional[str] = None
    workingHours: Optional[str] = None
    phone: Optional[str] = None


class ProjectContext(BaseModel):
    id: Optional[str] = None
    projectId: Optional[str] = None
    name: Optional[str] = None
    companyName: Optional[str] = None
    industry: Optional[str] = None
    niche: Optional[str] = None
    city: Optional[str] = "Москва"
    description: Optional[str] = None
    targetAudience: Optional[str] = None
    toneOfVoice: Optional[str] = "FRIENDLY"
    brandGuidelines: Optional[BrandGuidelines] = None
    visualDna: Optional[VisualDna] = None
    productsCatalog: Optional[List[ProductItem]] = Field(default_factory=list)
    keyBenefits: Optional[List[str]] = Field(default_factory=list)
    locations: Optional[List[LocationBranch]] = Field(default_factory=list)
    deliveryInfo: Optional[str] = None
    language: Optional[str] = "ru"
    recentPostTopics: Optional[List[str]] = Field(default_factory=list)
    socialLinks: Optional[Dict[str, Any]] = None
    businessHours: Optional[Dict[str, Any]] = None
    ownerId: Optional[str] = None
    logoUrl: Optional[str] = None
    brandColors: Optional[List[str]] = None
    usp: Optional[str] = None


class GeneratePostRequest(BaseModel):
    projectId: Optional[str] = None
    project_id: Optional[str] = None
    prompt: Optional[str] = None
    topic: Optional[str] = None
    companyName: Optional[str] = None
    company_name: Optional[str] = None
    niche: Optional[str] = None
    attachments: Optional[List[Any]] = Field(default_factory=list)
    promoCode: Optional[str] = None
    promo_code: Optional[str] = None
    projectContext: Optional[ProjectContext] = None
    project_context: Optional[ProjectContext] = None
    rubric: Optional[str] = None
    primaryCta: Optional[str] = None
    targetActionLink: Optional[str] = None
    language: Optional[str] = "ru"
    tone: Optional[str] = None
    aspect_ratio: Optional[str] = "1:1"
    callback_url: Optional[str] = None
    user_id: Optional[str] = "default_user"
    session_id: Optional[str] = None
    generate_image: bool = True


class AsyncGenerateTaskRequest(BaseModel):
    topic: str
    company_name: Optional[str] = "UCust"
    niche: Optional[str] = "Бизнес"
    tone: Optional[str] = "Дерзкий, уверенный, вдохновляющий"
    aspect_ratio: Optional[str] = "9:16"
    variation_index: Optional[int] = 0
    stage: Optional[str] = "problem_aware"
    framework: Optional[str] = None
    trigger: Optional[str] = None
    tier: Optional[str] = "BUSINESS"
    custom_prompt: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    callback_url: Optional[str] = None
    task_id: Optional[str] = None
    user_id: Optional[str] = "default_user"
    session_id: Optional[str] = None
    projectContext: Optional[ProjectContext] = None
    project_context: Optional[ProjectContext] = None


class UniversalCollectorRequest(BaseModel):
    source_type: Optional[str] = "auto"
    target: str
    limit: Optional[int] = 10
    include_media_vqa: Optional[bool] = True
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict)
    user_id: Optional[str] = "default_user"
    session_id: Optional[str] = None


class TelegramAnalyzeRequest(BaseModel):
    channel: str
    limit: Optional[int] = 10
    include_media_vqa: Optional[bool] = True
    user_id: Optional[str] = "default_user"
    session_id: Optional[str] = None


class VkAnalyzeRequest(BaseModel):
    group_id: str
    limit: Optional[int] = 10
    user_id: Optional[str] = "default_user"
    session_id: Optional[str] = None


class GeoAnalyzeRequest(BaseModel):
    url: str
    provider: Optional[str] = "auto"
    limit: Optional[int] = 10
    user_id: Optional[str] = "default_user"
    session_id: Optional[str] = None


class WebsiteAnalyzeRequest(BaseModel):
    url: str


class CompetitorAnalyzeRequest(BaseModel):
    url: str
    niche: Optional[str] = "Бизнес"


class StrategyGenerateRequest(BaseModel):
    company_name: Optional[str] = "UCust"
    niche: str
    target_audience: Optional[str] = ""
    usp: Optional[str] = ""


class CriticReviewRequest(BaseModel):
    text: str
    topic: Optional[str] = ""
    niche: Optional[str] = ""
    strictness: Optional[float] = 0.85


class ImageGenerateRequest(BaseModel):
    prompt: str
    niche: Optional[str] = "Бизнес"
    aspect_ratio: Optional[str] = "1:1"
    style: Optional[str] = "photorealistic"


class RAGQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


class RAGIngestRequest(BaseModel):
    documents: List[Dict[str, Any]]


class AchievementBroadcastRequest(BaseModel):
    title: str
    description: str
    metrics: Optional[List[str]] = Field(default_factory=list)
    media_path: Optional[str] = None
    channel: Optional[str] = "@UcustAi"


# -------------------------------------------------------------------
# 2. FastAPI Application Setup
# -------------------------------------------------------------------

orchestrator = MockUnifiedOrchestrator()
queue_manager = MockAsyncGenerationQueueManager(orchestrator=orchestrator)
rag_pipeline = MockCleanRAGPipeline()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await queue_manager.start_worker()
    yield
    await queue_manager.stop_worker()


app = FastAPI(
    title="UCust AI Service Gateway (Mock Replica)",
    description="Автономный, легковесный мок-сервер UCust AI Gateway v2.5.0 для быстрого локального и CI-тестирования бэкенда.",
    version="2.5.0-mock",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for mock photos
mock_output_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_output"))
os.makedirs(os.path.join(mock_output_dir, "photos"), exist_ok=True)
app.mount("/output", StaticFiles(directory=mock_output_dir), name="output")


def check_auth(x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")):
    expected_secret = os.getenv("INTERNAL_API_SECRET", "ucust-super-secret-service-token-2026")
    if x_internal_secret and x_internal_secret != expected_secret:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid internal secret.")


# ============================================================================
# 3. Реестр REST-эндпоинтов (Все 37 маршрутов)
# ============================================================================

# --- 3.1. Unified Orchestrator Gateway (Single Entry Point) ---
@app.post("/api/v1/orchestrator/execute", response_model=OrchestratorTaskResponse, tags=["Unified Orchestrator Gateway"])
@app.post("/api/v1/task/execute", response_model=OrchestratorTaskResponse, tags=["Unified Orchestrator Gateway"])
async def execute_orchestrator_task(
    request: OrchestratorTaskRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    t_start = time.time()
    session_id = request.session_id or f"sess_{uuid.uuid4().hex[:8]}"

    payload = dict(request.payload)
    payload["user_id"] = request.user_id
    payload["session_id"] = session_id

    # Security check
    for k, v in payload.items():
        if isinstance(v, str) and not MockSecurityGuard.check_user_input(v):
            return OrchestratorTaskResponse(
                status="error",
                task_type=request.task_type,
                user_id=request.user_id,
                session_id=session_id,
                data={},
                timings={"total_seconds": round(time.time() - t_start, 3)},
                error=f"Security Violation: обнаружен недопустимый ввод в поле '{k}'"
            )

    result_data = await orchestrator.execute_task(
        task_type=request.task_type,
        user_data=payload,
        session_id=session_id
    )

    # Simulate backend auto-push if callback_url provided
    if request.sync_backend and request.callback_url:
        asyncio.create_task(queue_manager._send_webhook(
            request.callback_url,
            {"task_id": f"task_{uuid.uuid4().hex[:8]}", "user_id": request.user_id, "session_id": session_id, "payload": payload, "result": result_data}
        ))

    return OrchestratorTaskResponse(
        status="success",
        task_type=request.task_type,
        user_id=request.user_id,
        session_id=session_id,
        data=result_data,
        timings=result_data.get("timings", {"total_seconds": round(time.time() - t_start, 3)})
    )


# --- 3.2. Direct Generation Bridge ---
@app.post("/orchestration/generate", tags=["Direct Generation Bridge"])
@app.post("/api/v1/orchestration/generate", tags=["Direct Generation Bridge"])
async def direct_orchestration_generate(
    request: GeneratePostRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    payload = request.model_dump()
    result = await orchestrator.execute_task(task_type="generate_post", user_data=payload, session_id=request.session_id)
    return result


# --- 3.3. Universal Hub Parser ---
@app.post("/api/v1/ai/parse", tags=["Data Collectors & Parsers"])
@app.post("/api/v1/collectors/parse", tags=["Data Collectors & Parsers"])
async def universal_collector_parse(
    request: UniversalCollectorRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    return await orchestrator.execute_task(
        task_type="universal_hub",
        user_data=request.model_dump(),
        session_id=request.session_id
    )


# --- 3.4. Telegram Collector + Vision/OCR ---
@app.post("/api/v1/ai/telegram/analyze", tags=["Data Collectors & Parsers"])
@app.post("/api/v1/collectors/telegram", tags=["Data Collectors & Parsers"])
async def analyze_telegram(
    request: TelegramAnalyzeRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    payload = {"channel": request.channel, "limit": request.limit, "include_media_vqa": request.include_media_vqa}
    return await orchestrator.execute_task(task_type="parse_telegram", user_data=payload, session_id=request.session_id)


# --- 3.5. VK Community Collector ---
@app.post("/api/v1/ai/vk/analyze", tags=["Data Collectors & Parsers"])
@app.post("/api/v1/collectors/vk", tags=["Data Collectors & Parsers"])
async def analyze_vk(
    request: VkAnalyzeRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    payload = {"group_id": request.group_id, "limit": request.limit}
    return await orchestrator.execute_task(task_type="parse_vk", user_data=payload, session_id=request.session_id)


# --- 3.6. Geo Maps Collector (2GIS & Yandex) ---
@app.post("/api/v1/ai/geo/analyze", tags=["Data Collectors & Parsers"])
@app.post("/api/v1/collectors/geo", tags=["Data Collectors & Parsers"])
async def analyze_geo(
    request: GeoAnalyzeRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    payload = {"url": request.url, "provider": request.provider, "limit": request.limit}
    return await orchestrator.execute_task(task_type="parse_geo", user_data=payload, session_id=request.session_id)


# --- 3.7. Website Deep Analyzer ---
@app.post("/api/v1/ai/website/analyze", tags=["Data Collectors & Parsers"])
@app.post("/api/v1/collectors/website", tags=["Data Collectors & Parsers"])
async def analyze_website(
    request: WebsiteAnalyzeRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    payload = {"url": request.url}
    return await orchestrator.execute_task(task_type="parse_website", user_data=payload)


# --- 3.8. Competitor Analyzer ---
@app.post("/api/v1/ai/competitor/analyze", tags=["Data Collectors & Parsers"])
async def analyze_competitor(
    request: CompetitorAnalyzeRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    return {
        "status": "success",
        "competitor_url": request.url,
        "niche": request.niche,
        "swot_matrix": {
            "strengths": ["Широкая известность бренда", "Развитая сеть филиалов"],
            "weaknesses": ["Медленная техподдержка", "Устаревший интерфейс"],
            "opportunities": ["Запуск персонализированных тарифов"],
            "threats": ["Демпинг цен со стороны новых игроков"]
        },
        "counter_strategy": "Сделать фокус на ультра-скорости обслуживания и персонализированном сервисе 24/7."
    }


# --- 3.9. Document Analyzer (PDF, DOCX) ---
@app.post("/api/v1/ai/documents/analyze", tags=["Data Collectors & Parsers"])
@app.post("/api/v1/collectors/analyze-documents", tags=["Data Collectors & Parsers"])
async def analyze_documents(
    payload: Dict[str, Any],
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    return await orchestrator.execute_task(task_type="analyze_documents", user_data=payload)


# --- 3.10. Complex Brand Onboarding ---
@app.post("/api/v1/collectors/analyze-brand", tags=["Data Collectors & Parsers"])
async def analyze_brand(
    payload: Dict[str, Any],
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    return await orchestrator.execute_task(task_type="analyze_brand", user_data=payload)


# --- 3.11. Quick Vision Analyzer ---
@app.post("/api/v1/vision/quick-analyze", tags=["Data Collectors & Parsers"])
async def quick_analyze_vision(
    payload: Dict[str, Any],
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    return {
        "status": "success",
        "detected_objects": ["продукт", "стильный интерьер", "акцентное освещение"],
        "dominant_colors": ["#4A2E18", "#E8D8C8"],
        "ocr_text": "PREMIUM QUALITY 2026",
        "quality_score": 9.5
    }


# --- 3.12. Image Generation ---
@app.post("/api/v1/ai/generate-image", tags=["Marketing & Content Generation"])
async def generate_image(
    request: ImageGenerateRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    return await orchestrator.execute_task(task_type="generate_image", user_data=request.model_dump())


# --- 3.13. Strategy Generation ---
@app.post("/api/v1/ai/strategy/generate", tags=["Marketing & Content Generation"])
async def generate_strategy(
    request: StrategyGenerateRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    return await orchestrator.execute_task(task_type="generate_strategy", user_data=request.model_dump())


# --- 3.14. Charlie Munger Critic ---
@app.post("/api/v1/ai/critic/review", tags=["Marketing & Content Generation"])
async def review_critic(
    request: CriticReviewRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    return await orchestrator.execute_task(task_type="critic_review", user_data=request.model_dump())


# --- 3.15. Trends & Memes ---
@app.get("/api/v1/ai/trends", tags=["Marketing & Content Generation"])
async def get_trends(
    niche: Optional[str] = Query("Бизнес", description="Ниша бизнеса")
):
    return {
        "status": "success",
        "niche": niche,
        "trends": [
            {"id": "trend_2026_01", "name": "AI Automation Speedrun", "viral_score": 9.8, "template": "Как делать за 1 день то, что раньше делали за месяц"},
            {"id": "trend_2026_02", "name": "Clean Aesthetic Craft", "viral_score": 9.4, "template": "Эстетика минимализма и прозрачности процессов"}
        ],
        "cached": True
    }


# --- 3.15.1. Platform Tariffs & Capabilities Matrix ---
PLATFORM_TARIFFS = {
    "START": {
        "tier_name": "START",
        "title": "Базовый Старт (Малый бизнес / Эксперты)",
        "monthly_post_limit": 12,
        "posts_per_week": 3,
        "allowed_days_of_week": [0, 2, 4],  # Пн, Ср, Пт
        "allowed_weekdays_ru": ["Понедельник", "Среда", "Пятница"],
        "media_capabilities": {
            "studio_photo_comfyui": True,
            "aspect_ratios": ["1:1"],
            "vlm_moondream_ocr": False,
            "video_generation_ltx23": False,
            "clean_rag_knowledge_base": False,
            "charlie_munger_critic_strictness": 0.80,
            "multi_variations_count": 1,
            "supported_channels": ["telegram"]
        },
        "queue_priority": "STANDARD",
        "description": "12 публикаций в месяц (3 раза в неделю) со студийными фото и текстами по фреймворкам."
    },
    "BUSINESS": {
        "tier_name": "BUSINESS",
        "title": "Бизнес Стандарт (Оптимальный для большинства ниш)",
        "monthly_post_limit": 20,
        "posts_per_week": 5,
        "allowed_days_of_week": [0, 1, 2, 3, 4],  # Пн-Пт
        "allowed_weekdays_ru": ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"],
        "media_capabilities": {
            "studio_photo_comfyui": True,
            "aspect_ratios": ["1:1", "9:16", "16:9"],
            "vlm_moondream_ocr": True,
            "video_generation_ltx23": False,
            "clean_rag_knowledge_base": True,
            "charlie_munger_critic_strictness": 0.90,
            "multi_variations_count": 4,
            "supported_channels": ["telegram", "vk", "website"]
        },
        "queue_priority": "HIGH",
        "description": "20 публикаций в месяц (каждый будний день) с VLM-анализом, RAG-базой знаний и 4 ракурсами воронки."
    },
    "ENTERPRISE": {
        "tier_name": "ENTERPRISE",
        "title": "Корпоративный Премиум (Флагманские бренды и сети)",
        "monthly_post_limit": 30,
        "posts_per_week": 7,
        "allowed_days_of_week": [0, 1, 2, 3, 4, 5, 6],  # Каждый день 24/7
        "allowed_weekdays_ru": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        "media_capabilities": {
            "studio_photo_comfyui": True,
            "aspect_ratios": ["1:1", "9:16", "16:9", "4:5"],
            "vlm_moondream_ocr": True,
            "video_generation_ltx23": True,
            "clean_rag_knowledge_base": True,
            "charlie_munger_critic_strictness": 0.95,
            "multi_variations_count": 8,
            "supported_channels": ["telegram", "vk", "instagram", "ok", "max", "website"]
        },
        "queue_priority": "DEDICATED_REALTIME",
        "description": "30+ публикаций в месяц (ежедневно), SWOT-анализ конкурентов, мульти-канальность и выделенный GPU-воркер."
    },
    "CUSTOM": {
        "tier_name": "CUSTOM",
        "title": "Индивидуальный план",
        "monthly_post_limit": 50,
        "posts_per_week": 7,
        "allowed_days_of_week": [0, 1, 2, 3, 4, 5, 6],
        "allowed_weekdays_ru": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        "media_capabilities": {
            "studio_photo_comfyui": True,
            "aspect_ratios": ["1:1", "9:16", "16:9", "4:5"],
            "vlm_moondream_ocr": True,
            "video_generation_ltx23": True,
            "clean_rag_knowledge_base": True,
            "charlie_munger_critic_strictness": 0.95,
            "multi_variations_count": 10,
            "supported_channels": ["all"]
        },
        "queue_priority": "DEDICATED_REALTIME",
        "description": "Персональные настройки частоты, форматов и выделенные мощности."
    }
}


@app.get("/api/v1/ai/tariffs", tags=["Tariffs & Quotas"])
@app.get("/api/v1/tariffs", tags=["Tariffs & Quotas"])
async def get_tariffs():
    return {
        "status": "success",
        "tariffs": PLATFORM_TARIFFS,
        "default_tier": "BUSINESS"
    }


@app.get("/api/v1/ai/clients/{client_id}/subscription-quota", tags=["Tariffs & Quotas"])
@app.get("/api/v1/subscription/quota", tags=["Tariffs & Quotas"])
async def get_client_subscription_quota(
    client_id: str = "default_client",
    tier: Optional[str] = Query(None, description="Опциональный тариф (START, BUSINESS, ENTERPRISE, CUSTOM)")
):
    tier_key = (tier or "BUSINESS").upper()
    tier_info = PLATFORM_TARIFFS.get(tier_key, PLATFORM_TARIFFS["BUSINESS"])

    import datetime as dt
    now = dt.datetime.now()
    slots = []
    current_day = now
    allowed_days = set(tier_info["allowed_days_of_week"])
    
    post_count = 0
    while len(slots) < tier_info["monthly_post_limit"] and (current_day - now).days < 35:
        if current_day.weekday() in allowed_days:
            post_count += 1
            slots.append({
                "slot_index": post_count,
                "date": current_day.strftime("%Y-%m-%d"),
                "time": "10:00" if post_count % 2 == 1 else "14:30",
                "weekday": current_day.strftime("%A"),
                "post_type": "PHOTO_AND_TEXT" if post_count % 5 != 0 else "ENGAGING_TEXT"
            })
        current_day += dt.timedelta(days=1)

    return {
        "status": "success",
        "client_id": client_id,
        "tier": tier_info,
        "subscription_status": "ACTIVE",
        "monthly_post_limit": tier_info["monthly_post_limit"],
        "remaining_quota": tier_info["monthly_post_limit"],
        "calendar_slots_count": len(slots),
        "calendar_slots": slots
    }


# --- 3.16. Async FIFO Queue ---
@app.post("/api/v1/ai/tasks/async-generate", status_code=status.HTTP_202_ACCEPTED, tags=["Async Task Queue"])
async def create_async_task(
    request: AsyncGenerateTaskRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    task_id = await queue_manager.enqueue(request.model_dump())
    return {
        "status": "accepted",
        "task_id": task_id,
        "message": "Задача успешно поставлена в очередь генерации.",
        "poll_status_url": f"/api/v1/ai/tasks/{task_id}/status"
    }


@app.get("/api/v1/ai/tasks/{task_id}/status", tags=["Async Task Queue"])
async def get_task_status(task_id: str):
    res = queue_manager.get_task_status(task_id)
    if not res:
        raise HTTPException(status_code=404, detail="Task not found")
    return res


# --- 3.17. Clean RAG ---
@app.post("/api/v1/ai/rag/query", tags=["Clean RAG Knowledge Base"])
async def rag_query(request: RAGQueryRequest):
    return await rag_pipeline.query(request.query, top_k=request.top_k or 5)


@app.post("/api/v1/ai/rag/ingest", tags=["Clean RAG Knowledge Base"])
async def rag_ingest(request: RAGIngestRequest):
    return await rag_pipeline.ingest(request.documents)


# --- 3.18. Social Broadcast & Publisher ---
@app.post("/api/v1/ai/broadcast/achievement", tags=["Publishers & Broadcast"])
async def broadcast_achievement(
    request: AchievementBroadcastRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    return {
        "status": "success",
        "message": f"Достижение '{request.title}' успешно отправлено в канал {request.channel}",
        "published_at": time.time()
    }


@app.post("/api/v1/ai/publish", tags=["Publishers & Broadcast"])
async def publish_post(
    payload: Dict[str, Any],
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    check_auth(x_internal_secret)
    return {
        "status": "success",
        "post_id": f"pub_{uuid.uuid4().hex[:6]}",
        "platforms": payload.get("platforms", ["telegram"]),
        "published": True
    }


# --- 3.19. Health & Diagnostic Endpoints ---
@app.get("/api/v1/ai/health", tags=["Health & Diagnostics"])
@app.get("/health", tags=["Health & Diagnostics"])
@app.get("/", tags=["Health & Diagnostics"])
async def health_check():
    return {
        "status": "healthy",
        "service": "UCust AI Service Gateway (Mock Replica)",
        "version": "2.5.0-mock",
        "gpu_mode": "MOCK_CPU_FAST",
        "timestamp": time.time(),
        "models": {
            "llm": "mock-saiga-nemo-12b",
            "vlm": "mock-moondream2",
            "ocr": "mock-paddleocr",
            "comfyui": "mock-headless-client"
        }
    }


# --- 3.20. Real-Time WebSocket Session Streamer ---
@app.websocket("/ws/ai/session/{session_id}")
async def websocket_session_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        steps = [
            {"step": "init", "message": "Подключение к сессии установлено", "progress": 10},
            {"step": "vision", "message": "Анализ медиа и визуального стиля...", "progress": 35},
            {"step": "llm_draft", "message": "Генерация текста по фреймворку PAS...", "progress": 65},
            {"step": "critic", "message": "Инверсионный аудит Чарли Мангера (скор: 9.6)...", "progress": 85},
            {"step": "final", "message": "Контент готов к публикации", "progress": 100}
        ]
        for s in steps:
            await asyncio.sleep(0.15)
            await websocket.send_json({
                "session_id": session_id,
                "timestamp": time.time(),
                **s
            })
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Mock Echo: {data}")
    except WebSocketDisconnect:
        pass
