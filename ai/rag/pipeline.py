"""
Clean RAG Pipeline Facade with Multi-Tenant Partitioning
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import asyncio
from typing import List, Dict, Any, Optional
from rag.models import Document, Chunk, RAGContext
from rag.sanitizer import SemanticChunker, TextSanitizer
from rag.hybrid_retriever import HybridRetriever
from rag.reranker import CrossEncoderReranker
from rag.guard import AntiHallucinationGuard

class CleanRAGPipeline:
    """
    Высоконадежный локальный Clean RAG пайплайн для UCust с жесткой изоляцией tenant_id.
    """
    def __init__(
        self, 
        target_chunk_tokens: int = 350,
        overlap_tokens: int = 50,
        min_confidence_threshold: float = 0.55,
        reranker_model: str = "BAAI/bge-reranker-base"
    ):
        self.chunker = SemanticChunker(target_chunk_tokens, overlap_tokens)
        self.retriever = HybridRetriever()
        self.reranker = CrossEncoderReranker(reranker_model)
        self.guard = AntiHallucinationGuard(min_confidence_threshold)

    def ingest_documents(self, documents: List[Document]) -> int:
        all_chunks: List[Chunk] = []
        for doc in documents:
            chunks = self.chunker.chunk_document(doc)
            all_chunks.extend(chunks)
            
        if all_chunks:
            self.retriever.index_chunks(all_chunks)
            print(f"[CleanRAGPipeline] 📥 Успешно проиндексировано {len(all_chunks)} семантических чанков из {len(documents)} документов.")
            
        return len(all_chunks)

    async def ingest_documents_async(self, documents: List[Document]) -> int:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.ingest_documents, documents)

    def query(self, query_text: str, top_k_retrieval: int = 6, top_n_rerank: int = 3, tenant_id: Optional[str] = None) -> RAGContext:
        cleaned_query = TextSanitizer.sanitize(query_text)
        if not cleaned_query:
            return self.guard.format_and_guard(query_text, [])

        # 1. Гибридный поиск с Multi-Tenant фильтром
        retrieved_candidates = self.retriever.hybrid_search(cleaned_query, top_k=top_k_retrieval, tenant_id=tenant_id)
        
        # 2. Кросс-энкодер переранжирование
        reranked_results = self.reranker.rerank(cleaned_query, retrieved_candidates, top_n=top_n_rerank)
        
        # 3. Guardrail защиты от галлюцинаций
        rag_context = self.guard.format_and_guard(cleaned_query, reranked_results)
        
        return rag_context

    async def query_async(self, query_text: str, top_k_retrieval: int = 6, top_n_rerank: int = 3, tenant_id: Optional[str] = None) -> RAGContext:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.query, query_text, top_k_retrieval, top_n_rerank, tenant_id)
