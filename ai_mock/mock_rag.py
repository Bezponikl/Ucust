"""
Mock Clean RAG Store for UCust AI Service.
Provides in-memory search and ingestion without dense embedding models or vector databases.
"""

import time
from typing import Any, Dict, List, Optional


class MockCleanRAGPipeline:
    def __init__(self, min_confidence_threshold: float = 0.65):
        self.min_confidence = min_confidence_threshold
        self.documents: List[Dict[str, Any]] = [
            {
                "id": "doc_base_01",
                "text": "UCust AI — передовая платформа автономного SMM-маркетинга 2026 года с поддержкой генерации постов, изображений и глубокой аналитики.",
                "metadata": {"category": "general", "created_at": "2026-01-01"}
            },
            {
                "id": "doc_base_02",
                "text": "Тарифы UCust: Pro включает 30 генераций в день, Enterprise предоставляет выделенный GPU сервер и безлимитный доступ к API.",
                "metadata": {"category": "pricing", "created_at": "2026-01-01"}
            }
        ]

    async def query(self, query_text: str, top_k: int = 5) -> Dict[str, Any]:
        t_start = time.time()
        # Simple keyword matching
        words = query_text.lower().split()
        scored_docs = []
        for doc in self.documents:
            score = 0.70
            for w in words:
                if w in doc["text"].lower():
                    score += 0.08
            score = min(score, 0.98)
            scored_docs.append({"document": doc, "score": round(score, 2)})

        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        top_results = scored_docs[:top_k]

        return {
            "query": query_text,
            "answer": f"Согласно базе знаний UCust: ответ на вопрос «{query_text}» подтвержден актуальными регламентами 2026 года.",
            "results": top_results,
            "confidence": top_results[0]["score"] if top_results else 0.85,
            "timings": {"search_seconds": 0.02, "total_seconds": round(time.time() - t_start, 3)}
        }

    async def ingest(self, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        count = 0
        for d in docs:
            doc_id = d.get("id") or f"doc_{len(self.documents) + 1}"
            self.documents.append({
                "id": doc_id,
                "text": d.get("text", "") or d.get("content", ""),
                "metadata": d.get("metadata", {})
            })
            count += 1
        return {"status": "success", "ingested_count": count, "total_in_db": len(self.documents)}
