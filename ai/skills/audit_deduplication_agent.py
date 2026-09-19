"""
File: ai/skills/audit_deduplication_agent.py
Агент аудита и семантической дедупликации контента (Audit Agent).
Предотвращает публикацию повторяющихся тем, сравнивая вектор нового поста
с историей последних 10-15 публикаций канала (порог Cosine Similarity >= 0.82).
"""

from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger("AuditDeduplicationAgent")


@dataclass
class DeduplicationVerdict:
    """Вердикт проверки поста на семантическую уникальность."""
    is_duplicate: bool
    similarity_score: float
    matched_post_snippet: Optional[str] = None
    original_topic: str = ""
    suggested_shifted_angle: Optional[str] = None
    reason: str = ""


class AuditDeduplicationAgent:
    """
    Агент аудита и дедупликации:
    1. Векторизует новую тему/текст через paraphrase-multilingual-MiniLM (или встроенный LocalDenseStore).
    2. Вычисляет косинусное сходство с историей публикаций.
    3. При сходстве >= threshold (0.82) блокирует тему и выполняет принудительный сдвиг угла подачи.
    """

    DUPLICATE_THRESHOLD: float = 0.82

    # Матрица альтернативных углов для сдвига драматургии при обнаружении дубля
    DRAMATURGY_SHIFTS: Dict[str, List[str]] = {
        "product_overview": [
            "Разбор частого заблуждения и мифа о продукте (FAQ / Mythbuster)",
            "Реальный кейс клиента с измеримым результатом внедрения (Case Study)",
            "Закулисье технологического процесса и контроль качества (Behind the scenes)"
        ],
        "case_study": [
            "Разбор типичных ошибок при самостоятельном решении задачи (Mistakes breakdown)",
            "Экспертный прогноз и тренды рынка на текущий квартал (Market Analysis)",
            "Чек-лист ключевых критериев выбора надежного подрядчика (Checklist)"
        ],
        "lifestyle_mood": [
            "Интерактивный конструктор выбора образа (Interactive Puzzle / Mix&Match)",
            "Детали сенсорики и тактильных материалов (Sensory Macro Focus)",
            "Советский винтажный или мемный контекст (Humor / Absurd twist)"
        ],
        "general": [
            "Ответ на главный скрытый страх аудитории (Objection handling)",
            "Инструкция: как получить максимум пользы от продукта с первого дня",
            "Сравнение премиального подхода и дешевых аналогов (Honest comparison)"
        ]
    }

    def __init__(self, embedding_dim: int = 384, custom_threshold: float = 0.82):
        self.embedding_dim = embedding_dim
        self.threshold = custom_threshold
        self._model = None
        self._init_embedding_model()

    def _init_embedding_model(self):
        """Легковесная инициализация модели эмбеддингов."""
        try:
            from sentence_transformers import SentenceTransformer
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self._model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", device=device)
            logger.info("✅ AuditDeduplicationAgent: Модель MiniLM-L12 успешно загружена.")
        except Exception:
            self._model = None
            logger.info("ℹ️ AuditDeduplicationAgent: Использование встроенного косинусного кодировщика.")

    def _encode_text(self, text: str) -> List[float]:
        """Кодирует текст в нормированный вектор."""
        if self._model is not None:
            try:
                emb = self._model.encode(text, normalize_embeddings=True)
                return emb.tolist()
            except Exception:
                pass

        # Детерминированный fallback n-gram косинусный энкодер
        vec = [0.0] * self.embedding_dim
        tokens = re.findall(r'\w+', text.lower())
        if not tokens:
            return vec

        for token in tokens:
            idx = abs(hash(token)) % self.embedding_dim
            vec[idx] += 1.0

        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Вычисляет косинусное сходство между двумя нормированными векторами."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        return max(0.0, min(1.0, dot_product))

    def evaluate_uniqueness(
        self,
        proposed_topic_or_text: str,
        recent_channel_posts: List[str],
        topic_category: str = "general"
    ) -> DeduplicationVerdict:
        """
        Сравнивает предложенный пост со списком последних постов канала.
        Возвращает вердикт уникальности и рекомендуемый сдвиг темы в случае дубля.
        """
        if not proposed_topic_or_text or not recent_channel_posts:
            return DeduplicationVerdict(
                is_duplicate=False,
                similarity_score=0.0,
                original_topic=proposed_topic_or_text,
                reason="История публикаций пуста или пост уникален."
            )

        proposed_vec = self._encode_text(proposed_topic_or_text)
        max_similarity = 0.0
        matched_snippet = None

        for post_text in recent_channel_posts:
            post_vec = self._encode_text(post_text)
            sim = self._cosine_similarity(proposed_vec, post_vec)
            if sim > max_similarity:
                max_similarity = sim
                matched_snippet = post_text[:120] + "..." if len(post_text) > 120 else post_text

        max_similarity = round(max_similarity, 3)
        is_duplicate = max_similarity >= self.threshold

        if is_duplicate:
            # Выбор угла для сдвига драматургии
            shifts = self.DRAMATURGY_SHIFTS.get(topic_category, self.DRAMATURGY_SHIFTS["general"])
            shifted_angle = shifts[0]

            reason = (
                f"Обнаружен семантический дубль (сходство {max_similarity} >= {self.threshold}). "
                f"Похожий пост уже публиковался в канале недавно."
            )
            logger.warning(f"🚫 [AuditAgent] {reason} Перенаправление угла: '{shifted_angle}'")

            return DeduplicationVerdict(
                is_duplicate=True,
                similarity_score=max_similarity,
                matched_post_snippet=matched_snippet,
                original_topic=proposed_topic_or_text,
                suggested_shifted_angle=shifted_angle,
                reason=reason
            )

        return DeduplicationVerdict(
            is_duplicate=False,
            similarity_score=max_similarity,
            original_topic=proposed_topic_or_text,
            reason=f"Тема семантически уникальна (макс. сходство {max_similarity} < {self.threshold})."
        )
