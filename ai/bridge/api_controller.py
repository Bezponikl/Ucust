"""
FastAPI controller for orchestrating the multi-agent marketing pipeline with PostgreSQL storage.
"""

from __future__ import annotations

import logging
import os
import sys
import asyncio
from typing import Any, Dict, List, Literal, Optional

try:
    from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status, Header
except ImportError:
    class FastAPI:
        def __init__(self, title: str = "UCust.AI API", version: str = "1.0.0"):
            self.title = title
            self.version = version

        def on_event(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

        def post(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

        def get(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

    class BackgroundTasks:
        def add_task(self, func, *args, **kwargs):
            func(*args, **kwargs)

    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            self.status_code = status_code
            self.detail = detail
            super().__init__(f"HTTP {status_code}: {detail}")

    class status:
        HTTP_200_OK = 200
        HTTP_202_ACCEPTED = 202
        HTTP_400_BAD_REQUEST = 400
        HTTP_404_NOT_FOUND = 404
        HTTP_409_CONFLICT = 409
        HTTP_500_INTERNAL_SERVER_ERROR = 500

    def Depends(dependency=None):
        return dependency

    def Header(default=None, alias=None):
        return default

from pydantic import BaseModel, Field

from core.agents import AgentContext, Agent_Copywriter
from core.notification_bridge import ApprovalDecision
from core.orchestrator import AgentState, build_default_orchestrator
from integration.java_bridge import JavaBridgeClient, get_java_bridge_client
from schemas.models import (
    CopywritingFramework,
    LTX23PromptSchema,
    PendingPostSchema,
    PostDraftSchema,
    PublishRequestSchema,
    QuestionnaireStep1,
    QuestionnaireStep2,
    QuestionnaireStep3,
    QuestionnaireStep4,
    QuestionnaireStep5,
    UserQuestionnaire,
)
from storage.db import (
    DatabaseFactory,
    create_task,
    get_async_sessionmaker,
    get_db_session,
    get_pending_tasks,
    get_task,
    init_db,
    update_task_status,
)
from publishers import (
    BasePublisher,
    InstagramPublisher,
    OdnoklassnikiPublisher,
    TelegramPublisher,
    VkPublisher,
    get_publisher,
)
from storage.repository import get_user_questionnaire

# Reconfigure stdout encoding for Windows CP1251 compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

LOG_FILE = os.getenv("UCUST_LOG_FILE", "app_log.log")
APP_TITLE = os.getenv("UCUST_APP_TITLE", "UCust.AI API")
APP_VERSION = os.getenv("UCUST_APP_VERSION", "1.0.0")

logging.basicConfig(
    level=os.getenv("UCUST_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("ucust_api")

try:
    database = DatabaseFactory.build()
except Exception as exc:
    logger.warning("DatabaseFactory initialization: %s", exc)
    database = None

app = FastAPI(title=APP_TITLE, version=APP_VERSION)


@app.on_event("startup")
async def startup_event() -> None:
    """Startup lifecycle hook to initialize database tables."""
    await init_db()


class ProcessRequest(BaseModel):
    """Input contract for starting a background content-generation job."""

    user_id: str = Field(..., description="External user identifier.")
    framework: CopywritingFramework = Field(
        default=CopywritingFramework.PAS,
        description="Фреймворк копирайтинга (PAS, AIDA, PMHS)",
    )


class ProcessResponse(BaseModel):
    """Response contract for accepted background jobs."""

    status: str
    detail: str
    job_id: int


class StatusResponse(BaseModel):
    """Status contract for task polling."""

    status: str
    result: Optional[str] = None
    error: Optional[str] = None
    approval_status: Optional[str] = None
    action_required: bool = False


class UserActionRequest(BaseModel):
    """Input contract for human-in-the-loop action submission."""

    action: Literal["APPROVED", "EDIT", "REGENERATE"] = Field(
        ...,
        description="User decision for the current draft.",
    )
    event_type: Optional[str] = Field(
        default=None,
        description="Optional event type (gratitude, holiday, achievement, emergency, custom_edit).",
    )
    context: Optional[str] = Field(
        default=None,
        description="Optional event context or editorial instruction.",
    )


class UserActionResponse(BaseModel):
    """Output contract for human-in-the-loop action processing."""

    status: str
    detail: str
    job_id: int
    result: Optional[str] = None


async def _get_or_create_questionnaire(user_id: str, session: Any = None) -> tuple[int, UserQuestionnaire]:
    """
    Attempts to fetch questionnaire from database;
    falls back to a default mock questionnaire for development/testing.
    """
    if database is not None:
        try:
            loaded = get_user_questionnaire(database, user_id)
            if loaded is not None:
                return loaded
        except Exception as exc:
            logger.warning("Could not fetch questionnaire from DB for user_id=%s: %s", user_id, exc)

    # Fallback default questionnaire for development mode
    mock_questionnaire = UserQuestionnaire(
        step1=QuestionnaireStep1(
            business_name=f"Brand-{user_id}",
            mission="Инновационные маркетинговые решения и автоматизация контента",
            region="Москва и регионы РФ",
        ),
        step2=QuestionnaireStep2(
            target_audience="B2B предприниматели, маркетологи и руководители продуктов",
            demographics="Мужчины и женщины 25-50 лет",
            pain_points="Высокая стоимость лида и нехватка времени на написание контента",
        ),
        step3=QuestionnaireStep3(
            tone_of_voice="Дружелюбный и экспертный",
            content_formats="Посты-кейсы, гайды, разборы трендов",
            taboo_topics="Политика, незаверенные обещания",
        ),
        step4=QuestionnaireStep4(
            goals="Повышение вовлеченности аудитории и лидогенерация",
            kpi="ER (Engagement Rate), количество заявок",
            frequency="3 раза в неделю",
        ),
        step5=QuestionnaireStep5(
            competitors="CompetitorA, CompetitorB",
            references="Примеры успешных IT-брендов",
            additional_notes="Демо-анкета для режима разработки",
        ),
    )
    return 1, mock_questionnaire


async def _run_orchestrator(job_id: int, user_id: str, questionnaire: UserQuestionnaire) -> None:
    """
    Executes the recursive orchestrator in background task.
    Uses its own dedicated database session factory so it remains active after 202 Accepted return.
    """
    try:
        await update_task_status(job_id, status="PROCESSING")

        context = AgentContext(questionnaire=questionnaire)
        orchestrator = build_default_orchestrator(database=database)

        try:
            context = await orchestrator.run_pipeline(context)
        except Exception as exc:
            logger.exception("Critical orchestrator failure for job_id=%d", job_id)
            await update_task_status(job_id, status="FAILED", error_message=str(exc))
            return

        payload = {
            "post_text": context.post_draft.text if context.post_draft else None,
            "image_url": context.post_draft.image_url if context.post_draft else None,
            "video_url": context.post_draft.video_url if context.post_draft else None,
            "audio_url": context.post_draft.audio_url if context.post_draft else None,
            "media_url": context.post_draft.media_url if context.post_draft else None,
            "local_video_path": context.post_draft.local_video_path if context.post_draft else None,
            "local_audio_path": context.post_draft.local_audio_path if context.post_draft else None,
            "approval_status": context.approval_status,
            "last_event_type": context.user_event_type,
            "last_event_context": context.user_event_context,
            "ltx23_prompts": [p.model_dump() for p in context.ltx23_prompts] if context.ltx23_prompts else [],
            "uniqueness_score": context.post_draft.uniqueness_score if context.post_draft else 1.0,
            "duplicates_found": context.post_draft.duplicates_found if context.post_draft else False,
        }

        task_status = "AWAITING_USER_ACTION" if context.pending_user_action else "COMPLETED"
        await update_task_status(job_id, status=task_status, result_payload=payload)

    except Exception as exc:
        logger.exception("Background processing failed for user_id=%s", user_id)
        await update_task_status(job_id, status="FAILED", error_message=str(exc))


@app.post("/api/v1/process", response_model=ProcessResponse, status_code=status.HTTP_202_ACCEPTED)
@app.post("/process", response_model=ProcessResponse, status_code=status.HTTP_202_ACCEPTED)
async def process_request(
    payload: ProcessRequest,
    background_tasks: BackgroundTasks,
    session: Any = Depends(get_db_session),
) -> ProcessResponse:
    """Endpoint for initiating asynchronous background content generation pipeline."""
    if not payload.user_id or not payload.user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field 'user_id' is required.",
        )

    clean_user_id = payload.user_id.strip()
    user_profile_id, questionnaire = await _get_or_create_questionnaire(clean_user_id, session)

    job_id = await create_task(
        user_id=clean_user_id,
        user_profile_id=user_profile_id,
        status="PENDING",
        session=session,
    )

    background_tasks.add_task(_run_orchestrator, job_id, clean_user_id, questionnaire)

    return ProcessResponse(
        status="accepted",
        detail="Background processing has started.",
        job_id=job_id,
    )


@app.get("/api/v1/status/{job_id}", response_model=StatusResponse)
async def get_status(
    job_id: int,
    session: Any = Depends(get_db_session),
) -> StatusResponse:
    """Endpoint for polling FSM task execution status and latest result payload."""
    task = await get_task(job_id, session=session)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with job_id={job_id} was not found.",
        )

    task_status = task.status
    result_payload = task.result_payload or {}

    result_value = result_payload.get("post_text") or result_payload.get("image_link")
    approval_status = result_payload.get("approval_status")
    action_required = task_status == "AWAITING_USER_ACTION"
    error_value = task.error_message if task_status == "FAILED" else None

    return StatusResponse(
        status=task_status,
        result=result_value,
        error=error_value,
        approval_status=approval_status,
        action_required=action_required,
    )


@app.post("/api/v1/action/{job_id}", response_model=UserActionResponse)
async def submit_user_action(
    job_id: int,
    payload: UserActionRequest,
    session: Any = Depends(get_db_session),
    java_bridge: JavaBridgeClient = Depends(get_java_bridge_client),
) -> UserActionResponse:
    """
    Endpoint for submitting human-in-the-loop decisions (APPROVED, EDIT, REGENERATE).
    Dispatches final artifacts to Java backend when APPROVED and updates DB status.
    """
    task = await get_task(job_id, session=session)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with job_id={job_id} was not found.",
        )

    current_status = task.status
    if current_status != "AWAITING_USER_ACTION":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Task status '{current_status}' does not accept user actions.",
        )

    current_payload = task.result_payload or {}
    current_post_text = current_payload.get("post_text") or ""

    # ACTION 1: APPROVED
    if payload.action == ApprovalDecision.APPROVED.value:
        current_payload["approval_status"] = ApprovalDecision.APPROVED.value

        post_draft = PostDraftSchema(
            text=current_post_text,
            uniqueness_score=current_payload.get("uniqueness_score", 1.0),
            duplicates_found=current_payload.get("duplicates_found", False),
            video_url=current_payload.get("video_url"),
            audio_url=current_payload.get("audio_url"),
            media_url=current_payload.get("media_url"),
            local_video_path=current_payload.get("local_video_path"),
            local_audio_path=current_payload.get("local_audio_path"),
        )

        raw_prompts = current_payload.get("ltx23_prompts", [])
        ltx23_prompts = [
            LTX23PromptSchema(**p) for p in raw_prompts if isinstance(p, dict)
        ]

        # Dispatch generated content artifacts to Java Backend asynchronously
        try:
            draft_ok = await java_bridge.send_post_draft(job_id, post_draft)
            prompts_ok = True
            if ltx23_prompts:
                prompts_ok = await java_bridge.send_ltx23_prompts(job_id, ltx23_prompts)

            if not draft_ok or not prompts_ok:
                logger.warning(
                    "Java backend dispatch warning for job_id=%d: draft_ok=%s, prompts_ok=%s",
                    job_id,
                    draft_ok,
                    prompts_ok,
                )
        except Exception as bridge_exc:
            logger.error("Error dispatching to Java bridge for job_id=%d: %s", job_id, bridge_exc)
            await update_task_status(
                job_id=job_id,
                status="FAILED",
                result_payload=current_payload,
                error_message=f"Java bridge dispatch error: {bridge_exc}",
                session=session,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to dispatch payload to Java backend: {bridge_exc}",
            )

        await update_task_status(
            job_id=job_id,
            status="COMPLETED",
            result_payload=current_payload,
            session=session,
        )

        return UserActionResponse(
            status="COMPLETED",
            detail="Content approved and sent to Java backend.",
            job_id=job_id,
            result=current_post_text,
        )

    # ACTION 2: EDIT
    if payload.action == ApprovalDecision.EDIT.value:
        event_type = (payload.event_type or "custom_edit").strip().lower()
        event_context = (payload.context or "").strip()

        copywriter = Agent_Copywriter()
        event_context_obj = AgentContext(
            post_draft=PostDraftSchema(
                text=current_post_text,
                uniqueness_score=current_payload.get("uniqueness_score", 1.0),
                duplicates_found=current_payload.get("duplicates_found", False),
            ),
            approval_status=ApprovalDecision.EDIT.value,
            pending_user_action=True,
        )

        event_context_obj = await copywriter.process_user_event(
            context=event_context_obj,
            event_type=event_type,
            event_context=event_context,
        )

        updated_text = (
            event_context_obj.post_draft.text if event_context_obj.post_draft else current_post_text
        )
        current_payload["post_text"] = updated_text
        current_payload["approval_status"] = ApprovalDecision.EDIT.value
        current_payload["last_event_type"] = event_type
        current_payload["last_event_context"] = event_context

        await update_task_status(
            job_id=job_id,
            status="AWAITING_USER_ACTION",
            result_payload=current_payload,
            session=session,
        )

        return UserActionResponse(
            status="AWAITING_USER_ACTION",
            detail="Draft updated with user event context; waiting for approval.",
            job_id=job_id,
            result=updated_text,
        )

    # ACTION 3: REGENERATE
    event_type = (payload.event_type or "regenerate").strip().lower()
    event_context = (payload.context or "").strip()

    regenerated_context = AgentContext(
        post_draft=PostDraftSchema(
            text=current_post_text,
            uniqueness_score=current_payload.get("uniqueness_score", 1.0),
            duplicates_found=current_payload.get("duplicates_found", False),
        ),
        approval_status=ApprovalDecision.REGENERATE.value,
        pending_user_action=True,
        user_event_type=event_type,
        user_event_context=event_context,
    )

    orchestrator = build_default_orchestrator(database=database)
    orchestrator.transition_to(AgentState.AWAITING_USER_DECISION)
    regenerated_context = await orchestrator.run_pipeline(regenerated_context)

    updated_text = (
        regenerated_context.post_draft.text if regenerated_context.post_draft else current_post_text
    )
    current_payload["post_text"] = updated_text
    current_payload["approval_status"] = regenerated_context.approval_status
    current_payload["last_event_type"] = regenerated_context.user_event_type
    current_payload["last_event_context"] = regenerated_context.user_event_context
    current_payload["ltx23_prompts"] = (
        [p.model_dump() for p in regenerated_context.ltx23_prompts]
        if regenerated_context.ltx23_prompts
        else []
    )

    next_status = "COMPLETED" if not regenerated_context.pending_user_action else "AWAITING_USER_ACTION"

    await update_task_status(
        job_id=job_id,
        status=next_status,
        result_payload=current_payload,
        session=session,
    )

    return UserActionResponse(
        status=next_status,
        detail="Regeneration flow executed.",
        job_id=job_id,
        result=updated_text,
    )


@app.get("/api/v1/posts/pending", response_model=list[PendingPostSchema])
async def get_pending_posts(
    session: Any = Depends(get_db_session),
) -> list[PendingPostSchema]:
    """
    Export endpoint for Human-in-the-Loop web UI preview.
    Retrieves all tasks/posts currently in 'AWAITING_USER_ACTION' state.
    """
    tasks = await get_pending_tasks(session=session)
    pending_list = []
    for task in tasks:
        payload = task.result_payload or {}
        pending_list.append(
            PendingPostSchema(
                job_id=task.id,
                user_id=task.user_id or "unknown",
                status=task.status,
                post_text=payload.get("post_text"),
                video_url=payload.get("video_url"),
                audio_url=payload.get("audio_url"),
                media_url=payload.get("media_url"),
                local_video_path=payload.get("local_video_path"),
                local_audio_path=payload.get("local_audio_path"),
                uniqueness_score=payload.get("uniqueness_score", 1.0),
                duplicates_found=payload.get("duplicates_found", False),
            )
        )
    return pending_list


@app.post("/api/v1/posts/{post_id}/publish", response_model=dict[str, Any])
async def publish_post(
    post_id: int,
    payload: PublishRequestSchema,
    session: Any = Depends(get_db_session),
) -> dict[str, Any]:
    """
    Publishing endpoint for Human-in-the-Loop pattern.
    Updates DB status to USER_APPROVED and dispatches post text and media to selected social publishers.
    """
    task = await get_task(post_id, session=session)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post task with ID {post_id} was not found.",
        )

    task_payload = task.result_payload or {}
    text_content = payload.custom_caption or task_payload.get("post_text") or "No text provided"
    media_path = task_payload.get("local_video_path") or task_payload.get("local_audio_path")

    # Step 1: Update task state to USER_APPROVED
    await update_task_status(
        job_id=post_id,
        status="USER_APPROVED",
        result_payload=task_payload,
        session=session,
    )

    publish_results = {}
    raw_platforms = payload.platforms or payload.target_platforms or ["telegram"]
    platforms = [p.lower().strip() for p in raw_platforms]

    # Step 2: Dynamically dispatch to requested publishers using get_publisher factory
    for platform in platforms:
        try:
            publisher = get_publisher(platform)
            ok_res = await publisher.publish(text=text_content, media_path=media_path)
            publish_results[platform] = ok_res
        except Exception as pub_exc:
            logger.error("Error publishing to platform '%s' for post_id=%d: %s", platform, post_id, pub_exc)
            publish_results[platform] = False

    # Step 3: Update task state to PUBLISHED
    await update_task_status(
        job_id=post_id,
        status="PUBLISHED",
        result_payload=task_payload,
        session=session,
    )

    return {
        "status": "PUBLISHED",
        "job_id": post_id,
        "detail": f"Post #{post_id} successfully published to platforms: {platforms}.",
        "publish_results": publish_results,
    }


