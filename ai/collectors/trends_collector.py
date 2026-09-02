# File: collectors/trends_collector.py
"""
Trends & Memes Collector & Knowledge Base Engine for UCust.AI.
Компенсирует Knowledge Cutoff базовой LLM-модели (2023 г.) без дообучения:
1. Загружает базу актуальных мемов, трендов и сленга 2024-2026 гг. из 'trends_and_memes.json'.
2. Еженедельно обновляет тренды и парсит свежие инфоповоды.
3. Индексирует мемы в Clean RAG категорию 'viral_trends_and_memes'.
4. Адаптирует мемы под B2B/B2C ниши клиентов (мебель, авто, рестораны, бьюти, IT) с Anti-Cringe фильтром.
"""

from __future__ import annotations

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger("trends_collector")


class TrendsAndMemesCollector:
    """
    Коллектор и менеджер вирусных мемов и трендов:
    - Загружает и валидирует файл 'trends_and_memes.json'.
    - Обеспечивает еженедельное обновление трендов.
    - Индексирует знания о трендах в RAG-память.
    """

    DEFAULT_TRENDS_FILE = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "trends_and_memes.json"
    )

    def __init__(self, trends_file_path: Optional[str] = None):
        self.file_path = trends_file_path or self.DEFAULT_TRENDS_FILE
        self._data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Ошибка чтения файла трендов {self.file_path}: {e}")
        return {
            "version": "2026.1.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "memes_and_trends": [],
            "trending_slang_lexicon_2026": {}
        }

    def save_data(self) -> bool:
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения файла трендов: {e}")
            return False

    def get_all_memes(self) -> List[Dict[str, Any]]:
        return self._data.get("memes_and_trends", [])

    def get_slang_lexicon(self) -> Dict[str, str]:
        return self._data.get("trending_slang_lexicon_2026", {})

    def get_trends_for_niche(self, niche: str) -> List[Dict[str, Any]]:
        """
        Подбирает релевантные мемы и форматы, адаптированные под конкретную нишу бизнеса.
        """
        niche_lower = (niche or "").lower()
        matched = []

        # Карта сопоставления ниш с ключами адаптации
        niche_key_map = {
            "мебел": "furniture",
            "кухн": "furniture",
            "стол": "furniture",
            "кофе": "coffee",
            "пекарн": "coffee",
            "ресторан": "restaurants",
            "еда": "restaurants",
            "авто": "auto",
            "сервис": "auto",
            "стоматолог": "dental",
            "клиник": "dental",
            "зуб": "dental",
            "красот": "beauty",
            "салон": "beauty",
            "smm": "it_smm",
            "маркетинг": "it_smm",
            "it": "it_smm"
        }

        active_niche_key = "general"
        for k, v in niche_key_map.items():
            if k in niche_lower:
                active_niche_key = v
                break

        for item in self.get_all_memes():
            adaptations = item.get("business_adaptation", {})
            if active_niche_key in adaptations or "furniture" in adaptations:
                specific_adaptation = adaptations.get(active_niche_key, list(adaptations.values())[0])
                matched.append({
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "emotion": item.get("emotion"),
                    "meaning": item.get("meaning"),
                    "niche_adaptation": specific_adaptation,
                    "viral_hooks": item.get("viral_hooks", []),
                    "anti_cringe_rule": item.get("anti_cringe_rule", "")
                })

        return matched

    def generate_meme_prompt_directive(self, company_name: str, niche: str, meme_id: Optional[str] = None) -> str:
        """
        Формирует готовую промпт-инструкцию для SaigaLLM, чтобы модель 2023 года
        написала современный вирусный пост с точным пониманием мема 2024-2026 гг.
        """
        niche_trends = self.get_trends_for_niche(niche)
        if not niche_trends:
            return ""

        chosen_trend = None
        if meme_id:
            for t in niche_trends:
                if t["id"] == meme_id:
                    chosen_trend = t
                    break

        if not chosen_trend:
            chosen_trend = niche_trends[0]

        slang_sample = list(self.get_slang_lexicon().items())[:4]
        slang_str = ", ".join([f"«{k}» ({v})" for k, v in slang_sample])

        directive = (
            f"🔥 ИНТЕГРАЦИЯ АКТУАЛЬНОГО ТРЕНДА / МЕМА 2024–2026 гг.:\n"
            f"• Название мема: {chosen_trend['name']}\n"
            f"• Суть и контекст: {chosen_trend['meaning']}\n"
            f"• Готовая адаптация под нишу «{niche}»: {chosen_trend['niche_adaptation']}\n"
            f"• Пример вирусного хука: {chosen_trend['viral_hooks'][0] if chosen_trend['viral_hooks'] else ''}\n"
            f"• Anti-Cringe правило: {chosen_trend['anti_cringe_rule']}\n"
            f"• Разрешенный современный сленг (умеренно): {slang_str}\n"
            f"⚡ Задача: Напиши живой, вирусный пост для «{company_name}», органично обыграв этот тренд без фальши."
        )
        return directive

    def update_weekly_trends_sync(self, fresh_trends_feed: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Еженедельный метод обновления базы знаний трендов:
        - Добавляет новые вирусные тренды недели.
        - Обновляет таймштамп 'last_updated'.
        - Синхронизирует актуальные данные в RAG.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        added_count = 0

        if fresh_trends_feed:
            existing_ids = {m["id"] for m in self._data["memes_and_trends"]}
            for trend in fresh_trends_feed:
                if trend.get("id") not in existing_ids:
                    self._data["memes_and_trends"].append(trend)
                    added_count += 1

        self._data["last_updated"] = now_iso
        self.save_data()

        logger.info(f"Тренды успешно обновлены. Добавлено новых: {added_count}, дата: {now_iso}")
        return {
            "status": "success",
            "last_updated": now_iso,
            "total_memes_count": len(self._data["memes_and_trends"]),
            "new_added_count": added_count
        }

    async def index_trends_to_rag(self, rag_pipeline: Any) -> int:
        """
        Индексирует все мемы и тренды в Clean RAG категорию 'viral_trends_and_memes'.
        """
        from rag import Document

        docs = []
        for meme in self.get_all_memes():
            text_payload = (
                f"Мем и Трендовый формат: {meme['name']}\n"
                f"Период: {meme.get('trend_period', '2024-2026')}\n"
                f"Суть мема: {meme['meaning']}\n"
                f"Эмоция: {meme.get('emotion', '')}\n"
                f"Адаптация под бизнес: {json.dumps(meme.get('business_adaptation', {}), ensure_ascii=False)}\n"
                f"Хуки: {' '.join(meme.get('viral_hooks', []))}\n"
                f"Правило: {meme.get('anti_cringe_rule', '')}"
            )
            docs.append(Document(
                doc_id=f"trend_{meme['id']}",
                source="trends_and_memes.json",
                text=text_payload,
                metadata={"category": "viral_trends_and_memes", "meme_id": meme["id"]}
            ))

        # Индексация сленга
        slang_items = [f"{k}: {v}" for k, v in self.get_slang_lexicon().items()]
        docs.append(Document(
            doc_id="trend_slang_lexicon_2026",
            source="trends_and_memes.json",
            text="Словарь современного молодежного и делового сленга 2024-2026 гг:\n" + "\n".join(slang_items),
            metadata={"category": "viral_trends_and_memes", "type": "slang_lexicon"}
        ))

        await rag_pipeline.ingest_documents_async(docs)
        return len(docs)
