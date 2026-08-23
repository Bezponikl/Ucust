"""
SQLAlchemy v2.0 ORM models for UCust.AI storage layer.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storage.db import Base


class UserProfile(Base):
    """
    ORM model for 5-step user questionnaire profile.
    Stores user_id, niche, city, target_audience and 5-step questionnaire JSON data.
    """

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    niche: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    target_audience: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    step1: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    step2: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    step3: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    step4: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    step5: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    projects: Mapped[List["ProjectMetadata"]] = relationship("ProjectMetadata", back_populates="user_profile")
    content_tasks: Mapped[List["ContentTask"]] = relationship("ContentTask", back_populates="user_profile")


class ProjectMetadata(Base):
    """
    ORM model for project metadata.
    """

    __tablename__ = "project_metadata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    niche: Mapped[str] = mapped_column(String(128), nullable=False)
    platforms: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user_profile: Mapped["UserProfile"] = relationship("UserProfile", back_populates="projects")
    publications: Mapped[List["PublicationHistory"]] = relationship("PublicationHistory", back_populates="project")


class PublicationHistory(Base):
    """
    ORM model for publication history.
    """

    __tablename__ = "publication_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("project_metadata.id"), nullable=False)
    platform: Mapped[str] = mapped_column(String(64), nullable=False)
    post_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    extra_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["ProjectMetadata"] = relationship("ProjectMetadata", back_populates="publications")


class ContentTask(Base):
    """
    ORM model for content pipeline task execution and state tracking.
    """

    __tablename__ = "content_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_profile_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("user_profiles.id"), nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True, default="PENDING")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    post_draft_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_profile: Mapped[Optional["UserProfile"]] = relationship("UserProfile", back_populates="content_tasks")

    @property
    def job_id(self) -> int:
        return self.id

    @property
    def result_payload(self) -> Optional[dict]:
        return self.post_draft_json

    @result_payload.setter
    def result_payload(self, value: Optional[dict]) -> None:
        self.post_draft_json = value


class NicheInsight(Base):
    """
    Глобальная База Знаний маркетинговых уловок и кейсов по нишам (Growth Hacker Knowledge Base).
    Накапливает и переиспользует аналитику между всеми пользователями системы.
    """

    __tablename__ = "niche_insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    niche_slug: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    psychological_hooks: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    successful_cases: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    promotional_mechanics: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OutboxEvent(Base):
    """
    Таблица Transactional Outbox Pattern для гарантии отложенной публикации постов и ответов на отзывы.
    Исключает двойную запись и обеспечивает отказоустойчивость при сбоях соцсетей.
    """

    __tablename__ = "outbox_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    target_platform: Mapped[str] = mapped_column(String(32), nullable=False)  # 'telegram', 'vk', 'yandex_maps', 'twogis'
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)  # 'PROMO_POST', 'REVIEW_REPLY'
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    status: Mapped[str] = mapped_column(String(32), default="PENDING", index=True)  # PENDING, PROCESSING, COMPLETED, FAILED
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    next_attempt_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    published_url: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


__all__ = [
    "UserProfile",
    "ProjectMetadata",
    "PublicationHistory",
    "ContentTask",
    "NicheInsight",
    "OutboxEvent",
]
