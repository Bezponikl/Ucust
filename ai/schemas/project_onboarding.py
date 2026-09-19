"""
File: ai/schemas/project_onboarding.py
Контракты данных 5 экранов онбординга проекта (Human-in-the-Loop).
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Экран 1: О проекте
class AboutScreen(BaseModel):
    name: str = Field(..., description="Название бренда/компании", example="Кофейня Аромат Зерен")
    niche: str = Field(..., description="Сфера деятельности / ниша", example="Кофейня спешелти и выпечка")
    positioning: str = Field(..., description="УТП и позиционирование бренда", example="Свежая обжарка и крафтовые десерты в уютной атмосфере")
    city: str = Field(default="Москва", description="Город присутствия", example="Санкт-Петербург")
    description: str = Field(default="", description="Краткое описание бизнеса", example="Спешелти-кофейня третьей волны с собственной пекарней")


# Экран 2: Рынок и конкуренты
class MarketScreen(BaseModel):
    competitors: List[str] = Field(default_factory=list, description="Список конкурентов и бенчмарков")
    geography: str = Field(default="Локально", description="Географический охват", example="Санкт-Петербург, Центральный район")
    audience_segment: str = Field(..., description="Сегмент целевой аудитории", example="Жители и гости района 20-45 лет, ценящие вкус и атмосферу")
    trends: List[str] = Field(default_factory=list, description="Актуальные тренды в нише")


# Экран 3: SWOT анализ
class SWOTScreen(BaseModel):
    strengths: List[str] = Field(default_factory=list, description="Сильные стороны (Strengths)")
    weaknesses: List[str] = Field(default_factory=list, description="Слабые стороны (Weaknesses)")
    opportunities: List[str] = Field(default_factory=list, description="Возможности (Opportunities)")
    threats: List[str] = Field(default_factory=list, description="Угрозы (Threats)")


# Экран 4: Услуги и цены
class ServiceItem(BaseModel):
    name: str = Field(..., description="Название услуги / продукта", example="Фирменный капучино")
    description: str = Field(default="", description="Описание позиции", example="На зерне двойной ферментации с овсяным молоком")
    price: str = Field(default="по запросу", description="Стоимость", example="290 руб.")


# Экран 5: Цели контента и Tone of Voice
class GoalsScreen(BaseModel):
    content_goals: List[str] = Field(default_factory=list, description="Цели ведения соцсетей (лидогенерация, удержание, охват)")
    tone_of_voice: List[str] = Field(default_factory=lambda: ["Теплый", "Гостеприимный", "Экспертный"], description="Тональность коммуникации")


# Единый агрегированный профиль (5 экранов)
class ProjectProfileDraft(BaseModel):
    about: AboutScreen
    market: MarketScreen
    swot: SWOTScreen
    services: List[ServiceItem] = Field(default_factory=list)
    goals: GoalsScreen


# -------------------------------------------------------------
# DTO для API эндпоинтов
# -------------------------------------------------------------

class ProjectAnalyzeRequest(BaseModel):
    source_url: Optional[str] = Field(None, description="Ссылка на Telegram-канал, сайт или группу VK", example="https://t.me/kofeina_aromat")
    niche_hint: Optional[str] = Field(None, description="Подсказка ниши от пользователя", example="Кофейня")
    city: Optional[str] = Field("Москва", description="Город", example="Санкт-Петербург")
    files: Optional[List[str]] = Field(default_factory=list, description="Список путей к загруженным файлам (PDF, DOCX)")


class ProjectAnalyzeResponse(BaseModel):
    status: str = "success"
    project_profile_draft: ProjectProfileDraft
    raw_character_count: int = 0


class ProjectCommitRequest(BaseModel):
    data: ProjectProfileDraft = Field(..., description="Отредактированный человеком финальный 5-экранный профиль")


class ProjectCommitResponse(BaseModel):
    status: str = "success"
    project_id: str
    chunks_indexed: int
    message: str = "База знаний проекта успешно сформирована и векторизована в pgvector"
