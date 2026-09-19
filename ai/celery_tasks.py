"""
File: ai/celery_tasks.py
Celery Worker Configuration & Distributed Task Bus for UCust AI.

Development Environment (Low-spec / 8GB RAM / CPU):
    celery -A celery_tasks.celery_app worker --loglevel=info --concurrency=1 -Q ucust_ai_queue

Production Environment (1-2x A100/H100 80GB VRAM, 128GB RAM):
    celery -A celery_tasks.celery_app worker --loglevel=info --concurrency=4 -Q ucust_ai_queue,ucust_gpu_render
"""

from __future__ import annotations

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional

try:
    from celery import Celery
    HAS_CELERY = True
except ImportError:
    HAS_CELERY = False

logger = logging.getLogger("CeleryTasks")

# Настройка брокера и бэкенда результатов (Redis)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

if HAS_CELERY:
    celery_app = Celery("ucust_ai", broker=REDIS_URL, backend=REDIS_URL)

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_routes={
            "celery_tasks.render_post_task": {"queue": "ucust_gpu_render"},
            "celery_tasks.*": {"queue": "ucust_ai_queue"},
        },
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        task_track_started=True,
        task_time_limit=300,  # 5 минут жесткий лимит
    )
else:
    class DummyAsyncResult:
        def __init__(self, task_id):
            self.id = task_id
            self.status = "PENDING"

    class DummyTask:
        def __init__(self, fn, name):
            self.fn = fn
            self.name = name
            self.request = type("Req", (), {"id": "mock-task-id-123"})()
        def __call__(self, *args, **kwargs):
            return self.fn(self, *args, **kwargs)
        def delay(self, *args, **kwargs):
            return self.fn(self, *args, **kwargs)

    class DummyCelery:
        def __init__(self, name, broker=None, backend=None):
            self.main = name
            self.broker = broker
            self.backend = backend
            self.conf = {}
            self.tasks = {}
        def task(self, *dargs, **dkwargs):
            def decorator(fn):
                t_name = dkwargs.get("name", fn.__name__)
                dt = DummyTask(fn, t_name)
                self.tasks[t_name] = dt
                return dt
            return decorator
        def send_task(self, name, args=None, kwargs=None, queue=None):
            import uuid
            tid = f"task_{uuid.uuid4().hex[:12]}"
            return DummyAsyncResult(task_id=tid)

    celery_app = DummyCelery("ucust_ai", broker=REDIS_URL, backend=REDIS_URL)




