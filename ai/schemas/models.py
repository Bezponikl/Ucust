"""
Pydantic-модели и JSON-контракты для комплекса «UCust.AI».
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CopywritingFramework(str, Enum):
    PAS = "PAS"
    AIDA = "AIDA"
    PMHS = "PMHS"  # Pain, More Pain, Hope, Solution


FRAMEWORK_PROMPTS = {
    CopywritingFramework.PAS: """
Твоя задача — написать текст строго по структуре PAS:
1. PROBLEM (Проблема): Начни с боли целевой аудитории. Зацепи внимание вопросом или фактом.
2. AGITATION (Усиление): Покажи, что будет, если проблему не решить. Нагнетай эмоции, добавь конкретики.
3. SOLUTION (Решение): Представь наш продукт/услугу как идеальное и единственно верное решение проблемы. Призови к действию (CTA).
""",
    CopywritingFramework.AIDA: """
Твоя задача — написать текст строго по структуре AIDA:
1. ATTENTION (Внимание): Яркий заголовок или нестандартный факт, заставляющий остановиться.
2. INTEREST (Интерес): Удержи внимание, раскрой интригу, приведи интересные цифры из SWOT-анализа.
3. DESIRE (Желание): Опиши выгоды. Заставь читателя захотеть продукт, покажи трансформацию "до/после".
4. ACTION (Действие): Четкий и понятный призыв к действию (CTA) — что нужно сделать прямо сейчас.
""",
    CopywritingFramework.PMHS: """
