"""
File: ai/skills/diff_applier.py
Модуль точечного применения правок (JSON Diff Applier) с поддержкой нечеткого поиска (Fuzzy Matching).
Позволяет точечно устранять галлюцинации и ошибки без полной перегенерации текста.
"""

from __future__ import annotations

import difflib
import logging
import re
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("DiffApplier")


class DiffApplier:
    """
    Легковесный детерминированный узел наложения JSON-патчей:
    - Точечно заменяет/удаляет/вставляет фрагменты текста
    - Поддерживает Fuzzy Matching (порог сходства >= 0.85) при расхождениях в пунктуации/символах
    - Имеет fallback на замену ближайшего абзаца при несовпадении точной строки
    """

    DEFAULT_SIMILARITY_THRESHOLD: float = 0.85

    @classmethod
    def apply_patches(
        cls,
        source_text: str,
        edits: List[Dict[str, Any]],
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD
    ) -> Tuple[str, int]:
        """
        Применяет список правок к исходному тексту.
        
        edits: список словарей вида:
        {
            "target_sentence": "предложение с ошибкой",
            "action": "REPLACE" | "DELETE" | "INSERT",
            "replacement": "исправленный фрагмент"
        }
        
        Возвращает: (обновленный_текст, количество_успешно_примененных_правок)
        """
        if not edits or not source_text:
            return source_text, 0

        updated_text = source_text
        applied_count = 0

        for edit in edits:
            target = edit.get("target_sentence") or edit.get("target") or ""
            action = (edit.get("action") or "REPLACE").upper()
            replacement = edit.get("replacement") or ""

            if not target and action != "INSERT":
                continue

            # 1. Попытка точной замены
            if target in updated_text:
                if action == "REPLACE":
                    updated_text = updated_text.replace(target, replacement, 1)
                elif action == "DELETE":
                    updated_text = updated_text.replace(target, "", 1)
                applied_count += 1
                logger.info(f"✅ [DiffApplier] Точная замена ({action}): '{target[:40]}...' -> '{replacement[:40]}...'")
                continue

            # 2. Нечеткий поиск (Fuzzy Matching) по предложениям
            best_match, best_score, span = cls._find_fuzzy_match(
                updated_text, target, threshold=similarity_threshold
            )

            if best_match and span:
                start_idx, end_idx = span
                if action == "REPLACE":
                    updated_text = updated_text[:start_idx] + replacement + updated_text[end_idx:]
                elif action == "DELETE":
                    updated_text = updated_text[:start_idx] + updated_text[end_idx:]
                applied_count += 1
                logger.info(f"🔍 [DiffApplier] Нечеткая замена (score={best_score:.2f}, {action}): '{best_match[:40]}...' -> '{replacement[:40]}...'")
                continue

            # 3. Fallback: замена ближайшего абзаца
            paragraph_match, p_span = cls._find_closest_paragraph(updated_text, target)
            if paragraph_match and p_span:
                start_idx, end_idx = p_span
                if action == "REPLACE":
                    updated_text = updated_text[:start_idx] + replacement + updated_text[end_idx:]
                elif action == "DELETE":
                    updated_text = updated_text[:start_idx] + updated_text[end_idx:]
                applied_count += 1
                logger.warning(f"⚠️ [DiffApplier] Fallback на замену абзаца: '{paragraph_match[:40]}...'")
            else:
                logger.warning(f"❌ [DiffApplier] Не удалось локализовать цель для правки: '{target[:50]}'")

        # Нормализация лишних пробелов и переносов строк после удалений
        updated_text = re.sub(r'[ \t]+', ' ', updated_text)
        updated_text = re.sub(r'\n{3,}', '\n\n', updated_text).strip()
        return updated_text, applied_count

    @classmethod
    def _find_fuzzy_match(
        cls,
        text: str,
        target: str,
        threshold: float = 0.85
    ) -> Tuple[Optional[str], float, Optional[Tuple[int, int]]]:
        """Разбивает текст на предложения и находит наиболее похожее через SequenceMatcher."""
        # Разделение на предложения с сохранением позиций
        sentence_regex = re.compile(r'[^.!?\n]+[.!?\n]?')
        matches = list(sentence_regex.finditer(text))

        best_score = 0.0
        best_sentence = None
        best_span = None

        target_norm = cls._normalize(target)

        for match in matches:
            candidate = match.group(0)
            candidate_norm = cls._normalize(candidate)
            
            score = difflib.SequenceMatcher(None, target_norm, candidate_norm).ratio()
            if score > best_score:
                best_score = score
                best_sentence = candidate
                best_span = (match.start(), match.end())

        if best_score >= threshold:
            return best_sentence, best_score, best_span

        return None, best_score, None

    @classmethod
    def _find_closest_paragraph(
        cls,
        text: str,
        target: str
    ) -> Tuple[Optional[str], Optional[Tuple[int, int]]]:
        """Ищет абзац с наибольшим пересечением слов с целевой строкой."""
        paragraphs = list(re.finditer(r'[^\n]+', text))
        target_words = set(re.findall(r'\w+', target.lower()))
        if not target_words:
            return None, None

        best_overlap = 0
        best_para = None
        best_span = None

        for p_match in paragraphs:
            para = p_match.group(0)
            para_words = set(re.findall(r'\w+', para.lower()))
            overlap = len(target_words.intersection(para_words))
            if overlap > best_overlap:
                best_overlap = overlap
                best_para = para
                best_span = (p_match.start(), p_match.end())

        if best_overlap >= max(2, len(target_words) // 3):
            return best_para, best_span
        return None, None

    @staticmethod
    def _normalize(text: str) -> str:
        """Нормализация для нечеткого сравнения (удаление пунктуации и приведение к нижнему регистру)."""
        return re.sub(r'[^\w\s]', '', text.lower()).strip()