def _run_async(coro):
    """Хелпер для запуска асинхронных корутин внутри синхронных Celery тасок."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(asyncio.run, coro).result()
    else:
        new_loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(new_loop)
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()



@celery_app.task(name="celery_tasks.onboard_brand_task", bind=True)
def onboard_brand_task(
    self,
    tenant_id: str,
    company_name: str,
    niche: str,
    telegram_channel: Optional[str] = None,
    website_url: Optional[str] = None,
    document_paths: Optional[List[str]] = None,
    raw_notes: Optional[str] = None,
    callback_url: Optional[str] = None,
    dev_mode: bool = True
) -> Dict[str, Any]:
    """
    Фоновый онбординг бренда: сбор данных, извлечение Brand DNA, сохранение в Persistent RAG
    и отправка Webhook уведомления на внешний бэкенд.
    """
    logger.info(f"🚀 [Celery] Старт онбординга {company_name} (Task ID: {self.request.id})")
    from skills.onboarding_agent import OnboardingAgent
    from services.rag_manager import BrandKnowledgeManager
    from services.webhook_manager import WebhookCallbackManager

    agent = OnboardingAgent(dev_mode=dev_mode)
    
    try:
        brand_dna = _run_async(agent.ingest_and_profile_brand(
            tenant_id=tenant_id,
            company_name=company_name,
            niche=niche,
            telegram_channel=telegram_channel,
            website_url=website_url,
            document_paths=document_paths,
            raw_notes=raw_notes
        ))
        
        # Сохранение в Persistent RAG (PostgreSQL / SQLite)
        _run_async(BrandKnowledgeManager.upsert_brand_dna(
            tenant_id=tenant_id,
            dna_data=brand_dna.dict()
        ))

        res = {
            "status": "success",
            "task_id": self.request.id,
            "tenant_id": tenant_id,
            "brand_dna": brand_dna.dict()
        }

        # Webhook Push обратной связи
        if callback_url:
            WebhookCallbackManager.send_callback_sync(
                callback_url=callback_url,
                event_type="onboarding_completed",
                tenant_id=tenant_id,
                task_id=self.request.id,
                status="success",
                data=res
            )

        return res
    except Exception as exc:
        logger.error(f"❌ [Celery] Ошибка онбординга {company_name}: {exc}")
        if callback_url:
            WebhookCallbackManager.send_callback_sync(
                callback_url=callback_url,
                event_type="onboarding_failed",
                tenant_id=tenant_id,
                task_id=self.request.id,
                status="failed",
                error=str(exc)
            )
        raise exc


@celery_app.task(name="celery_tasks.audit_post_task", bind=True)
def audit_post_task(
    self,
    proposed_topic_or_text: str,
    recent_channel_posts: List[str],
    topic_category: str = "general",
    threshold: float = 0.82
) -> Dict[str, Any]:
    """
    Фоновый аудит уникальности темы / текста поста.
    """
    logger.info(f"🔍 [Celery] Аудит темы: '{proposed_topic_or_text[:50]}...'")
    from skills.audit_deduplication_agent import AuditDeduplicationAgent
    agent = AuditDeduplicationAgent(custom_threshold=threshold)
    verdict = agent.evaluate_uniqueness(
        proposed_topic_or_text=proposed_topic_or_text,
        recent_channel_posts=recent_channel_posts,
        topic_category=topic_category
    )
    return {
        "status": "success",
        "task_id": self.request.id,
        "verdict": {
            "is_duplicate": verdict.is_duplicate,
            "similarity_score": verdict.similarity_score,
            "original_topic": verdict.original_topic,
            "suggested_shifted_angle": verdict.suggested_shifted_angle,
            "reason": verdict.reason
        }
    }


@celery_app.task(name="celery_tasks.generate_post_draft_task", bind=True)
def generate_post_draft_task(
    self,
    tenant_id: str,
    tier: str = "pro",
    industry: str = "b2b_corporate",
    topic: str = "Экспертный обзор",
    callback_url: Optional[str] = None,
    dev_simulation_mode: bool = True
) -> Dict[str, Any]:
    """
    Генерация черновика поста с нулевой стоимостью GPU (Lazy Rendering)
    и отправка Webhook уведомления.
    """
    logger.info(f"✍️ [Celery] Генерация черновика для {tenant_id}...")
    from core.lazy_rendering_controller import LazyRenderingController, SubscriptionTier, IndustryArchetype
    from skills.content_strategy_engine import ContentStrategyEngine, BrandProfile
    from services.rag_manager import BrandKnowledgeManager
    from services.webhook_manager import WebhookCallbackManager
    
    try:
        # Пытаемся обогатить BrandProfile данными из Persistent RAG
        saved_dna = _run_async(BrandKnowledgeManager.get_brand_dna(tenant_id))
        brand_name = saved_dna.get("company_name", tenant_id) if saved_dna else tenant_id
        tov = saved_dna.get("tone_of_voice", "Экспертный, лаконичный") if saved_dna else "Экспертный, лаконичный"
        props = saved_dna.get("brand_props", ["minimalist oak desk", "brass details"]) if saved_dna else ["minimalist oak desk", "brass details"]

        from skills.content_strategy_engine import RawDataIngestion, IngestionSourceType
        from datetime import datetime

        engine = ContentStrategyEngine(dev_mode=True)
        brand = BrandProfile(
            brand_id=tenant_id,
            company_name=brand_name,
            industry=IndustryArchetype(industry),
            tier=SubscriptionTier(tier),
            tone_of_voice=tov,
            brand_props=props
        )
        
        raw_input = RawDataIngestion(
            source_type=IngestionSourceType.RAG_FACTS_ONLY,
            user_raw_intent=topic,
            rag_context_snippets=[topic]
        )

        draft = engine.generate_post_draft(
            brand=brand,
            raw_input=raw_input,
            target_date=datetime.utcnow()
        )
        
        res = {
            "status": "success",
            "task_id": self.request.id,
            "post_draft": draft.dict()
        }

        if callback_url:
            WebhookCallbackManager.send_callback_sync(
                callback_url=callback_url,
                event_type="content_draft_ready",
                tenant_id=tenant_id,
                task_id=self.request.id,
                status="success",
                data=res
            )

        return res
    except Exception as exc:
        logger.error(f"❌ [Celery] Ошибка генерации черновика для {tenant_id}: {exc}")
        if callback_url:
            WebhookCallbackManager.send_callback_sync(
                callback_url=callback_url,
                event_type="content_draft_failed",
                tenant_id=tenant_id,
                task_id=self.request.id,
                status="failed",
                error=str(exc)
            )
        raise exc


@celery_app.task(name="celery_tasks.render_post_task", bind=True)
def render_post_task(
    self,
    post_id: str,
    tenant_id: Optional[str] = "tenant_default",
    callback_url: Optional[str] = None,
    dev_simulation_mode: bool = True
) -> Dict[str, Any]:
    """
    Тяжелый GPU-рендер графики по запросу (выполняется в очереди ucust_gpu_render).
    """
    logger.info(f"🎨 [Celery GPU] Запуск рендера для post_id={post_id}...")
    from core.lazy_rendering_controller import LazyRenderingController
    from services.webhook_manager import WebhookCallbackManager

    controller = LazyRenderingController(dev_simulation_mode=dev_simulation_mode)
    
    try:
        rendered_post = _run_async(controller.trigger_render(post_id=post_id))
        res = {
            "status": "success",
            "task_id": self.request.id,
            "post_id": post_id,
            "rendered_post": rendered_post.dict() if rendered_post else None
        }

        if callback_url:
            WebhookCallbackManager.send_callback_sync(
                callback_url=callback_url,
                event_type="render_completed",
                tenant_id=tenant_id or "tenant_default",
                task_id=self.request.id,
                status="success",
                data=res
            )

        return res
    except Exception as exc:
        logger.error(f"❌ [Celery GPU] Ошибка рендера для {post_id}: {exc}")
        if callback_url:
            WebhookCallbackManager.send_callback_sync(
                callback_url=callback_url,
                event_type="render_failed",
                tenant_id=tenant_id or "tenant_default",
                task_id=self.request.id,
                status="failed",
                error=str(exc)
            )
        raise exc