# ============================================================================
# МУЛЬТИМОДАЛЬНЫЕ ЭНДПОИНТЫ: ПАРСЕРЫ, ДОКУМЕНТЫ И МОМЕНТАЛЬНЫЙ MOONDREAM (VISION)
# ============================================================================

class QuickVisionAnalysisRequest(BaseModel):
    user_id: str = Field(..., description="ID пользователя")
    session_id: Optional[str] = Field(default=None, description="ID сессии для кэширования")
    prompt: Optional[str] = Field(default="", description="Текстовый промпт/намерение пользователя")
    niche: Optional[str] = Field(default="Бизнес и услуги", description="Ниша бизнеса")
    company_name: Optional[str] = Field(default="UCust", description="Название компании")
    attachments: List[Any] = Field(..., description="1-3 фото (Base64 data-url, URL или пути к файлам)")


class DocumentAnalysisRequest(BaseModel):
    user_id: str = Field(..., description="ID пользователя")
    company_name: Optional[str] = Field(default="UCust", description="Название компании")
    niche: Optional[str] = Field(default="Бизнес и услуги", description="Ниша компании")
    documents: List[str] = Field(..., description="Пути к файлам или имена документов (PDF, DOCX, PPTX)")


class UnifiedBrandAnalysisRequest(BaseModel):
    user_id: str = Field(..., description="ID пользователя")
    company_name: Optional[str] = Field(default="", description="Название компании")
    niche: Optional[str] = Field(default="", description="Сфера деятельности")
    city: Optional[str] = Field(default="Москва", description="Город")
    urls: List[str] = Field(default=[], description="Ссылки: сайт, VK, Telegram, 2GIS/Яндекс")
    documents: List[str] = Field(default=[], description="Пути к документам (PDF, DOCX, PPTX)")
    images: List[Any] = Field(default=[], description="Фото / логотипы (Base64 или пути)")
    raw_notes: Optional[str] = Field(default="", description="Дополнительные заметки")
    fast_mode: bool = Field(default=True, description="Быстрый режим предварительного сканирования")


