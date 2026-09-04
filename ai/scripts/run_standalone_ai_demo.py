"""
run_standalone_ai_demo.py
======================================================================
Автономный запуск AI-контура UCust (STANDALONE РЕЖИМ БЕЗ БЭКЕНДА):
Демонстрация генерации недельного контент-плана для клиента:
- Ниша: «Кондитерская и пекарня "Bakery Mood"» (г. Москва).
- 5 дней (Понедельник - Пятница).
- Соблюдение 2-режимной модели: 80% Студийное фото + 20% Текст/Интерактив.
- Воронки TOFU -> MOFU -> BOFU и 5 ступеней узнавания Бена Ханта.
- Хэштеги конкурентов ниши без утечек (#UCust).
- Защита от додумываний (ZeroAssumptionsGuard) и фильтрация моделей (TechSanitizer).
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio
from datetime import datetime, timedelta

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from skills.saiga_llm import SaigaLLMSkill
from skills.object_storytelling import ObjectKnowledgeStoryteller
from skills.competitor_hashtags import NicheCompetitorHashtagEngine
from skills.tech_sanitizer import TechSanitizer
from skills.zero_assumptions_guard import ZeroAssumptionsGuard
from skills.marketing_frameworks import MarketingFrameworkDirector, MarketingFramework, HuntStage


async def run_standalone_campaign():
    print("=" * 80)
    print("🥐 АВТОНОМНАЯ ГЕНЕРАЦИЯ КОНТЕНТ-ПЛАНА (STANDALONE БЕЗ БЭКЕНДА)")
    print("🏢 Бренд: «Bakery Mood» | Ниша: Кондитерская и пекарня | Город: Москва")
    print("📅 Период: 5 рабочих дней (Пн–Пт) | Баланс: 80% Фото + 20% Текст/Интерактив")
    print("=" * 80)

    saiga = SaigaLLMSkill()
    start_monday = datetime(2026, 9, 7) # Понедельник

    plan_schedule = [
        {
            "day": "Понедельник (09:00)",
            "funnel": "TOFU (Охват / Верх воронки)",
            "hunt_stage": "Stage 1: Unaware (Привлечение внимания)",
            "media_type": "PHOTO (Студийное макро-фото)",
            "topic": "Идеальный ролл с миндалем и кремом Франжипан",
            "format": "equation_hook"
        },
        {
            "day": "Вторник (14:30)",
            "funnel": "TOFU (Охват / Польза)",
            "hunt_stage": "Stage 2: Problem Aware (Снятие усталости и стресса)",
            "media_type": "PHOTO (Студийное фото среза)",
            "topic": "Краффин с корицей и сотовой слоистостью",
            "format": "did_you_know"
        },
        {
            "day": "Среда (11:00)",
            "funnel": "MOFU (Прогрев / Экспертность)",
            "hunt_stage": "Stage 3: Solution Aware (Секреты рецептуры)",
            "media_type": "PHOTO (Интерьер и десерты)",
            "topic": "Классический аутентичный Тирамису из Тревизо",
            "format": "storytelling"
        },
        {
            "day": "Четверг (16:00)",
            "funnel": "TOFU (Вовлечение / Интерактив)",
            "hunt_stage": "Stage 4: Product Aware (Выбор любимого вкуса)",
            "media_type": "TEXT_ONLY (Быстрый блиц-опрос)",
            "topic": "Битва вкусов к утреннему кофе",
            "format": "interactive_poll"
        },
        {
            "day": "Пятница (18:00)",
            "funnel": "BOFU (Продажа / Закрытие сделки)",
            "hunt_stage": "Stage 5: Most Aware (Готовность к покупке)",
            "media_type": "PHOTO (Подарочный сет десертов)",
            "topic": "Свежие сеты выпечки на выходные с промокодом",
            "format": "direct_offer"
        }
    ]

    for idx, item in enumerate(plan_schedule, 1):
        print(f"\n{'─' * 80}")
        print(f"📌 ДЕНЬ #{idx}: {item['day']} — {item['funnel']}")
        print(f"🎯 Ступень Ханта: {item['hunt_stage']}")
        print(f"📷 Медиа-формат: {item['media_type']}")
        print(f"📝 Тема: {item['topic']}")
        print(f"{'─' * 80}")

        # Генерация в зависимости от формата
        if item["format"] == "equation_hook":
            post_data = ObjectKnowledgeStoryteller.generate_equation_formula_post(
                topic=item["topic"],
                company_name="Bakery Mood",
                niche="Кондитерская и пекарня",
                city="Москва"
            )
            text = post_data["post_text"]
            hashtags = post_data["hashtags"]
            prompt = post_data["visual_prompt"]

        elif item["format"] == "did_you_know":
            post_data = ObjectKnowledgeStoryteller.generate_curated_did_you_know_post(
                topic=item["topic"],
                company_name="Bakery Mood",
                niche="Кондитерская и пекарня",
                city="Москва"
            )
            text = post_data["post_text"]
            hashtags = post_data["hashtags"]
            prompt = post_data["visual_prompt"]

        elif item["format"] == "storytelling":
            gen = saiga.generate_smm_post(
                topic=item["topic"],
                company_name="Bakery Mood",
                niche="Кондитерская и пекарня",
                city="Москва"
            )
            text = gen["post_text"]
            hashtags = gen["hashtags"]
            prompt = gen["visual_prompt"]

        elif item["format"] == "interactive_poll":
            text = (
                "☕️ Битва десертов к вашей чашке кофе:\n\n"
                "1️⃣ 🥐 Хрустящий краффин с пряной корицей\n"
                "2️⃣ 🌰 Ролл с нежной миндальной пастой и лепестками\n\n"
                "Какой десерт выбираете сегодня для идеального настроения? Пишите цифру 1 или 2 в комментариях! 👇✨"
            )
            hashtags = NicheCompetitorHashtagEngine.get_competitor_hashtags(
                niche="Кондитерская и пекарня",
                topic=item["topic"],
                city="Москва",
                company_name="Bakery Mood"
            )
            prompt = "None (Текстовый интерактивный пост / Стильная минималистичная карточка-опрос)"

        elif item["format"] == "direct_offer":
            gen = saiga.generate_smm_post(
                topic=item["topic"],
                company_name="Bakery Mood",
                niche="Кондитерская и пекарня",
                city="Москва"
            )
            text = gen["post_text"]
            hashtags = gen["hashtags"]
            prompt = gen["visual_prompt"]

        # Финальная очистка безопасности
        clean_text = TechSanitizer.sanitize_text(text)
        safe_text = ZeroAssumptionsGuard.sanitize_assumptions(clean_text)

        print(f"\n📄 ТЕКСТ ДЛЯ ПУБЛИКАЦИИ:\n{safe_text}")
        print(f"\n🏷️ ХЭШТЕГИ КОНКУРЕНТОВ:\n{hashtags}")
        if item["media_type"] != "TEXT_ONLY":
            print(f"\n🎨 ПРОМПТ ДЛЯ ФОТОГЕНЕРАТОРА (FLUX/SDXL):\n{prompt}")

    print("\n" + "=" * 80)
    print("🎉 АВТОНОМНЫЙ КОНТЕНТ-ПЛАН НА НЕДЕЛЮ ПОЛНОСТЬЮ СФОРМИРОВАН БЕЗ УЧАСТИЯ БЭКЕНДА!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_standalone_campaign())
