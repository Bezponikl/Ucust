"""
AI Service Gateway (FastAPI)
Единый шлюз подключения ИИ-агентов UCust к Бэкенду и Фронтенду.
Предоставляет REST API и WebSockets для real-time онбординга.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from fastapi.staticfiles import StaticFiles
import os

from storage.db import DatabaseFactory
from core.orchestrator import UnifiedOrchestrator, SecurityGuard
from rag.pipeline import CleanRAGPipeline
from rag.models import Document

# -------------------------------------------------------------------
# 1. Pydantic Модели запросов и ответов (API Contract v2.5.0)
# -------------------------------------------------------------------

class OrchestratorTaskRequest(BaseModel):
    task_type: str = Field(
        ...,
        example="generate_post",
        description="Тип задачи: 'generate_post', 'quick_vision', 'analyze_documents', 'quick_scan', 'onboard_user', 'plan_content', 'feedback_loop', 'rag_query', 'rag_ingest'"
    )
    user_id: str = Field("default_user", example="usr_94812", description="Идентификатор пользователя")
    session_id: Optional[str] = Field(None, example="sess_abc123", description="ID сессии диалога / трейса")
    callback_url: Optional[str] = Field(None, example="http://10.0.0.1:8080/api/v1/ai/callback", description="Динамический URL вебхука для авто-пуша")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Полезная нагрузка (параметры, ссылки, фото, тексты)")
    sync_backend: bool = Field(default=True, description="Флаг авто-пуша результата в бэкенд")


class OrchestratorTaskResponse(BaseModel):
    status: str = Field(..., example="success", description="'success' или 'error'")
    task_type: str
    user_id: str
    session_id: str
    data: Dict[str, Any] = Field(default_factory=dict)
    timings: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class TaskRequest(BaseModel):
    user_id: str = Field("default_user", example="usr_94812", description="Идентификатор пользователя")
    session_id: Optional[str] = Field(None, example="sess_abc123", description="ID сессии диалога")
    task_type: str = Field(..., example="generate_post", description="Тип задачи: generate_post | generate_image | prepare_holiday_greeting | get_trends | rag_query")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Параметры задачи")


class TaskResponse(BaseModel):
    status: str = Field(..., example="success")
    task_id: str = Field(..., example="task_38df92a")
    session_id: str = Field(..., example="sess_abc123")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TrendResponse(BaseModel):
    status: str = "success"
    niche: str
    trends: Any
    cached: bool = True


class ImageGenerateRequest(BaseModel):
    prompt: str = Field(..., example="Сезонный тыквенный латте с корицей и круассан")
    niche: str = Field("Кофейня", example="Кофейня")
    aspect_ratio: str = Field("1:1", example="1:1")
    style: str = Field("photorealistic", example="photorealistic")
class RAGQueryRequest(BaseModel):
    query: str = Field(..., example="Сколько стоит тариф Pro?")
    top_k: int = Field(5, ge=1, le=20)


class RAGIngestRequest(BaseModel):
    documents: List[Dict[str, Any]] = Field(..., description="Список документов для базы знаний")


class VisionAnalyzeRequest(BaseModel):
    image: Optional[str] = Field(None, description="Base64 DataUrl или путь к изображению")
    attachments: Optional[List[Dict[str, Any]]] = Field(None, description="Список вложений")
    topic: Optional[str] = Field("", example="Летний фестиваль напитков")
    company_name: Optional[str] = Field("UCust", example="UCust")


class WebsiteAnalyzeRequest(BaseModel):
    url: str = Field(..., example="https://ucust.ai", description="URL веб-сайта компании для парсинга и анализа")


class CompetitorAnalyzeRequest(BaseModel):
    url: str = Field(..., example="https://competitor.com", description="URL сайта конкурента для декомпозиции")
    niche: Optional[str] = Field("Бизнес", example="Автосервис", description="Ниша вашей компании")


class StrategyGenerateRequest(BaseModel):
    company_name: Optional[str] = Field("UCust", example="UCust")
    niche: str = Field(..., example="IT Автоматизация")
    target_audience: Optional[str] = Field("", example="Предприниматели 25-45 лет")
    usp: Optional[str] = Field("", example="Автономный маркетинг за 1 день")


class CriticReviewRequest(BaseModel):
    text: str = Field(..., description="Текст поста или оффера для инверсионного аудита Чарли Мангера")
    topic: Optional[str] = Field("", description="Тема поста")
    niche: Optional[str] = Field("", description="Целевая ниша")
    strictness: Optional[float] = Field(0.85, description="Строгость критика (0.5 - мягкая, 0.95 - жесткая)")


class AchievementBroadcastRequest(BaseModel):
    title: str = Field(..., example="Релиз автономного SMM-пайплайна 2.0", description="Заголовок достижения")
    description: str = Field(..., example="Команда ИИ-агентов UCust завершила интеграцию критика и LTX-2.", description="Описание достижения")
    metrics: Optional[List[str]] = Field(default_factory=list, example=["Скорость: 60 сек", "Качество: 98%"], description="Ключевые показатели")
    media_path: Optional[str] = Field(None, description="Путь к фото или видео")
    channel: Optional[str] = Field("@UcustAi", example="@UcustAi", description="Целевой Telegram-канал")


class ProjectContext(BaseModel):
    id: Optional[str] = Field(None, description="ID проекта")
    projectId: Optional[str] = Field(None, description="ID проекта (алиас)")
    name: Optional[str] = Field(None, description="Название бренда/компании")
    companyName: Optional[str] = Field(None, description="Название бренда (алиас)")
    industry: Optional[str] = Field(None, description="Индустрия / сфера деятельности")
    niche: Optional[str] = Field(None, description="Ниша бизнеса (алиас)")
    city: Optional[str] = Field("Москва", description="Город присутствия")
    description: Optional[str] = Field(None, description="Описание бизнеса и ключевое позиционирование")
    targetAudience: Optional[str] = Field(None, description="Описание целевой аудитории")
    toneOfVoice: Optional[str] = Field("FRIENDLY", description="Тон коммуникации (FRIENDLY, BOLD, EXPERT, FORMAL)")
    socialLinks: Optional[Dict[str, Any]] = Field(None, description="Ссылки на соцсети (telegram, instagram, vk, website)")
    businessHours: Optional[Dict[str, Any]] = Field(None, description="График работы и выходные дни")
    ownerId: Optional[str] = Field(None, description="ID владельца")
    logoUrl: Optional[str] = Field(None, description="URL логотипа бренда")
    brandColors: Optional[List[str]] = Field(None, description="Фирменные цвета (Hex)")
    usp: Optional[str] = Field(None, description="Уникальное торговое предложение")


class GeneratePostRequest(BaseModel):
    projectId: Optional[str] = Field(None, description="ID проекта")
    project_id: Optional[str] = Field(None, description="ID проекта")
    prompt: Optional[str] = Field(None, description="Промпт или тема публикации")
    topic: Optional[str] = Field(None, description="Тема публикации (алиас)")
    companyName: Optional[str] = Field(None, description="Название компании")
    company_name: Optional[str] = Field(None, description="Название компании (алиас)")
    niche: Optional[str] = Field(None, description="Ниша бизнеса")
    attachments: Optional[List[Any]] = Field(default_factory=list, description="Медиа-вложения (фото, референсы)")
    promoCode: Optional[str] = Field(None, description="Промокод / специальное предложение")
    promo_code: Optional[str] = Field(None, description="Промокод (алиас)")
    projectContext: Optional[ProjectContext] = Field(None, description="Полный объект проекта")
    project_context: Optional[ProjectContext] = Field(None, description="Полный объект проекта (алиас)")
    tone: Optional[str] = Field(None, description="Тон коммуникации")
    aspect_ratio: Optional[str] = Field("1:1", description="Соотношение сторон (1:1, 9:16, 16:9)")
    callback_url: Optional[str] = Field(None, description="URL для Push-коллбека")
    user_id: Optional[str] = Field("default_user", description="ID пользователя")
    session_id: Optional[str] = Field(None, description="ID сессии")
    generate_image: bool = Field(True, description="Флаг генерации визуального контента")


class AsyncGenerateTaskRequest(BaseModel):
    topic: str = Field(..., description="Тема или промпт поста")
    company_name: Optional[str] = Field("UCust", description="Название компании")
    niche: Optional[str] = Field("Бизнес", description="Ниша")
    tone: Optional[str] = Field("Дерзкий, уверенный, вдохновляющий", description="Тон общения")
    aspect_ratio: Optional[str] = Field("9:16", description="Формат соотношения сторон (1:1, 4:5, 9:16, 16:9)")
    variation_index: Optional[int] = Field(0, description="Индекс ракурса/вариации (0, 1, 2, 3...)")
    stage: Optional[str] = Field("problem_aware", description="Ступень воронки Ханта")
    framework: Optional[str] = Field(None, description="PAS | AIDA | StoryBrand | BAB")
    trigger: Optional[str] = Field(None, description="Триггер Чалдини")
    tier: Optional[str] = Field("BUSINESS", description="Тариф медиа-оснащения")
    custom_prompt: Optional[str] = Field(None, description="Пользовательский визуальный промпт")
    attachments: Optional[List[Dict[str, Any]]] = Field(None, description="Вложения для анализа и генерации")
    callback_url: Optional[str] = Field(None, description="URL для отправки результата (Push-коллбек)")
    task_id: Optional[str] = Field(None, description="Опциональный внешний task_id")
    user_id: Optional[str] = Field("default_user", description="ID пользователя")
    session_id: Optional[str] = Field(None, description="ID сессии")
    projectContext: Optional[ProjectContext] = Field(None, description="Полный контекст проекта")
    project_context: Optional[ProjectContext] = Field(None, description="Полный контекст проекта (алиас)")



# -------------------------------------------------------------------
# 2. Инициализация FastAPI приложения
# -------------------------------------------------------------------

from contextlib import asynccontextmanager
from core.queue_manager import AsyncGenerationQueueManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Старт фонового GPU-воркера очереди при запуске приложения
    await queue_manager.start_worker()
    yield
    # Остановка воркера при выключении
    await queue_manager.stop_worker()

app = FastAPI(
    title="UCust AI Service Gateway",
    description="Единая точка входа для бэкенда и фронтенда к команде автономных ИИ-агентов UCust.",
    version="2.5.0",
    lifespan=lifespan
)

# Разрешаем CORS для любых фронтендов (React, Next.js, Vue, Mobile)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Раздача сгенерированных фото и медиа файлов
output_static_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "output"))
os.makedirs(os.path.join(output_static_dir, "photos"), exist_ok=True)
app.mount("/output", StaticFiles(directory=output_static_dir), name="output")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from storage.models import Base

db_engine = create_engine("sqlite:///./ai_smm_dev.db", echo=False)
Base.metadata.create_all(bind=db_engine)
SessionLocal = sessionmaker(bind=db_engine)
db_session = SessionLocal()
orchestrator = UnifiedOrchestrator(db_session=db_session)
rag_pipeline = CleanRAGPipeline(min_confidence_threshold=0.65)
queue_manager = AsyncGenerationQueueManager(orchestrator=orchestrator)


# ============================================================================
# ЕДИНЫЙ КОМАНДНЫЙ ШЛЮЗ ОРКЕСТРАТОРА (v2.5.0 WIREGUARD HTTP REST)
# ============================================================================

@app.post("/api/v1/orchestrator/execute", response_model=OrchestratorTaskResponse, tags=["Unified Orchestrator Gateway"])
@app.post("/api/v1/task/execute", response_model=OrchestratorTaskResponse, tags=["Unified Orchestrator Gateway"])
async def execute_orchestrator_task(
    request: OrchestratorTaskRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret"),
) -> OrchestratorTaskResponse:
    """
    ЕДИНЫЙ КОМАНДНЫЙ ШЛЮЗ ОРКЕСТРАТОРА ДЛЯ БЭКЕНДА (v2.5.0):
    - Принимает любую задачу ('generate_post', 'quick_vision', 'onboard_user', 'analyze_documents', 'quick_scan', 'plan_content', 'feedback_loop', 'rag_query', 'rag_ingest').
    - Проводит централизованную валидацию безопасности (SSRF, Injections, Secret).
    - Выполняет оркестровку через UnifiedOrchestrator.
    - Автоматически синхронизирует результат с основным бэкендом (HTTP Push Webhook) при sync_backend=True.
    """
    import time

    # 1. Проверка внутреннего секрета доступа
    expected_secret = os.getenv("INTERNAL_API_SECRET", "ucust-super-secret-service-token-2026")
    if x_internal_secret and x_internal_secret != expected_secret:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid internal secret.")

    t_start = time.time()
    session_id = request.session_id or f"sess_{int(time.time()*1000)}"

    # 2. Обогащение payload системными метаданными
    task_payload = dict(request.payload)
    task_payload["user_id"] = request.user_id
    task_payload["session_id"] = session_id

    # 3. Безопасность ввода
    for k, v in task_payload.items():
        if isinstance(v, str) and not SecurityGuard.check_user_input(v):
            return OrchestratorTaskResponse(
                status="error",
                task_type=request.task_type,
                user_id=request.user_id,
                session_id=session_id,
                data={},
                timings={"total_seconds": round(time.time() - t_start, 3)},
                error=f"Security Violation: обнаружен недопустимый ввод в поле '{k}'"
            )

    try:
        result_data = await orchestrator.execute_task(
            task_type=request.task_type,
            user_data=task_payload,
            session_id=session_id
        )

        total_sec = round(time.time() - t_start, 3)
        timings = result_data.get("timings") if isinstance(result_data, dict) else {}
        if isinstance(timings, dict):
            timings["gateway_total_seconds"] = total_sec

        # 4. Фоновый Auto-Push в бэкенд (динамический callback_url или глобальный из .env)
        if request.sync_backend:
            backend_cb = request.callback_url or os.getenv("BACKEND_COLLECTOR_CALLBACK_URL") or os.getenv("JAVA_BACKEND_CALLBACK_URL")
            if backend_cb:
                async def _push_bg():
                    try:
                        import aiohttp
                        async with aiohttp.ClientSession() as s:
                            headers = {"X-Internal-Secret": expected_secret, "Content-Type": "application/json"}
                            body = {
                                "user_id": request.user_id,
                                "session_id": session_id,
                                "task_type": request.task_type,
                                "status": result_data.get("status", "success"),
                                "result": result_data,
                                "timestamp": time.time()
                            }
                            await s.post(backend_cb, json=body, headers=headers, timeout=aiohttp.ClientTimeout(total=5))
                    except Exception:
                        pass
                asyncio.create_task(_push_bg())

        return OrchestratorTaskResponse(
            status="success" if result_data.get("status") != "error" else "error",
            task_type=request.task_type,
            user_id=request.user_id,
            session_id=session_id,
            data=result_data,
            timings=timings if isinstance(timings, dict) else {"total_seconds": total_sec}
        )
    except Exception as exc:
        return OrchestratorTaskResponse(
            status="error",
            task_type=request.task_type,
            user_id=request.user_id,
            session_id=session_id,
            data={},
            timings={"total_seconds": round(time.time() - t_start, 3)},
            error=str(exc)
        )


# -------------------------------------------------------------------
# 3. REST API Эндпоинты
# -------------------------------------------------------------------

@app.post("/orchestration/generate", tags=["Direct Generation Bridge"])
@app.post("/api/v1/orchestration/generate", tags=["Direct Generation Bridge"])
async def direct_orchestration_generate(
    request: GeneratePostRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret"),
):
    """
    ⚡ ПРЯМОЙ ЭНДПОИНТ ГЕНЕРАЦИИ КОНТЕНТА ДЛЯ БЭКЕНДА (с поддержкой ProjectContext):
    - Принимает как минимальные параметры (prompt, attachments, promoCode),
      так и полный объект проекта (city, toneOfVoice, targetAudience, businessHours, logoUrl, socialLinks).
    - Автоматически обогащает контекст для Saiga LLM, Moondream2 и ComfyUI.
    - Выполняет сквозную оркестровку и возвращает структурированный результат.
    """
    expected_secret = os.getenv("INTERNAL_API_SECRET", "ucust-super-secret-service-token-2026")
    if x_internal_secret and x_internal_secret != expected_secret:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid internal secret.")

    session_id = request.session_id or f"sess_{uuid.uuid4().hex[:8]}"

    # 1. Базовый payload
    task_payload: Dict[str, Any] = {
        "prompt": request.prompt or request.topic or "",
        "topic": request.prompt or request.topic or "",
        "company_name": request.companyName or request.company_name or "UCust",
        "niche": request.niche or "Бизнес",
        "attachments": request.attachments or [],
        "promo_code": request.promoCode or request.promo_code,
        "offer": request.promoCode or request.promo_code,
        "aspect_ratio": request.aspect_ratio or "1:1",
        "generate_image": request.generate_image,
        "tone": request.tone or "Естественный и живой",
        "user_id": request.user_id or "default_user",
        "session_id": session_id,
        "project_id": request.projectId or request.project_id
    }

    # 2. Обогащение данными из ProjectContext
    proj = request.projectContext or request.project_context
    if proj:
        proj_dict = proj.dict(exclude_none=True)
        task_payload["project_context"] = proj_dict
        task_payload["project"] = proj_dict
        if proj.name or proj.companyName:
            task_payload["company_name"] = proj.name or proj.companyName
        if proj.industry or proj.niche:
            task_payload["niche"] = proj.industry or proj.niche
        if proj.city:
            task_payload["city"] = proj.city
        if proj.description:
            task_payload["description"] = proj.description
            task_payload["usp"] = proj.description
        if proj.targetAudience:
            task_payload["target_audience"] = proj.targetAudience
        if proj.toneOfVoice:
            task_payload["tone"] = proj.toneOfVoice
            task_payload["tone_of_voice"] = proj.toneOfVoice
        if proj.socialLinks:
            task_payload["social_links"] = proj.socialLinks
        if proj.businessHours:
            task_payload["business_hours"] = proj.businessHours
        if proj.logoUrl:
            task_payload["logo_url"] = proj.logoUrl
        if proj.brandColors:
            task_payload["brand_colors"] = proj.brandColors
        if proj.id or proj.projectId:
            task_payload["project_id"] = proj.id or proj.projectId

    # 3. Валидация безопасности
    payload_str = json.dumps(task_payload, ensure_ascii=False)
    if not SecurityGuard.check_user_input(payload_str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security Violation: обнаружен недопустимый ввод в запросе."
        )

    # 4. Запуск генерации через Orchestrator
    result = await orchestrator.execute_task(
        task_type="generate_post",
        user_data=task_payload,
        session_id=session_id
    )

    return {
        "status": "success" if result.get("status") != "error" else "error",
        "session_id": session_id,
        "project_id": task_payload.get("project_id"),
        "data": result
    }


@app.get("/api/v1/ai/health", tags=["System"])

@app.get("/health", tags=["System"])
@app.get("/", tags=["System"])
async def health_check():
    """Проверка доступности ИИ-шлюза и агентов."""
    return {
        "status": "healthy",
        "service": "UCust AI Service Gateway",
        "version": "2.5.0",
        "routes": {
            "unified_orchestrator": "/api/v1/orchestrator/execute",
            "async_queue": "/api/v1/ai/tasks/async-generate",
            "health": "/api/v1/ai/health"
        },
        "agents": ["Interviewer", "Analyst", "Saiga Copywriter", "Visual Director LTX-2", "ToV Gatekeeper", "UnifiedOrchestrator"],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/ai/tasks/async-generate", status_code=status.HTTP_202_ACCEPTED, tags=["Async Generation Queue"])
async def submit_async_generation_task(request: AsyncGenerateTaskRequest):
    """
    ⚡ Асинхронный запуск генерации с гарантией FIFO-очереди и Push-коллбеком на Java-бэкенд.
    Мгновенно отвечает кодом 202 Accepted, резервирует позицию в очереди и начинает обработку.
    """
    payload = request.dict(exclude={"callback_url", "task_id", "user_id", "session_id"})
    payload["task_type"] = "generate_post"

    # Проверка безопасности
    payload_str = json.dumps(payload, ensure_ascii=False)
    if not SecurityGuard.check_user_input(payload_str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security Violation: обнаружен запрещенный запрос или попытка инъекции."
        )

    task_info = await queue_manager.enqueue_task(
        payload=payload,
        callback_url=request.callback_url,
        task_id=request.task_id,
        user_id=request.user_id or "default_user",
        session_id=request.session_id
    )
    return task_info


@app.get("/api/v1/ai/tasks/{task_id}/status", tags=["Async Generation Queue"])
async def get_async_task_status(task_id: str):
    """
    Получение текущего статуса задачи (QUEUED, PROCESSING, COMPLETED, FAILED, PUSHED)
    и позиции в очереди.
    """
    task_status = queue_manager.get_task_status(task_id)
    if not task_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача '{task_id}' не найдена в реестре очереди."
        )
    return {
        "status": "success",
        "task": task_status
    }


@app.get("/api/v1/ai/queue/stats", tags=["Async Generation Queue"])
async def get_generation_queue_stats():
    """
    Мониторинг состояния очереди и загруженности GPU.
    """
    return queue_manager.get_queue_stats()


@app.post("/api/v1/ai/task", response_model=TaskResponse, tags=["AI Tasks"])
async def execute_ai_task(request: TaskRequest):
    """
    Универсальный эндпоинт выполнения задач агентами.
    Бэкенд передает task_type и payload, Оркестратор распределяет нагрузку.
    """
    session_id = request.session_id or f"sess_{uuid.uuid4().hex[:8]}"
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    
    # 1. Проверка безопасности входящих данных
    payload_str = json.dumps(request.payload, ensure_ascii=False)
    if not SecurityGuard.check_user_input(payload_str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security Violation: обнаружен запрещенный запрос или попытка инъекции."
        )

    # 2. Передача в UnifiedOrchestrator
    try:
        result = await orchestrator.execute_task(
            task_type=request.task_type,
            user_data=request.payload,
            session_id=session_id
        )
        
        if result.get("status") == "error":
            return TaskResponse(
                status="error",
                task_id=task_id,
                session_id=session_id,
                error=result.get("message", "Ошибка выполнения задачи")
            )
            
        return TaskResponse(
            status="success",
            task_id=task_id,
            session_id=session_id,
            data=result
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка оркестратора: {str(e)}"
        )


@app.get("/api/v1/ai/trends", response_model=TrendResponse, tags=["Trends & Analytics"])
async def get_weekly_trends(niche: str = Query("IT и Автоматизация", description="Ниша бизнеса")):
    """
    Отдача закешированных недельных трендов из Redis за 3-5 миллисекунд.
    """
    session_id = f"trend_req_{uuid.uuid4().hex[:6]}"
    result = await orchestrator.execute_task(
        task_type="get_trends",
        user_data={"niche": niche},
        session_id=session_id
    )
    
    return TrendResponse(
        niche=niche,
        trends=result.get("trends", ""),
        cached=True
    )


@app.get("/api/v1/ai/analytics/graphs", tags=["Trends & Analytics"])
async def get_frontend_graphs():
    """
    Безопасные агрегированные данные для графиков и дашбордов фронтенда (без PII).
    """
    graphs_data = orchestrator.get_frontend_graph_data()
    return {
        "status": "success",
        "data": graphs_data
    }


@app.post("/api/v1/ai/generate-image", tags=["Visual & Media"])
async def generate_smm_image(request: ImageGenerateRequest):
    """
    Генерация качественного SMM-изображения для постов, баннеров и сторис.
    """
    result = await orchestrator.execute_task(
        task_type="generate_image",
        user_data=request.dict(),
        session_id=f"img_{uuid.uuid4().hex[:8]}"
    )
    return result


@app.post("/api/v1/ai/vision/analyze", tags=["Visual & Media"])
async def analyze_visual_media(request: VisionAnalyzeRequest):
    """
    Анализ загруженного фото через ИИ-аналитика Moondream2.
    Извлекает доминирующие цвета, ключевые объекты, композицию и готовит промпт.
    """
    from skills.moondream_vqa import MoondreamVQASkill
    moondream = MoondreamVQASkill()
    
    if request.attachments:
        result = moondream.analyze_attachments_batch(
            attachments=request.attachments,
            topic=request.topic or "",
            company_name=request.company_name or "UCust"
        )
    elif request.image:
        result = moondream.extract_visual_dossier(
            image_input=request.image,
            topic=request.topic or "",
            company_name=request.company_name or "UCust"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не передано изображение или список вложений для анализа."
        )
        
    return {
        "status": "success",
        "vision_analyst": "Moondream2",
        "data": result
    }


@app.post("/api/v1/ai/website/analyze", tags=["Web & Social Intelligence"])
async def analyze_website(request: WebsiteAnalyzeRequest):
    """
    Глубокий парсинг и ИИ-анализ веб-сайта компании (B2B, e-commerce, лендинги).
    Извлекает УТП, заголовки, описание услуг, контакты, соцсети и готовит контекст для LLM.
    """
    from collectors.website_collector import WebsiteCollector
    collector = WebsiteCollector()
    result = await collector.collect_website_async(request.url)
    
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Не удалось распарсить сайт: {result.get('error')}"
        )
        
    return {
        "status": "success",
        "analyst": "WebsiteCollector",
        "data": result
    }


@app.post("/api/v1/ai/competitor/analyze", tags=["Web & Social Intelligence"])
async def analyze_competitor(request: CompetitorAnalyzeRequest):
    """
    Глубокая декомпозиция конкурента (Strengths, Weaknesses, Pricing, UVP)
    и генерация контр-стратегии отстройки для SMM.
    """
    from skills.competitive_intel import CompetitiveIntelSkill
    intel = CompetitiveIntelSkill()
    result = await intel.analyze_competitor_async(request.url, my_company_niche=request.niche)
    
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка анализа конкурента: {result.get('error')}"
        )
        
    return {
        "status": "success",
        "analyst": "CompetitiveIntelSkill",
        "data": result
    }


@app.post("/api/v1/ai/strategy/generate", tags=["Content Strategy & Personas"])
async def generate_content_strategy(request: StrategyGenerateRequest):
    """
    Генерация воронки контента (TOFU / MOFU / BOFU), арсенала виральных хуков
    и глубокого портрета покупателя (Jobs-to-be-Done, Pains, Triggers).
    """
    from skills.content_strategy_engine import ContentStrategyEngine
    engine = ContentStrategyEngine()
    result = engine.generate_strategy(
        company_name=request.company_name or "UCust",
        niche=request.niche,
        target_audience=request.target_audience or "",
        key_usp=request.usp or ""
    )
    return {
        "status": "success",
        "strategist": "ContentStrategyEngine",
        "data": result
    }


@app.post("/api/v1/ai/critic/review", tags=["Content Quality & Pre-Mortem"])
async def review_content_with_critic(request: CriticReviewRequest):
    """
    Инверсионный Pre-Mortem аудит текста (методология Чарли Мангера):
    выявление клише, скучных хуков, отсутствия CTA и генерация правок для автора.
    """
    from skills.critic_munger import CriticMungerSkill
    critic = CriticMungerSkill(strictness=request.strictness or 0.85)
    result = critic.review_content(
        text=request.text,
        topic=request.topic or "",
        target_audience=request.niche or ""
    )
    return {
        "status": "success",
        "critic": "Charlie Munger Pre-Mortem Agent",
        "data": result
    }


@app.post("/api/v1/ai/achievements/post", tags=["Telegram Achievement Broadcaster"])
async def broadcast_achievement_endpoint(request: AchievementBroadcastRequest):
    """
    Публикация крупного достижения / релиза в официальный Telegram-канал (@UcustAi).
    Поддерживает прикрепление медиафайлов, форматирование метрик и HTML-теги.
    """
    from publishers.achievement_broadcaster import AchievementBroadcaster
    broadcaster = AchievementBroadcaster(target_channel=request.channel or "@UcustAi")
    result = await broadcaster.broadcast_milestone_async(
        title=request.title,
        description=request.description,
        metrics=request.metrics,
        media_path=request.media_path
    )
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка публикации достижения: {result.get('error') or result.get('message')}"
        )
    return {
        "status": "success",
        "broadcaster": "Telethon AchievementBroadcaster",
        "data": result
    }


@app.post("/api/v1/ai/rag/query", tags=["Knowledge Base RAG"])
async def query_knowledge_base(request: RAGQueryRequest):
    """
    Поиск по базе знаний через Clean RAG с защитой от галлюцинаций.
    """
    rag_context = await rag_pipeline.query_async(request.query, top_k_retrieval=request.top_k)
    return {
        "query": rag_context.query,
        "has_sufficient_context": rag_context.has_sufficient_context,
        "top_score": round(rag_context.top_score, 3),
        "context": rag_context.formatted_context if rag_context.has_sufficient_context else None,
        "fallback_message": rag_context.fallback_message
    }


@app.post("/api/v1/ai/rag/ingest", tags=["Knowledge Base RAG"])
async def ingest_knowledge_base(request: RAGIngestRequest):
    """
    Загрузка и индексация документов в локальный Clean RAG.
    """
    docs = []
    for item in request.documents:
        docs.append(
            Document(
                doc_id=item.get("doc_id", str(uuid.uuid4())),
                text=item.get("text", ""),
                source=item.get("source", "api_upload"),
                metadata=item.get("metadata", {})
            )
        )
    indexed_count = await rag_pipeline.ingest_documents_async(docs)
# -------------------------------------------------------------------
# 3.1 УДОБНЫЕ АЛИАСЫ ДЛЯ ФРОНТЕНДА И СБОРА ДАННЫХ (CONVENIENCE ALIASES)
# -------------------------------------------------------------------

class QuickVisionAnalysisRequest(BaseModel):
    user_id: str = Field("default_user", description="ID пользователя")
    session_id: Optional[str] = Field(None, description="ID сессии для кэширования")
    prompt: Optional[str] = Field("", description="Текстовый промпт/намерение пользователя")
    niche: Optional[str] = Field("Бизнес и услуги", description="Ниша бизнеса")
    company_name: Optional[str] = Field("UCust", description="Название компании")
    attachments: List[Any] = Field(..., description="1-3 фото (Base64 data-url, URL или пути к файлам)")


class DocumentAnalysisRequest(BaseModel):
    user_id: str = Field("default_user", description="ID пользователя")
    company_name: Optional[str] = Field("UCust", description="Название компании")
    niche: Optional[str] = Field("Бизнес и услуги", description="Ниша компании")
    documents: List[str] = Field(..., description="Пути к файлам или имена документов (PDF, DOCX, PPTX)")


class UnifiedBrandAnalysisRequest(BaseModel):
    user_id: str = Field("default_user", description="ID пользователя")
    company_name: Optional[str] = Field("", description="Название компании")
    niche: Optional[str] = Field("", description="Сфера деятельности")
    city: Optional[str] = Field("Москва", description="Город")
    urls: List[str] = Field(default=[], description="Ссылки: сайт, VK, Telegram, 2GIS/Яндекс")
    documents: List[str] = Field(default=[], description="Пути к документам (PDF, DOCX, PPTX)")
    images: List[Any] = Field(default=[], description="Фото / логотипы (Base64 или пути)")
    raw_notes: Optional[str] = Field("", description="Дополнительные заметки")
    fast_mode: bool = Field(True, description="Быстрый режим предварительного сканирования")


@app.post("/api/v1/vision/quick-analyze", response_model=Dict[str, Any], tags=["Convenience Aliases"])
async def quick_vision_analyze(
    payload: QuickVisionAnalysisRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret"),
) -> Dict[str, Any]:
    task_req = OrchestratorTaskRequest(
        task_type="quick_vision",
        user_id=payload.user_id,
        session_id=payload.session_id,
        payload=payload.dict()
    )
    res = await execute_orchestrator_task(task_req, x_internal_secret=x_internal_secret)
    return res.data


@app.post("/api/v1/collectors/analyze-documents", response_model=Dict[str, Any], tags=["Convenience Aliases"])
async def analyze_documents_direct(
    payload: DocumentAnalysisRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret"),
) -> Dict[str, Any]:
    task_req = OrchestratorTaskRequest(
        task_type="analyze_documents",
        user_id=payload.user_id,
        payload=payload.dict()
    )
    res = await execute_orchestrator_task(task_req, x_internal_secret=x_internal_secret)
    return res.data


@app.post("/api/v1/collectors/analyze-brand", response_model=Dict[str, Any], tags=["Convenience Aliases"])
async def analyze_brand_multimodal(
    payload: UnifiedBrandAnalysisRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret"),
) -> Dict[str, Any]:
    task_req = OrchestratorTaskRequest(
        task_type="quick_scan",
        user_id=payload.user_id,
        payload=payload.dict()
    )
    res = await execute_orchestrator_task(task_req, x_internal_secret=x_internal_secret)
    return res.data
# 4. WebSocket: Живой онбординг и Real-time стриминг для Фронтенда
# -------------------------------------------------------------------

class ConnectionManager:
    """Менеджер активных WebSocket подключений."""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        print(f"[WebSocket] 🔌 Клиент подключен к сессии: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            print(f"[WebSocket] 🔌 Клиент отключен: {session_id}")

    async def send_event(self, session_id: str, step: str, payload: Any):
        if session_id in self.active_connections:
            message = {
                "session_id": session_id,
                "step": step,
                "timestamp": datetime.utcnow().isoformat(),
                "payload": payload
            }
            await self.active_connections[session_id].send_text(json.dumps(message, ensure_ascii=False))

ws_manager = ConnectionManager()


@app.websocket("/ws/ai/session/{session_id}")
async def websocket_onboarding_stream(websocket: WebSocket, session_id: str):
    """
    WebSocket канал для живого интерактивного онбординга.
    Фронтенд отправляет данные формы или сообщения пользователя,
    Оркестратор в реальном времени стримит ответы агентов и статус прогресса.
    """
    await ws_manager.connect(session_id, websocket)
    
    try:
        # Приветственное событие от Интервьюера
        await ws_manager.send_event(
            session_id=session_id,
            step="interviewer_greeting",
            payload={
                "message": "Здравствуйте! Я ИИ-ассистент онбординга UCust. Готов собрать данные о вашем бизнесе и настроить команду агентов.",
                "required_fields": ["company_name", "niche", "raw_social_input", "goals"]
            }
        )
        
        while True:
            # Получаем сообщение от фронтенда
            raw_data = await websocket.receive_text()
            user_msg = json.loads(raw_data)
            
            # 1. Этап интервьюера (проверка ссылок и целей)
            await ws_manager.send_event(
                session_id=session_id,
                step="interviewer_processing",
                payload={"status": "Проверка ссылок и структуры данных..."}
            )
            await asyncio.sleep(0.5)
            
            # Запуск онбординга через Оркестратор
            await ws_manager.send_event(
                session_id=session_id,
                step="analyst_started",
                payload={"progress": 25, "status": "Аналитик собирает посты и отзывы..."}
            )
            
            result = await orchestrator.execute_task(
                task_type="onboarding",
                user_data=user_msg,
                session_id=session_id
            )
            
            await ws_manager.send_event(
                session_id=session_id,
                step="copywriter_started",
                payload={"progress": 65, "status": "Сайга формирует Tone-of-Voice и контент-план..."}
            )
            await asyncio.sleep(0.5)
            
            # Финальное событие завершения
            await ws_manager.send_event(
                session_id=session_id,
                step="pipeline_completed",
                payload={
                    "progress": 100,
                    "status": "Команда агентов успешно настроена!",
                    "result": result
                }
            )
            
    except WebSocketDisconnect:
        ws_manager.disconnect(session_id)
    except Exception as e:
        await ws_manager.send_event(
            session_id=session_id,
            step="error",
            payload={"error": str(e)}
        )
        ws_manager.disconnect(session_id)


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("AI_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("AI_SERVICE_PORT", "8000"))
    print(f"[API Gateway] 🚀 Запуск AI Service Gateway на http://{host}:{port} ...")
    uvicorn.run(app, host=host, port=port)
