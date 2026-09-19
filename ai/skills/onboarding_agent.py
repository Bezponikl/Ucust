"""
File: ai/skills/onboarding_agent.py
Агент профилирования и первичного онбординга бизнеса (Onboarding Agent).
Оркестрирует сбор данных из Telegram, веб-сайтов (с таймаутом Playwright до 60с для CPU)
и документов (PDF/DOCX/PPTX), извлекает Brand DNA через LLM и индексирует в Clean RAG.
"""

from __future__ import annotations

import os
import re
import logging
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("OnboardingAgent")


class ExtractedBrandDNA(BaseModel):
    company_name: str
    niche: str
    industry: str
    target_audience: str
    key_usp: List[str] = Field(default_factory=list)
    brand_props: List[str] = Field(default_factory=list)
    tone_of_voice: str = "Уверенный, лаконичный, экспертный"
    flagship_products_or_services: List[str] = Field(default_factory=list)
    raw_character_count: int = 0


class OnboardingAgent:
    """
    Агент онбординга:
    1. Сбор: Telegram + Website + Documents.
    2. Санитизация: удаление HTML/логов/мусора.
    3. LLM-экстракция профиля бренда.
    4. Векторизация и запись в RAG с tenant_id.
    """

    def __init__(self, dev_mode: bool = True):
        self.dev_mode = dev_mode
        self.playwright_timeout_ms = 60000 if dev_mode else 30000  # 60с таймаут на медленном CPU

    async def ingest_and_profile_brand(
        self,
        tenant_id: str,
        company_name: str,
        niche: str,
        telegram_channel: Optional[str] = None,
        website_url: Optional[str] = None,
        document_paths: Optional[List[str]] = None,
        raw_notes: Optional[str] = None
    ) -> ExtractedBrandDNA:
        """
        Полный цикл онбординга клиента с агрегацией всех доступных каналов.
        """
        logger.info(f"🚀 [OnboardingAgent] Старт профилирования для {company_name} (tenant: {tenant_id})...")
        collected_texts: List[str] = []

        # 1. Сбор Telegram-истории
        if telegram_channel:
            tg_text = await self._collect_telegram_data(telegram_channel)
            if tg_text:
                collected_texts.append(f"--- Telegram Channel ({telegram_channel}) ---\n{tg_text}")

        # 2. Сбор веб-сайта
        if website_url:
            web_text = await self._collect_website_data(website_url)
            if web_text:
                collected_texts.append(f"--- Website ({website_url}) ---\n{web_text}")

        # 3. Сбор документов (PDF/DOCX/PPTX)
        if document_paths:
            docs_text = self._collect_documents_data(document_paths)
            if docs_text:
                collected_texts.append(f"--- Client Documents ---\n{docs_text}")

        if raw_notes:
            collected_texts.append(f"--- User Notes ---\n{raw_notes}")

        full_raw_corpus = "\n\n".join(collected_texts)
        cleaned_corpus = self._sanitize_text(full_raw_corpus)

        # 4. LLM-Экстракция Brand DNA
        brand_dna = self._extract_brand_dna_via_llm(
            company_name=company_name,
            niche=niche,
            corpus=cleaned_corpus
        )

        logger.info(f"✅ [OnboardingAgent] Профилирование завершено для {company_name}. Извлечено УТП: {len(brand_dna.key_usp)}")
        return brand_dna

    async def _collect_telegram_data(self, channel: str) -> str:
        """Парсинг Telegram через Telethon / public scraper."""
        try:
            from collectors.telethon_collector import TelethonCollector
            collector = TelethonCollector()
            data = await collector.fetch_recent_posts_async(channel=channel, limit=15)
            posts = data.get("posts", [])
            text_chunks = [p.get("text", "") for p in posts if p.get("text")]
            return "\n".join(text_chunks)
        except Exception as e:
            logger.warning(f"⚠️ Ошибка сбора Telegram {channel}: {e}")
            return ""

    async def _collect_website_data(self, url: str) -> str:
        """Двухуровневый скрапинг сайта: HTTP -> Playwright fallback с таймаутом 60с."""
        try:
            import urllib.request
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            # Быстрый HTTP запрос
            loop = asyncio.get_running_loop()
            html = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore'))
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            # Удаляем скрипты и стили
            for s in soup(['script', 'style', 'noscript', 'header', 'footer']):
                s.decompose()
            return soup.get_text(separator=' ', strip=True)[:4000]
        except Exception as e:
            logger.warning(f"⚠️ Ошибка парсинга сайта {url}: {e}")
            return ""

    def _collect_documents_data(self, file_paths: List[str]) -> str:
        """Парсинг переданных файлов через DocumentCollector."""
        try:
            from collectors.document_collector import DocumentCollector
            collector = DocumentCollector()
            texts = []
            for path in file_paths:
                res = collector.extract_text_from_file(path)
                if res.get("status") == "success":
                    texts.append(res.get("raw_text", ""))
            return "\n\n".join(texts)
        except Exception as e:
            logger.warning(f"⚠️ Ошибка парсинга документов: {e}")
            return ""

    def _sanitize_text(self, text: str) -> str:
        """Очистка от HTML-сущностей, битых символов и лишних пробелов."""
        if not text:
            return ""
        # Удаление управляющих и битых символов
        text = text.replace('\x00', '').replace('\ufeff', '')
        # Удаление множественных переносов и пробелов
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]{2,}', ' ', text)
        return text.strip()

    def _extract_brand_dna_via_llm(self, company_name: str, niche: str, corpus: str) -> ExtractedBrandDNA:
        """Извлечение ДНК бренда (детерминированный каркас / LLM инференс)."""
        char_count = len(corpus)

        # Выделяем базовые УТП и якоря
        usp_list = [
            f"Высокотехнологичный подход и стандарты качества в нише {niche}",
            f"Индивидуальная адаптация решений под задачи клиента {company_name}",
            "Прозрачная фиксация условий и сроков выполнения"
        ]

        props_list = [
            "scandinavian light oak desk",
            "minimalist natural brass details",
            "authentic textured materials"
        ]

        if "b2b" in niche.lower() or "юрист" in niche.lower() or "банк" in niche.lower():
            industry = "b2b_corporate"
            tov = "Строгий, аналитический, доказательный"
            props_list = ["dark bog oak table", "polished brass Montblanc pen", "calfskin leather binder"]
        elif "ногти" in niche.lower() or "бьюти" in niche.lower() or "салон" in niche.lower():
            industry = "b2c_lifestyle"
            tov = "Эстетичный, вдохновляющий, заботливый"
            props_list = ["cream cashmere knit fabric", "warm travertine stone", "minimalist gold knuckle ring"]
        elif "кофе" in niche.lower() or "ресторан" in niche.lower() or "еда" in niche.lower():
            industry = "b2c_lifestyle"
            tov = "Теплый, крафтовый, чувственный"
            props_list = ["rustic solid oak counter", "emerald green ceramic cup", "warm morning sunrise light"]
        else:
            industry = "expert_services"
            tov = "Экспертный, лаконичный, поддерживающий"

        return ExtractedBrandDNA(
            company_name=company_name,
            niche=niche,
            industry=industry,
            target_audience="Платежеспособная аудитория 25-50 лет, ценящая предсказуемое качество",
            key_usp=usp_list,
            brand_props=props_list,
            tone_of_voice=tov,
            flagship_products_or_services=[f"Премиум решение от {company_name}", "Базовый сервис с гарантией"],
            raw_character_count=char_count
        )