@app.post("/api/v1/vision/quick-analyze", response_model=Dict[str, Any])
async def quick_vision_analyze(
    payload: QuickVisionAnalysisRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret"),
) -> Dict[str, Any]:
    """
    Эндпоинт моментального анализа фото при загрузке на фронтенде:
    1. Запускает Moondream VLM сразу при прикреплении пользователем 1-3 фото.
    2. Определяет семантические роли (руки/маникюр, питомец, интерьер/кофейня).
    3. Раскладывает по слотам воркфлоу realism2.0.json (Ноды 55, 64, 65).
    4. Синтезирует композиционный Fusion-промпт и палитру цветов.
    5. Кэширует результат, чтобы генерация поста происходила мгновенно.
    """
    import time
    from skills.moondream_vqa import MoondreamVQA

    t_start = time.time()
    vqa = MoondreamVQA()

    analysis_res = vqa.analyze_attachments_batch(
        attachments=payload.attachments,
        topic=payload.prompt or "",
        company_name=payload.company_name
    )

    duration_ms = round((time.time() - t_start) * 1000, 2)
    return {
        "status": "success",
        "execution_time_ms": duration_ms,
        "user_id": payload.user_id,
        "session_id": payload.session_id,
        "photos_count": analysis_res.get("count", 0),
        "brand_colors": analysis_res.get("colors", []),
        "slot_mapping": analysis_res.get("slot_mapping"),
        "fusion_prompt": analysis_res.get("fusion_prompt"),
        "visual_narrative": analysis_res.get("fusion_narrative"),
        "prompt_keywords": analysis_res.get("prompt_keywords")
    }


