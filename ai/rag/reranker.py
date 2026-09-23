"""
3. Reranking (Переранжирование)
Кросс-энкодер для глубокой попарной оценки (query, chunk).
Отсеивает шумные совпадения и выстраивает топ-чанки строго по релевантности.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import os
from typing import List, Tuple
from rag.models import RetrievalResult

class CrossEncoderReranker:
    """
    Модуль переранжирования на базе Cross-Encoder (bge-reranker / ms-marco).
    В отличие от bi-encoder, кросс-энкодер выполняет full-attention 
    между запросом и документом одновременно.
    """
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        self.model_name = model_name
        self.model = None
        
        # Загрузка только если есть явный флаг или доступна модель
        if os.getenv("ENABLE_NEURAL_MODELS", "0") == "1":
            try:
                from sentence_transformers import CrossEncoder
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.model = CrossEncoder(self.model_name, device=device, local_files_only=True)
                print(f"[CrossEncoderReranker] 🟢 Кросс-энкодер '{self.model_name}' успешно загружен на {device.upper()}.")
            except Exception:
                self.model = None
        else:
            self.model = None

    def rerank(self, query: str, candidates: List[RetrievalResult], top_n: int = 3) -> List[RetrievalResult]:
        """
        Переранжирует список кандидатов по точному скору релевантности.
        """
        if not candidates:
            return []
            
        if self.model is not None:
            try:
                pairs = [[query, res.chunk.text] for res in candidates]
                scores = self.model.predict(pairs)
                
                for res, score in zip(candidates, scores):
                    # Приводим к диапазону [0.0, 1.0] через sigmoid при необходимости
                    res.rerank_score = float(1.0 / (1.0 + (2.71828 ** (-float(score))))) if score < 0 or score > 1 else float(score)
                    
                candidates.sort(key=lambda x: x.rerank_score, reverse=True)
                return candidates[:top_n]
            except Exception as e:
                print(f"[CrossEncoderReranker] ⚠️ Ошибка инференса модели: {e}. Применяется fallback-ранжирование.")

        # Fallback Reranking: взвешенное комбинирование dense + sparse + term overlap
        import re
        try:
            from skills.audit_deduplication_agent import AuditDeduplicationAgent
            stem_fn = AuditDeduplicationAgent._stem_russian_word
        except Exception:
            stem_fn = lambda x: x

        stop_words = {"какие", "что", "как", "в", "на", "и", "с", "по", "для"}
        q_words = {stem_fn(w) for w in re.findall(r'\w+', query.lower()) if w not in stop_words and len(w) > 1}

        for res in candidates:
            chunk_words = {stem_fn(w) for w in re.findall(r'\w+', res.chunk.text.lower()) if w not in stop_words and len(w) > 1}
            overlap_ratio = len(q_words.intersection(chunk_words)) / len(q_words) if q_words else 0.0
            
            # Калиброванный скор релевантности (с минимальной базой при наличии совпадений)
            base_score = 0.50 if (res.dense_score > 0 or res.sparse_score > 0 or overlap_ratio > 0) else 0.0
            final_score = (
                base_score +
                0.25 * (res.dense_score or 0.0) +
                0.15 * (res.sparse_score or 0.0) +
                0.35 * overlap_ratio
            )
            res.rerank_score = min(1.0, max(0.0, final_score))
            
        candidates.sort(key=lambda x: x.rerank_score, reverse=True)
        return candidates[:top_n]
