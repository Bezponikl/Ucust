# File: ai/skills/visual_knowledge_researcher.py
"""
VisualKnowledgeResearcher — Модуль параллельного поиска и визуальной спецификации объектов,
одежды, материалов и стилей для сверхточного промпт-инжиниринга в ComfyUI.
"""

from __future__ import annotations

import os
import re
import asyncio
import logging
from typing import Dict, Any, List, Optional

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger("visual_knowledge_researcher")


class VisualKnowledgeResearcher:
    """
    Исследователь визуальных деталей и точных спецификаций одежды / предметов.
    Извлекает конструктивные особенности, крой, текстуры тканей, фурнитуру
    и переводит их в фотореалистичные дескрипторы для ComfyUI.
    """

    # Предустановленная верифицированная база точных спецификаций сложных визуальных объектов
    CURATED_VISUAL_SPECS: Dict[str, Dict[str, str]] = {
        "микробикини": {
            "en_term": "micro-bikini",
            "visual_description": "exquisite minimalist micro-bikini swimwear crafted from shimmering spandex with ultra-thin elastic string ties, tiny triangular fabric coverage designed for maximum tan lines, delicate stitching and authentic fabric stretch",
            "text_story": "ультра-минималистичный крой для идеального загара, тонкие завязки и премиальный металлизированный эластан"
        },
        "стринги": {
            "en_term": "extreme thong swimsuit / string thong",
            "visual_description": "ultra-minimalist high-cut Brazilian thong swimwear with delicate side ties, smooth seamless fabric edges and elegant silhouette",
            "text_story": "высокий вырез, подчеркивающий силуэт, и безупречная посадка из бесшовных премиальных материалов"
        },
        "купальник для загара": {
            "en_term": "tanning swimsuit / minimalist bandeau bikini",
            "visual_description": "minimalist tanning bikini with strapless bandeau top and ultra-low coverage bottoms designed to minimize tan lines, high-grade quick-dry matte lycra",
            "text_story": "модель бандо без бретелей для ровного бронзового загара из быстросохнущей матовой лайкры"
        },
        "кимоно": {
            "en_term": "Mulberry silk kimono robe",
            "visual_description": "flowing luxurious Mulberry silk kimono robe with smooth lustrous sheen, elegant wide sleeves and delicate golden embroidery accents",
            "text_story": "струящийся натуральный шелк малбери, изысканный блеск и свободный силуэт для моментов домашней роскоши"
        },
        "корсет": {
            "en_term": "structured Victorian boned corset",
            "visual_description": "tailored satin corset with structured vertical boning channels, delicate lace trim and satin back ribbon lacing",
            "text_story": "скульптурирующий силуэт на гибких косточках с атласной шнуровкой и нежным кружевом"
        },
        "дубайский шоколад": {
            "en_term": "Dubai Fix pistachio kataifi chocolate",
            "visual_description": "thick artisanal milk chocolate bar broken open showing vibrant emerald pistachio cream layered with crisp golden toasted kataifi pastry threads",
            "text_story": "хрустящее золотистое тесто катаифи, насыщенная натуральная фисташковая паста и премиальный молочный шоколад"
        },
        "франжипан": {
            "en_term": "Frangipane almond cream pastry",
            "visual_description": "golden layered puff pastry roll filled with rich velvety almond frangipane cream, topped with toasted caramelized sliced almond flakes and fine powdered sugar",
            "text_story": "классический французский крем франжипан из тертого отборного миндаля, запеченный в хрустящем слоеном тесте"
        },
        "горячие камни": {
            "en_term": "basalt hot stones SPA therapy",
            "visual_description": "smooth polished volcanic black basalt massage stones glistening with aromatic botanical essential oils placed along spine",
            "text_story": "прогретые базальтовые камни вулканического происхождения, глубоко прогревающие мышцы и снимающие стресс"
        }
    }

    @classmethod
    async def research_visual_spec(cls, topic: str) -> Dict[str, str]:
        """
        Ищет точную визуальную специфику для объекта / одежды.
        Сначала проверяет локальную базу, при необходимости делает запрос к поисковику.
        """
        if not topic:
            return {}

        topic_lower = topic.lower()

        # 1. Проверяем локальную экспертную базу
        for key, spec in cls.CURATED_VISUAL_SPECS.items():
            if key in topic_lower:
                logger.info(f"[VisualKnowledgeResearcher] 🎯 Найдена точная спецификация для «{key}»")
                return spec

        # 2. Если сложный термин не найден — выполняем параллельный веб-поиск через Tavily / DuckDuckGo
        try:
            tavily_key = os.getenv("TRAVITY_API_KEY") or os.getenv("TAVILY_API_KEY")
            if tavily_key and httpx is not None:
                async with httpx.AsyncClient(timeout=6.0) as client:
                    resp = await client.post(
                        "https://api.tavily.com/search",
                        json={
                            "api_key": tavily_key,
                            "query": f"what is {topic} clothing design visual details fabrics",
                            "max_results": 2
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        results = data.get("results", [])
                        if results:
                            snippet = results[0].get("content", "")[:200]
                            return {
                                "en_term": topic,
                                "visual_description": f"authentic detailed representation of {topic}, {snippet}",
                                "text_story": f"авторский дизайн и внимание к деталям: {topic}"
                            }
        except Exception as ex:
            logger.debug(f"[VisualKnowledgeResearcher] Web search fallback: {ex}")

        # Fallback по умолчанию
        return {
            "en_term": topic,
            "visual_description": f"authentic representation of {topic} with accurate physical textures and materials",
            "text_story": topic
        }

    @classmethod
    def research_visual_spec_sync(cls, topic: str) -> Dict[str, str]:
        """
        Синхронная обертка для быстрого вызова из генераторов промптов.
        """
        topic_lower = topic.lower()
        for key, spec in cls.CURATED_VISUAL_SPECS.items():
            if key in topic_lower:
                return spec
        return {
            "en_term": topic,
            "visual_description": f"authentic commercial representation of {topic}",
            "text_story": topic
        }