@app.post("/api/v1/collectors/analyze-documents", response_model=Dict[str, Any])
async def analyze_documents_direct(
    payload: DocumentAnalysisRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret"),
) -> Dict[str, Any]:
    """
    Эндпоинт парсинга документов клиентов (PDF, DOCX, PPTX):
    1. Извлекает текст, прайсы, списки услуг и УТП.
    2. Индексирует контент в Clean RAG память бренда.
    3. Возвращает структурированную сводку для предзаполнения анкеты.
    """
    import time
    from collectors.document_collector import DocumentCollector

    t_start = time.time()
    doc_collector = DocumentCollector()
    extracted_docs = doc_collector.extract_documents_batch(payload.documents)

    summary_chunks = []
    for doc in extracted_docs:
        if doc.get("status") == "success" and doc.get("raw_text"):
            summary_chunks.append(f"[{doc['file_name']}]: {doc['raw_text'][:300]}")

    duration_ms = round((time.time() - t_start) * 1000, 2)
    return {
        "status": "success",
        "execution_time_ms": duration_ms,
        "user_id": payload.user_id,
        "company_name": payload.company_name,
        "documents_count": len(extracted_docs),
        "extracted_documents": extracted_docs,
        "quick_summary": "\n".join(summary_chunks)
    }


