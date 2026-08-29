# File: skills/competitive_intel.py
"""
Competitive Intelligence Analyst Skill for UCust.AI.
Deconstructs competitor websites, pricing, and offers to build winning SMM counter-strategies.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
import re

class CompetitiveIntelSkill:
    def __init__(self):
        pass

    async def analyze_competitor_async(self, competitor_url: str, my_company_niche: str = "") -> Dict[str, Any]:
        from collectors.website_collector import WebsiteCollector
        collector = WebsiteCollector()
        site_data = await collector.collect_website_async(competitor_url)
        
        if site_data.get("status") == "error":
            return {
                "status": "error",
                "url": competitor_url,
                "error": site_data.get("error")
            }

        title = site_data.get("title", "")
        desc = site_data.get("description", "")
        headings = site_data.get("headings", [])
        key_texts = site_data.get("key_texts", [])
        contacts = site_data.get("contacts", {})
        socials = site_data.get("social_links", {})

        strengths = []
        if len(headings) > 5:
            strengths.append("Разветвленная структура услуг и продуктов")
        if socials.get("telegram") or socials.get("vk"):
            strengths.append("Присутствие в ключевых соцсетях")
        if contacts.get("phones"):
            strengths.append("Прямой контактный телефон на первом экране")
        if not strengths:
            strengths.append("Базовое присутствие в интернете")

        weaknesses = []
        full_text = " ".join(key_texts).lower()
        if not re.search(r"\d+[%₽$]|гарант|кейс|отзыв", full_text):
            weaknesses.append("Слабая доказательная база (мало кейсов с измеримыми цифрами и гарантиями)")
        if not re.search(r"скидк|акци|спец|промо|бесплатн|демо", full_text):
            weaknesses.append("Отсутствие завлекающего лид-магнита или спецпредложения на входе")
        if len(desc) < 40:
            weaknesses.append("Размытое УТП (не сразу понятно, в чем ключевое отличие от других)")
        if not weaknesses:
            weaknesses.append("Консервативный Tone-of-Voice, медленный цикл закрытия лида")

        counter_strategy = {
            "differentiation_angles": [
                f"Позиционирование через скорость и прозрачность (в отличие от {title})",
                "Демонстрация реальных отзывов и видео-кейсов клиентов",
                "Сильный лид-магнит на первое касание с мгновенным результатом"
            ],
            "killer_post_topics": [
                f"3 ошибки при выборе подрядчика в {my_company_niche or 'нише'}, о которых молчат на рынке",
                "Как мы экономим клиентам 40% бюджета за счет автоматизации (наш реальный кейс)",
                "Сравнение: делать по старинке vs внедрить умную систему за 1 день"
            ],
            "recommended_hooks": [
                "Устали переплачивать за стандартные решения? Вот как получить x2 результат...",
                "Почему 80% клиентов уходят от типичных агентств: честный разбор"
            ]
        }

        return {
            "status": "success",
            "competitor_url": site_data.get("url"),
            "competitor_name": title,
            "competitor_uvp": desc or "Не выражено явно",
            "key_offerings": headings[:6],
            "strengths": strengths,
            "weaknesses": weaknesses,
            "social_channels": socials,
            "counter_strategy": counter_strategy,
            "summary_dossier": f"Конкурент: {title}\nУТП: {desc}\nСлабые места: {weaknesses}\nКонтр-стратегия: {counter_strategy['differentiation_angles']}"
        }