Твоя задача — написать текст строго по структуре PMHS:
1. PAIN (Боль): Определи ключевую проблему читателя.
2. MORE PAIN (Еще больше боли): Углуби проблему, покажи негативные последствия бездействия.
3. HOPE (Надежда): Дай надежду на решение и положительные изменения.
4. SOLUTION (Решение): Предложи конкретное решение и призвание к действию (CTA).
""",
}


class QuestionnaireStep1(BaseModel):
    """
    Шаг 1 анкеты пользователя.

    Определяет базовые сведения о компании/бренде для последующей
    работы модулей, включая лингвистический фильтр и
    нейросетевой генеративный модуль.
    """

    business_name: str = Field(..., description="Название компании или бренда")
    mission: str = Field(..., description="Миссия и ценности")
    region: str = Field(..., description="Регион присутствия")


class QuestionnaireStep2(BaseModel):
    """
    Шаг 2 анкеты пользователя.

    Фиксирует демографические и смысловые параметры целевой аудитории.
    """

    target_audience: str = Field(..., description="Описание целевой аудитории")
    demographics: Optional[str] = Field(default=None, description="Агрегированные демографические признаки")
    age_range: str = Field(..., description="Возрастной диапазон аудитории (например, '25-45 лет')")
    geo: str = Field(..., description="География и локация аудитории (например, 'Москва, Санкт-Петербург, РФ')")
    core_audience_description: str = Field(..., description="Подробное описание ядра целевой аудитории")
    pain_points: str = Field(..., description="Боли и потребности аудитории")


class QuestionnaireStep3(BaseModel):
    """
    Шаг 3 анкеты пользователя.

    Определяет тональность, форматы и ограничения, которые далее
    учитываются агентом-копирайтером и векторным хранилищем эмбеддингов.
    """

    tone_of_voice: str = Field(..., description="Тональность коммуникации")
    content_formats: str = Field(..., description="Предпочтительные форматы контента")
    taboo_topics: str = Field(..., description="Запрещенные темы и слова")


class QuestionnaireStep4(BaseModel):
    """
    Шаг 4 анкеты пользователя.

    Содержит целевые показатели и параметры публикаций, которые
    используются при формировании стратегии и сетки контента.
    """

    goals: str = Field(..., description="Цели коммуникации")
    kpi: str = Field(..., description="KPI/метрики эффективности")
    frequency: str = Field(..., description="Частота публикаций")


class QuestionnaireStep5(BaseModel):
    """
    Шаг 5 анкеты пользователя.

    Собирает данные о конкурентах и референсах для SWOT-анализа
    и последующих генеративных модулей.
    """

    competitors: str = Field(..., description="Ключевые конкуренты")
    references: str = Field(..., description="Референсы и примеры")
    additional_notes: str = Field(..., description="Дополнительные комментарии")
    yandex_maps_url: Optional[str] = Field(default=None, description="Ссылка на карточку организации в Яндекс.Картах")
    twogis_url: Optional[str] = Field(default=None, description="Ссылка на карточку организации в 2GIS")


class UserQuestionnaire(BaseModel):
    """
    Полная анкета пользователя из 5 шагов.

    Используется агентом-интервьюером для валидации и сохранения
    в SQL-хранилище и передачи в Java-backend.
    """

    step1: QuestionnaireStep1
    step2: QuestionnaireStep2
    step3: QuestionnaireStep3
    step4: QuestionnaireStep4
    step5: QuestionnaireStep5
    visual_identity: Optional[Dict[str, Any]] = Field(default=None, description="Визуальный ДНК бренда")


class ProjectMetadataSchema(BaseModel):
    """
    Метаданные проекта SMM-кампании.

    Передаются между агентами и могут быть сериализованы в JSON-контракт.
    """

    project_id: Optional[int] = Field(None, description="Идентификатор проекта")
    user_id: Optional[int] = Field(None, description="Идентификатор пользователя")
    name: str = Field(..., description="Название проекта")
    niche: str = Field(..., description="Ниша/отрасль")
    platforms: List[str] = Field(..., description="Платформы продвижения")
    created_at: Optional[datetime] = Field(None, description="Дата создания")


class PublicationHistorySchema(BaseModel):
    """
    Запись истории публикаций.

    Нужна для аудита и контроля повторов в рамках ниши.
    """

    publication_id: Optional[int] = Field(None, description="Идентификатор публикации")
    project_id: int = Field(..., description="Идентификатор проекта")
    platform: str = Field(..., description="Платформа публикации")
    post_text: str = Field(..., description="Текст публикации")
    status: str = Field(..., description="Статус публикации")
    published_at: Optional[datetime] = Field(None, description="Дата публикации")


class CollectorDataSchema(BaseModel):
    """
    Результат работы модулей API-парсинга.

    Объединяет данные из Telethon и vk_api для последующего анализа.
    """

    source: str = Field(..., description="Источник данных")
    payload: dict = Field(..., description="Сырые данные парсинга")


class SWOTResultSchema(BaseModel):
    """
    Результат SWOT-анализа.

    Используется аналитическим агентом как промежуточный артефакт.
    """

    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    summary: str


class SanitizedDataSchema(BaseModel):
    """
    Результат работы лингвистического фильтра.

    Отражает очищенный текст и оценку тональности.
    """

    text: str
    sentiment: str
    notes: List[str]
    technical_log: List[str] = Field(default_factory=list, description="Технический лог работы фильтра")


class StrategyPlanSchema(BaseModel):
    """
    Результат работы нейросетевого генеративного модуля.

    Формирует общую стратегию для копирайтера и визуального директора.
    """

    strategy: str
    risks: List[str]
    recommendations: List[str]
    technical_log: List[str] = Field(default_factory=list, description="Технический лог генерации стратегии")


class PostDraftSchema(BaseModel):
    """
    Черновик поста для публикации.

    Содержит метку уникальности, результаты фактчекинга и ссылки на сгенерированные медиа-артефакты (изображения, видео, аудио).
    """

    text: str
    uniqueness_score: float
    duplicates_found: bool
    fact_checked: bool = Field(default=False, description="Флаг успешного прохождения фактчекинга")
    removed_claims: List[str] = Field(default_factory=list, description="Список удаленных несоответствий/галлюцинаций")
    image_url: Optional[str] = Field(None, description="URL сгенерированного изображения")
    video_url: Optional[str] = Field(None, description="URL сгенерированного видео (LTX-2.3)")
    audio_url: Optional[str] = Field(None, description="URL сгенерированной аудиодорожки (LTX-2.3)")
    media_url: Optional[str] = Field(None, description="Универсальный URL основного медиа-файла")
    local_video_path: Optional[str] = Field(None, description="Локальный путь к видеофайлу на сервере (ComfyUI Output)")
    local_audio_path: Optional[str] = Field(None, description="Локальный путь к аудиофайлу на сервере (ComfyUI Output)")
    local_image_path: Optional[str] = Field(None, description="Локальный путь к файлу изображения на сервере")


class GridTileSchema(BaseModel):
    """
    Элемент контентной сетки (плитка).

    Используется визуальным директором для описания будущего мультимодального видео-контента.
    """

    tile_id: int
    title: str
    description: str


class GridPlanSchema(BaseModel):
    """
    План сетки контента.

    Хранит список плиток и применяется при генерации видео и аудио промптов LTX-2.3.
    """

    tiles: List[GridTileSchema]


class LTX23ConfigSchema(BaseModel):
    """
    Конфигурация 6 обязательных компонентов мультимодальной архитектуры LTX-2.3 (ComfyUI Headless API).
    """

    checkpoint: str = Field(default="ltx-2.3-22b-dev.safetensors", description="1. Базовый чекпоинт (Модель диффузии)")
    text_encoder: str = Field(default="gemma_3_12B_it_fp4_mixed.safetensors", description="2. Текстовый энкодер Google Gemma 3 12B IT FP4")
    lora: str = Field(default="ltx-2.3-22b-distilled-lora-384.safetensors", description="3. LoRA для дистилляции и ускорения генерации")
    spatial_upscaler: str = Field(default="ltx-2.3-spatial-upscaler-x2-1.1.safetensors", description="4. Пространственный апскейлер x2 в latent space")
    video_vae: str = Field(default="LTX23_video_vae_bf16.safetensors", description="5. Видео VAE автоэнкодер")
    audio_vae: str = Field(default="LTX23_audio_vae_bf16.safetensors", description="6. Аудио VAE автоэнкодер")


class LTX23PromptSchema(BaseModel):
    """
    Технический промпт и ComfyUI JSON-workflow для генерации видео со звуком на мультимодальном движке LTX-2.3.
    """

    video_prompt: str = Field(..., description="Промпт для генерации динамического видеоряда")
    audio_prompt: str = Field(..., description="Промпт для генерации синхронной аудиодорожки")
    motion_bucket_id: int = Field(default=127, description="Коэффициент динамики движения")
    fps: int = Field(default=24, description="Частота кадров в секунду")
    aspect_ratio: str = Field(default="16:9", description="Соотношение сторон кадра (16:9, 9:16, 1:1)")
    duration_seconds: float = Field(default=5.0, description="Длительность генерируемого видеоклипа")
    config: LTX23ConfigSchema = Field(default_factory=LTX23ConfigSchema, description="Конфигурация 6 компонентов LTX-2.3")
    comfyui_workflow: Dict[str, Any] = Field(default_factory=dict, description="JSON-workflow граф для ComfyUI Headless API")


class PostGenerationTaskSchema(BaseModel):
    """
    Pydantic-схема задачи для генерации поста.
    """

    user_id: str = Field(..., description="Идентификатор пользователя")
    framework: CopywritingFramework = Field(
        default=CopywritingFramework.PAS,
        description="Фреймворк копирайтинга (PAS, AIDA, PMHS)",
    )


class PublishRequestSchema(BaseModel):
    """
    Input schema for publishing a Human-in-the-Loop post to target platforms (Telegram, VK, Instagram, OK, MAX).
    """

    platforms: Optional[List[str]] = Field(
        default=None,
        description="List of target platforms (e.g., ['telegram', 'vk', 'instagram', 'ok', 'max'])",
    )
    target_platforms: List[str] = Field(
        default=["telegram"],
        description="List of target platforms (e.g., ['telegram', 'vk', 'instagram', 'ok', 'max'])",
    )
    custom_caption: Optional[str] = Field(
        default=None,
        description="Optional custom caption override provided by user prior to publishing",
    )


class PendingPostSchema(BaseModel):
    """
    Export schema for posts awaiting human-in-the-loop review in the web UI.
    """

    job_id: int = Field(..., description="FSM Task / Job ID")
    user_id: str = Field(..., description="External user identifier")
    status: str = Field(..., description="FSM Task Status")
    post_text: Optional[str] = Field(None, description="Generated draft post text")
    video_url: Optional[str] = Field(None, description="URL for video preview")
    audio_url: Optional[str] = Field(None, description="URL for audio preview")
    media_url: Optional[str] = Field(None, description="URL for combined media preview")
    local_video_path: Optional[str] = Field(None, description="Local server file path for video")
    local_audio_path: Optional[str] = Field(None, description="Local server file path for audio")
    uniqueness_score: float = Field(default=1.0, description="Vector uniqueness score")
    duplicates_found: bool = Field(default=False, description="Duplicate detection flag")


class NicheSalesTacticsSchema(BaseModel):
    """
    Схема маркетинговых уловок, психологических триггеров и успешных продаж в нише клиента.
    Используется агентом-аналитиком (Growth Hacker) и сохраняется в базе знаний (Knowledge Base).
    """

    niche_name: str = Field(..., description="Название или описание ниши")
    psychological_hooks: List[str] = Field(
        default_factory=list,
        description="Психологические триггеры и эмоциональные уловки, работающие в этой нише",
    )
    successful_cases: List[str] = Field(
        default_factory=list,
        description="Примеры успешных маркетинговых воронок, кейсов и продаж в нише",
    )
    promotional_mechanics: List[str] = Field(
        default_factory=list,
        description="Рабочие форматы офферов, скидок, лид-магнитов и промо-механик",
    )


class TaskType(str, Enum):
    PROMO_POST = "PROMO_POST"
    REVIEW_REPLY = "REVIEW_REPLY"


class ReviewReplySchema(BaseModel):
    """
    Схема ответа агента-копирайтера на отзыв пользователя с геосервисов (ORM модуль).
    Включает гибридную маршрутизацию для ручного утверждения (Human-in-the-Loop).
    """

    author: str = Field(..., description="Имя автора отзыва")
    rating: int = Field(..., description="Оценка отзыва от 1 до 5")
    original_rating: int = Field(..., description="Исходный числовой рейтинг отзыва (1-5)")
    review_text: str = Field(..., description="Текст отзыва пользователя")
    draft_text: str = Field(..., description="Сгенерированный черновик ответа бренда")
    reply_text: str = Field(..., description="Финальный отклик бренда (утвержденный или авто)")
    sentiment: str = Field(default="neutral", description="Тональность отзыва (positive / negative / neutral)")
    action_needed: bool = Field(default=False, description="Флаг необходимости урегулирования негатива менеджером")
    requires_manual_approval: bool = Field(
        default=True,
        description="Маршрутизация: True если требуется ручное утверждение (1-3 звезды), False при авто-ответе (4-5 звезд)",
    )

