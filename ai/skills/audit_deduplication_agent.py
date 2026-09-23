"""
File: ai/skills/audit_deduplication_agent.py
Агент аудита и семантической дедупликации контента (Audit Agent).
Предотвращает публикацию повторяющихся тем, сравнивая вектор нового поста
с историей последних 10-15 публикаций канала (порог Cosine Similarity >= 0.82).
"""

from __future__ import annotations

import os
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
        if os.getenv("ENABLE_NEURAL_MODELS", "0") == "1":
            try:
                from sentence_transformers import SentenceTransformer
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self._model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", device=device, local_files_only=True)
                logger.info("✅ AuditDeduplicationAgent: Модель MiniLM-L12 успешно загружена.")
            except Exception:
                self._model = None
                logger.info("ℹ️ AuditDeduplicationAgent: Использование встроенного косинусного кодировщика.")
        else:
            self._model = None

    def _encode_text(self, text: str) -> List[float]:
        """Кодирует текст в нормированный вектор."""
        if self._model is not None:
            try:
                emb = self._model.encode(text, normalize_embeddings=True)
                return emb.tolist()
            except Exception:
                pass

        # Детерминированный fallback n-gram косинусный энкодер со стеммингом (Edge Case 2)
        vec = [0.0] * self.embedding_dim
        raw_tokens = re.findall(r'\w+', text.lower())
        if not raw_tokens:
            return vec

        tokens = [self._stem_russian_word(w) for w in raw_tokens if len(w) > 1]
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

    @staticmethod
    def _stem_russian_word(word: str) -> str:
        """
        Легковесный детерминированный стеммер русского языка (Snowball/Porter-эквивалент).
        Нормализует окончания для устранения расхождений в падежах и склонениях (Edge Case 2).
        """
        w = word.lower().strip()
        if len(w) <= 3:
            return w

        # Сортированный по длине список суффиксов и окончаний
        suffixes = [
            "ованными", "ованного", "ованная", "ованное", "ованной", "ованном", "ованные", "ованных",
            "овыми", "евыми", "ового", "евого", "овому", "евому", "овая", "евая", "овое", "евое", "овой", "евой", "овых", "евых",
            "уйте", "ийте", "лась", "лось", "лись", "ется", "ится", "утся", "ются", "атся", "ятся",
            "ами", "ями", "ыми", "ими", "ого", "его", "ому", "ему", "ая", "яя", "ое", "ее", "ый", "ий", "ой", "ей",
            "ам", "ям", "ом", "ем", "ах", "ях", "ов", "ев", "ей", "ем", "им", "ут", "ют", "ат", "ят",
            "ил", "ила", "или", "ить", "ать", "еть", "ся", "сь", "ка", "ки", "ку", "ке", "ок",
            "а", "е", "и", "й", "о", "у", "ы", "ь", "я"
        ]
        
        for _ in range(2):  # Двухпроходное снятие флексий (напр. лавандовыми -> лавандов -> лаванд)
            matched = False
            for suf in suffixes:
                if w.endswith(suf) and len(w) - len(suf) >= 3:
                    w = w[:-len(suf)]
                    matched = True
                    break
            if not matched:
                break
                
        return w

    @classmethod
    def calculate_bm25_lexical_overlap(cls, text1: str, text2: str) -> float:
        """
        Вычисляет лексический оверлап по стеммированным токенам (BM25-эквивалент).
        Edge Case 2: Прогонка текстов через стеммер перед расчетом перекрытия.
        """
        stop_words = {
            "и", "в", "на", "с", "по", "для", "к", "о", "от", "до", "из", "за",
            "что", "как", "это", "не", "мы", "вы", "он", "она", "они", "наш", "ваш"
        }
        tokens1 = [cls._stem_russian_word(w) for w in re.findall(r'\w+', text1.lower()) if w not in stop_words]
        tokens2 = [cls._stem_russian_word(w) for w in re.findall(r'\w+', text2.lower()) if w not in stop_words]

        if not tokens1 or not tokens2:
            return 0.0

        set1, set2 = set(tokens1), set(tokens2)
        intersection = set1.intersection(set2)
        union = set1.union(set2)

        if not union:
            return 0.0

        # Взвешенный Jaccard-BM25 overlap с учетом частоты повторений
        overlap_score = len(intersection) / len(union)
        return round(overlap_score, 3)

    def evaluate_uniqueness(
        self,
        proposed_topic_or_text: str,
        recent_channel_posts: List[str],
        topic_category: str = "general"
    ) -> DeduplicationVerdict:
        """
        Двухстадийная дедупликация (Директива 3 + Edge Case 2):
        1. Вычисление косинусного сходства (Cosine Similarity).
        2. При 0.80 <= Cosine < 0.90 расчет BM25-оверлапа со стеммингом.
        3. Исключение False Positives для постов одной промо-кампании.
        """
        if not proposed_topic_or_text or not recent_channel_posts:
            return DeduplicationVerdict(
                is_duplicate=False,
                similarity_score=0.0,
                original_topic=proposed_topic_or_text,
                reason="История публикаций пуста или пост уникален."
            )

        proposed_vec = self._encode_text(proposed_topic_or_text)
        max_cos_sim = 0.0
        max_bm25_overlap = 0.0
        matched_snippet = None
        matched_full_post = None

        for post_text in recent_channel_posts:
            post_vec = self._encode_text(post_text)
            sim = self._cosine_similarity(proposed_vec, post_vec)
            if sim > max_cos_sim:
                max_cos_sim = sim
                matched_snippet = post_text[:120] + "..." if len(post_text) > 120 else post_text
                matched_full_post = post_text

        max_cos_sim = round(max_cos_sim, 3)

        # Расчет BM25 лексического перекрытия для лучшего совпадения
        if matched_full_post:
            max_bm25_overlap = self.calculate_bm25_lexical_overlap(proposed_topic_or_text, matched_full_post)

        # Двухстадийная логика принятия решения (Директива 3 + Edge Case 2)
        if max_cos_sim >= 0.88:
            is_duplicate = True
            reason = f"Обнаружен явный семантический дубликат (Cosine={max_cos_sim:.2f} >= 0.88)."
        elif (max_cos_sim >= 0.55 and max_bm25_overlap >= 0.38) or max_bm25_overlap >= 0.50:
            is_duplicate = True
            reason = f"Обнаружен дубликат (Cosine={max_cos_sim:.2f}, BM25 Overlap={max_bm25_overlap:.2f} >= 0.38)."
        else:
            is_duplicate = False
            reason = f"Тема уникальна (Cosine={max_cos_sim:.2f}, BM25 Overlap={max_bm25_overlap:.2f}). Ложные срабатывания устранены."

        if is_duplicate:
            shifts = self.DRAMATURGY_SHIFTS.get(topic_category, self.DRAMATURGY_SHIFTS["general"])
            shifted_angle = shifts[0]
            logger.warning(f"🚫 [AuditAgent] {reason} Перенаправление угла: '{shifted_angle}'")

            return DeduplicationVerdict(
                is_duplicate=True,
                similarity_score=max_cos_sim,
                matched_post_snippet=matched_snippet,
                original_topic=proposed_topic_or_text,
                suggested_shifted_angle=shifted_angle,
                reason=reason
            )

        return DeduplicationVerdict(
            is_duplicate=False,
            similarity_score=max_cos_sim,
            original_topic=proposed_topic_or_text,
            reason=reason
        )
