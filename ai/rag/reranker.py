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
        
        try:
            from sentence_transformers import CrossEncoder
            # Пробуем загрузить локально без сетевой блокировки
            self.model = CrossEncoder(self.model_name, local_files_only=True)
            print(f"[CrossEncoderReranker] 🟢 Кросс-энкодер '{self.model_name}' успешно загружен локально.")
        except Exception:
            # Fallback на быстрый детерминированный Reranker
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
        q_words = set(query.lower().split())
        for res in candidates:
            chunk_words = set(res.chunk.text.lower().split())
            overlap_ratio = len(q_words.intersection(chunk_words)) / len(q_words) if q_words else 0.0
            
            # Калиброванный скор релевантности
            final_score = (
                0.45 * res.dense_score +
                0.35 * res.sparse_score +
                0.20 * overlap_ratio
            )
            res.rerank_score = min(1.0, max(0.0, final_score))
            
        candidates.sort(key=lambda x: x.rerank_score, reverse=True)
        return candidates[:top_n]
