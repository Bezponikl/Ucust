"""
4. Context Injection & Anti-Hallucination Guard
Форматирование найденных чанков с метаданными и пороговая фильтрация (score >= 0.75).
Защита генеративной модели от галлюцинаций при недостатке релевантных данных.
"""

from typing import List, Optional
from rag.models import RetrievalResult, RAGContext

class AntiHallucinationGuard:
    """
    RAG-Guard & Context Injector:
    1. Проверяет релевантность найденных данных по порогу (score threshold).
    2. Упаковывает чанки с прозрачными метаданными (источник, дата, скор).
    3. Запрещает генеративной модели придумывать факты, если в базе нет ответа.
    """
    
    def __init__(self, min_confidence_threshold: float = 0.75):
        self.min_confidence_threshold = min_confidence_threshold

    def format_and_guard(self, query: str, results: List[RetrievalResult]) -> RAGContext:
        """
        Форматирует контекст и применяет Guardrail защиты от галлюцинаций.
        """
        if not results:
            return RAGContext(
                query=query,
                formatted_context="",
                chunks=[],
                top_score=0.0,
                has_sufficient_context=False,
                fallback_message="В проверенной базе знаний UCust нет подтвержденной информации по вашему запросу. Генерация фактов запрещена во избежание галлюцинаций."
            )
            
        top_score = results[0].rerank_score
        
        # Проверка порога уверенности RAG-Guard
        if top_score < self.min_confidence_threshold:
            return RAGContext(
                query=query,
                formatted_context="",
                chunks=[r.chunk for r in results],
                top_score=top_score,
                has_sufficient_context=False,
                fallback_message=(
                    f"Уровень релевантности найденных документов ({top_score:.2f}) ниже порога безопасности ({self.min_confidence_threshold:.2f}). "
                    "Недостаточно фактуры для гарантированно точного ответа. Додумывание цифр и фактов запрещено."
                )
            )

        # Сборка форматированного контекста с метаданными
        context_blocks = []
        for i, res in enumerate(results):
            chunk = res.chunk
            header = f"[ИСТОЧНИК #{i+1}: {chunk.source} | Дата: {chunk.created_at[:10]} | ID: {chunk.chunk_id} | Score: {res.rerank_score:.2f}]"
            body = chunk.text
            context_blocks.append(f"{header}\n{body}")

        formatted_context_str = "\n\n---\n\n".join(context_blocks)
        
        return RAGContext(
            query=query,
            formatted_context=formatted_context_str,
            chunks=[r.chunk for r in results],
            top_score=top_score,
            has_sufficient_context=True,
            fallback_message=None
        )
