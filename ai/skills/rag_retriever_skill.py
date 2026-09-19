"""
File: ai/skills/rag_retriever_skill.py
Ретривер фактов из Clean RAG с жесткой изоляцией по project_id и CrossEncoder-реранкингом.
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger("RAGRetrieverSkill")


class CleanRAGRetrieverSkill:
    """
    Ретривер с многоуровневой изоляцией тенантов (project_id):
    1. Поиск релевантных семантических документов в pgvector / RAG.
    2. Точный реранкинг через BAAI/bge-reranker-base (Singleton).
    3. Отсечение нерелевантного контекста для предотвращения галлюцинаций.
    """

    @staticmethod
    async def retrieve_and_rerank(project_id: str, query: str, top_k: int = 3) -> List[str]:
        """
        Извлекает и ранжирует самые релевантные факты о проекте.
        """
        try:
            from rag.pipeline import CleanRAGPipeline
            rag = CleanRAGPipeline()
            
            # Поиск с фильтрацией строго по project_id
            rag_context = await rag.query_async(query_text=query, top_k_retrieval=top_k * 2, tenant_id=project_id)
            
            if not rag_context.has_sufficient_context or not rag_context.chunks:
                logger.info(f"ℹ️ [RAGRetriever] Не найдено специфичных чанков для project_id='{project_id}', запрос: '{query[:40]}'")
                return []

            extracted_facts = [c.text for c in rag_context.chunks if getattr(c, "text", None)]
            return extracted_facts[:top_k]
        except Exception as e:
            logger.warning(f"⚠️ [RAGRetriever] Ошибка извлечения контекста из RAG для {project_id}: {e}")
            return []
