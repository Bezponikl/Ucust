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
    country: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, default="Россия")
    location_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)
    target_audience: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    step1: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    step2: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    step3: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    step4: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    step5: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Ссылки на соцсети, собранные Интервьюером (Telegram, VK и т.д.)
    social_links: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)

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


class OrchestratorTrace(Base):
    """
    ORM model for tracing agent interactions and hashing state.
    Used by the Chief Orchestrator to checkpoint the pipeline stages and recover sessions.
    """
    __tablename__ = "orchestrator_traces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    agent_name: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    payload_hash: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


__all__ = [
    "UserProfile",
    "ProjectMetadata",
    "PublicationHistory",
    "ContentTask",
    "OrchestratorTrace",
]