@app.post("/api/v1/collectors/analyze-brand", response_model=Dict[str, Any])
async def analyze_brand_multimodal(
    payload: UnifiedBrandAnalysisRequest,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret"),
) -> Dict[str, Any]:
    """
    Единый мультимодальный эндпоинт для онбординга и предзаполнения анкеты:
    1. Параллельно опрашивает парсеры сайта, VK, TG, карт (2GIS/Яндекс).
    2. Анализирует загруженные документы (PDF/DOCX) и фото через Moondream VLM.
    3. Формирует готовую анкету бренда (название, ниша, УТП, цвета, соцсети, отзывы).
    4. Автоматически отправляет результат в бэкенд через Webhook (BACKEND_COLLECTOR_CALLBACK_URL).
    """
    import time
    from collectors.website_collector import WebsiteCollector
    from collectors.vk_collector import VKCollector
    from collectors.twogis_collector import TwoGISCollector
    from collectors.document_collector import DocumentCollector
    from skills.moondream_vqa import MoondreamVQA
    from core.orchestrator import SecurityGuard

    t_start = time.time()
    
    # SSRF защита ссылок
    safe_urls = []
    for u in payload.urls:
        if SecurityGuard.check_user_input(u) and not any(h in u.lower() for h in ["localhost", "127.0.0.1", "10.0.", "192.168.", "169.254."]):
            safe_urls.append(u)

    site_urls = [u for u in safe_urls if not any(k in u.lower() for k in ["vk.com", "t.me", "2gis.", "yandex."])]
    vk_urls = [u for u in safe_urls if "vk.com" in u.lower()]
    tg_urls = [u for u in safe_urls if "t.me" in u.lower()]
    map_urls = [u for u in safe_urls if any(k in u.lower() for k in ["2gis.", "yandex.ru/maps", "maps.yandex"])]

    # Параллельные асинхронные задачи
    async def _fetch_site():
        if not site_urls:
            return None
        return await WebsiteCollector().collect_website_async(site_urls[0])

    async def _fetch_vk():
        if not vk_urls:
            return None
        return await VKCollector().collect_group_async(vk_urls[0])

    async def _fetch_maps():
        if not map_urls:
            return None
        return await TwoGISCollector().collect_reviews_async(map_urls[0])

    async def _fetch_docs():
        if not payload.documents:
            return []
        return DocumentCollector().extract_documents_batch(payload.documents)

    async def _fetch_vision():
        if not payload.images:
            return None
        return MoondreamVQA().analyze_attachments_batch(
            attachments=payload.images,
            company_name=payload.company_name or "Brand"
        )

    site_data, vk_data, maps_data, docs_data, vision_data = await asyncio.gather(
        _fetch_site(),
        _fetch_vk(),
        _fetch_maps(),
        _fetch_docs(),
        _fetch_vision(),
        return_exceptions=True
    )

    # Агрегация фирменных цветов
    brand_colors = []
    if isinstance(vision_data, dict) and vision_data.get("colors"):
        brand_colors.extend(vision_data["colors"])
    if isinstance(site_data, dict) and site_data.get("theme_color"):
        brand_colors.append(site_data["theme_color"])

    extracted_title = payload.company_name or (site_data.get("title") if isinstance(site_data, dict) else "") or "Мой бизнес"
    extracted_niche = payload.niche or (site_data.get("description", "")[:60] if isinstance(site_data, dict) else "") or "Бизнес и услуги"
    description = payload.raw_notes or (site_data.get("description") if isinstance(site_data, dict) else "")

    prefilled_profile = {
        "business_name": extracted_title,
        "niche": extracted_niche,
        "city": payload.city,
        "description": description,
        "brand_colors": list(dict.fromkeys(brand_colors))[:5] or ["#3b82f6", "#1e293b"],
        "visual_style": vision_data.get("visual_context_for_llm") if isinstance(vision_data, dict) else "Естественный студийный свет",
        "contacts": site_data.get("contacts") if isinstance(site_data, dict) else {},
        "reviews_summary": maps_data.get("summary") if isinstance(maps_data, dict) else None,
        "documents_parsed_count": len(docs_data) if isinstance(docs_data, list) else 0,
        "social_links": {
            "website": site_urls[0] if site_urls else None,
            "vk": vk_urls[0] if vk_urls else None,
            "telegram": tg_urls[0] if tg_urls else None
        }
    }

    # Фоновый HTTP Push в основной Бэкенд
    backend_sync_url = os.getenv("BACKEND_COLLECTOR_CALLBACK_URL")
    if backend_sync_url:
        async def _push():
            try:
                import aiohttp
                secret = os.getenv("INTERNAL_API_SECRET", "ucust-super-secret-service-token-2026")
                async with aiohttp.ClientSession() as s:
                    headers = {"X-Internal-Secret": secret, "Content-Type": "application/json"}
                    await s.post(backend_sync_url, json={"user_id": payload.user_id, "profile": prefilled_profile}, headers=headers, timeout=aiohttp.ClientTimeout(total=5))
            except Exception:
                pass
        asyncio.create_task(_push())

    duration_ms = round((time.time() - t_start) * 1000, 2)
    return {
        "status": "success",
        "execution_time_ms": duration_ms,
        "user_id": payload.user_id,
        "prefilled_profile": prefilled_profile,
        "moondream_analysis": vision_data if isinstance(vision_data, dict) else None,
        "documents_analysis": docs_data if isinstance(docs_data, list) else []
    }


__all__ = ["app"]
