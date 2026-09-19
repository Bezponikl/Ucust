"""
File: ai/models/db_models.py
Схемы хранения профилей брендов и векторных чанков знаний.
"""

from __future__ import annotations

from sqlalchemy import Column, String, Text, Float, JSON, Integer
from sqlalchemy.dialects.postgresql import JSONB

try:
    from core.database import Base, IS_POSTGRES
except ImportError:
    from ai.core.database import Base, IS_POSTGRES

try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    class Vector:
        def __init__(self, dim):
            self.dim = dim


class HybridVector(Vector if HAS_PGVECTOR else object):
    """Кастомный тип для фоллбека на SQLite при отсутствии pgvector."""
    def load_dialect_impl(self, dialect):
        if dialect.name == 'sqlite' or not HAS_PGVECTOR:
            return dialect.type_descriptor(JSON())
        return super().load_dialect_impl(dialect)


class BrandProfileModel(Base):
    __tablename__ = "brand_profiles"

    tenant_id = Column(String, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    industry_type = Column(String, nullable=False)
    
    # Хранение извлеченных Brand DNA (Tone of Voice, визуальные якоря)
    tone_of_voice = Column(Text, nullable=True)
    brand_props = Column(JSONB if IS_POSTGRES else JSON, default=list)
    contacts = Column(JSONB if IS_POSTGRES else JSON, default=dict)
    forbidden_topics = Column(JSONB if IS_POSTGRES else JSON, default=list)


class TenantKnowledgeChunk(Base):
    __tablename__ = "tenant_knowledge_chunks"

    chunk_id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    
    source_type = Column(String, nullable=False)  # website, telegram, pdf, notes
    content = Column(Text, nullable=False)
    
    # 384-мерный вектор (paraphrase-multilingual-MiniLM-L12-v2)
    embedding = Column(Vector(384) if (IS_POSTGRES and HAS_PGVECTOR) else JSON, nullable=False)
