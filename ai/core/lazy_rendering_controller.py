"""
File: ai/core/lazy_rendering_controller.py
Стейт-машина и контроллер отложенного рендера (Lazy Rendering State Machine) для UCust AI.
Управляет переходами жизненного цикла постов, математическим расчетом VRAM и очередями задач.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, Field

logger = logging.getLogger("LazyRenderingController")


class SubscriptionTier(str, Enum):
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class IndustryArchetype(str, Enum):
    B2C_LIFESTYLE = "b2c_lifestyle"
    B2B_CORPORATE = "b2b_corporate"
    EXPERT_SERVICES = "expert_services"


class ContentFormat(str, Enum):
    SINGLE_SHOT = "single_shot"
    CAROUSEL_LIGHT = "carousel_light"  # До 3 слайдов
    CAROUSEL_HEAVY = "carousel_heavy"  # До 5 слайдов
    CRYPTEX_PUZZLE = "cryptex_puzzle"  # 4-слойный интерактивный пазл


class PostLifecycleStatus(str, Enum):
    DRAFT_TEXT = "draft_text"            # Сгенерирован только текст и промпты (0 GPU)
    AWAITING_RENDER = "awaiting_render"  # Поставлен в очередь на рендер (аппрув/CRON)
    RENDERING = "rendering"              # Выполняется в ComfyUI
    RENDERED = "rendered"                # Картинки сгенерированы и загружены в хранилище
    PUBLISHED = "published"              # Опубликован в Telegram
    FAILED = "failed"                    # Ошибка генерации / валидации


class ImageGenerationSpec(BaseModel):
    prompt: str
    negative_prompt: str = "plastic, cheap, cluttered, cgi, 3d render, distorted anatomy, blurry, lowres, noise"
    aspect_ratio: str = Field(default="1:1", description="1:1, 4:5, 16:9")
    width: int = 1024
    height: int = 1024
    seed: Optional[int] = None


class PostDraft(BaseModel):
    post_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    brand_id: str
    target_date: datetime
    format: ContentFormat
    status: PostLifecycleStatus = PostLifecycleStatus.DRAFT_TEXT
    text_content: Optional[str] = None
    image_specs: List[ImageGenerationSpec] = Field(default_factory=list)
    rendered_image_urls: List[str] = Field(default_factory=list)
    vram_cost_mb: int = 0
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class VRAMCostCalculator:
    """
    Математический калькулятор аллокации VRAM с защитой от OOM и поддержкой Dev-режима.
    """
    BASE_MODEL_VRAM_MB: int = 6500   # Чекпоинт SDXL / Flux (FP16/BF16 с текстовыми энкодерами)
    VAE_BUFFER_MB: int = 850         # Буфер декодирования VAE

    @classmethod
    def calculate_spec_vram(cls, spec: ImageGenerationSpec, dev_simulation_mode: bool = False) -> int:
        """
        Полный расчет VRAM с учетом веса базовой модели.
        """
        pixel_ratio = (spec.width * spec.height) / (1024 * 1024)
        dynamic_activation_mb = int(1850 * (pixel_ratio ** 1.35))
        
        # Полная физическая стоимость инстанса
        total_vram_mb = cls.BASE_MODEL_VRAM_MB + dynamic_activation_mb + cls.VAE_BUFFER_MB

        if dev_simulation_mode:
            # В dev-режиме возвращаем номинальную оценку для логики без аппаратной блокировки
            return total_vram_mb

        return total_vram_mb

    @classmethod
    def calculate_total_post_vram(
        cls, 
        post: PostDraft, 
        execute_in_batch: bool = False,
        dev_simulation_mode: bool = False
    ) -> int:
        if not post.image_specs:
            return 0

        # Базовый вес модели загружается один раз на процесс
        base_weight = cls.BASE_MODEL_VRAM_MB

        if execute_in_batch and len(post.image_specs) > 1:
            # При параллельном батче буфер активаций масштабируется
            single_act = max(
                int(1850 * (((s.width * s.height) / (1024 * 1024)) ** 1.35)) + cls.VAE_BUFFER_MB 
                for s in post.image_specs
            )
            total_dynamic = int(single_act * (1 + 0.45 * (len(post.image_specs) - 1)))
            return base_weight + total_dynamic
        else:
            # Последовательный рендер (1 кадр за раз): VRAM = вес модели + максимальный одиночный кадр
            max_single_dynamic = max(
                int(1850 * (((s.width * s.height) / (1024 * 1024)) ** 1.35)) + cls.VAE_BUFFER_MB 
                for s in post.image_specs
            )
            return base_weight + max_single_dynamic


class LazyRenderingController:
    """
    Стейт-машина управления жизненным циклом и очередью рендера.
    """

    def __init__(
        self, 
        scheduler_backend: Optional[Any] = None, 
        storage_uploader: Optional[Callable] = None,
        comfy_bridge: Optional[Any] = None,
        dev_simulation_mode: bool = True
    ):
        self.scheduler = scheduler_backend
        self.uploader = storage_uploader or self._default_mock_uploader
        self.dev_simulation_mode = dev_simulation_mode
        self.posts_db: Dict[str, PostDraft] = {}
        
        if comfy_bridge is not None:
            self.comfy_bridge = comfy_bridge
        else:
            try:
                from bridge.comfy_bridge import ComfyUIBridge
                self.comfy_bridge = ComfyUIBridge()
            except ImportError:
                try:
                    from ai.bridge.comfy_bridge import ComfyUIBridge
                    self.comfy_bridge = ComfyUIBridge()
                except ImportError:
                    self.comfy_bridge = None

    def register_draft(self, post: PostDraft, dev_simulation_mode: Optional[bool] = None) -> PostDraft:
        """Сохраняет черновик в БД со статусом DRAFT_TEXT без вызова GPU."""
        is_sim = dev_simulation_mode if dev_simulation_mode is not None else self.dev_simulation_mode
        post.status = PostLifecycleStatus.DRAFT_TEXT
        post.vram_cost_mb = VRAMCostCalculator.calculate_total_post_vram(
            post, 
            dev_simulation_mode=is_sim
        )
        post.updated_at = datetime.now()
        self.posts_db[post.post_id] = post
        logger.info(f"📝 Пост {post.post_id} зарегистрирован как DRAFT_TEXT. VRAM оценка: {post.vram_cost_mb} MB")
        return post

    async def trigger_render(self, post_id: str, trigger_source: str = "manual_approve") -> PostDraft:
        """
        Переводит пост из DRAFT_TEXT в AWAITING_RENDER и отправляет в планировщик.
        """
        post = self.posts_db.get(post_id)
        if not post:
            raise ValueError(f"Пост с ID {post_id} не найден.")

        if post.status not in (PostLifecycleStatus.DRAFT_TEXT, PostLifecycleStatus.FAILED):
            logger.warning(f"⚠️ Пост {post_id} уже в статусе {post.status}, повторный запуск пропущен.")
            return post

        # Переход состояния: DRAFT_TEXT -> AWAITING_RENDER
        post.status = PostLifecycleStatus.AWAITING_RENDER
        post.updated_at = datetime.now()
        logger.info(f"⏳ Пост {post_id} переведен в AWAITING_RENDER (Триггер: {trigger_source}).")

        # Запуск асинхронного воркера рендера
        await self._process_render_job(post)
        return post

    async def _process_render_job(self, post: PostDraft):
        """
        Исполнение задачи: аллокация VRAM -> ComfyUI рендер -> S3 аплоад -> статус RENDERED.
        """
        try:
            # 1. Смена статуса на RENDERING
            post.status = PostLifecycleStatus.RENDERING
            post.updated_at = datetime.now()
            logger.info(f"🎨 Старт GPU рендера для поста {post.post_id} ({len(post.image_specs)} изображений)...")

            rendered_urls = []

            # 2. Исполнение каждой спецификации через ComfyUIBridge
            for idx, spec in enumerate(post.image_specs):
                logger.debug(f"   🖼️ Рендер кадра #{idx + 1} ({spec.width}x{spec.height}, {spec.aspect_ratio})...")
                
                if self.comfy_bridge:
                    raw_image_bytes = await self.comfy_bridge.render_image(
                        spec=spec,
                        post_id=f"{post.post_id}_{idx}",
                        dev_simulation_mode=self.dev_simulation_mode
                    )
                else:
                    raw_image_bytes = await self._execute_comfy_generation(spec)
                
                # 3. Загрузка в S3/хранилище
                s3_url = await self.uploader(raw_image_bytes, f"posts/{post.post_id}/img_{idx + 1}.jpg")
                rendered_urls.append(s3_url)

            # 4. Успешный переход в RENDERED
            post.rendered_image_urls = rendered_urls
            post.status = PostLifecycleStatus.RENDERED
            post.updated_at = datetime.now()
            logger.info(f"✅ Пост {post.post_id} успешно отрендерен. Получено URL: {len(rendered_urls)}")

        except Exception as e:
            post.status = PostLifecycleStatus.FAILED
            post.error_message = str(e)
            post.updated_at = datetime.now()
            logger.error(f"❌ Ошибка рендера поста {post.post_id}: {e}", exc_info=True)

    async def _execute_comfy_generation(self, spec: ImageGenerationSpec) -> bytes:
        """Резервный метод симуляции генерации."""
        await asyncio.sleep(0.05)
        return b"mock_jpeg_binary_data"

    async def _default_mock_uploader(self, data: bytes, destination_key: str) -> str:
        return f"https://s3.ucust.ai/media/{destination_key}"
