"""
Модели данных для Clean RAG подсистемы UCust.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

@dataclass
class Document:
    """Сырой входной документ (пост, статья базы знаний, отзыв)."""
    doc_id: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class Chunk:
    """Семантический чанк документа, подготовленный для индексации."""
    chunk_id: str
    doc_id: str
    text: str
    token_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class RetrievalResult:
    """Результат поиска с оценками релевантности."""
    chunk: Chunk
    dense_score: float = 0.0
    sparse_score: float = 0.0
    hybrid_score: float = 0.0
    rerank_score: float = 0.0


@dataclass
class RAGContext:
    """Финальный упакованный контекст для передачи в генеративную модель (Сайгу)."""
    query: str
    formatted_context: str
    chunks: List[Chunk]
    top_score: float
    has_sufficient_context: bool
    fallback_message: Optional[str] = None
