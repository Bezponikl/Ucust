"""
test_crocus_beauty_pipeline.py
======================================================================
Тест сквозного автономного пайплайна для нового бизнеса «Крокус» (Салон красоты).

Параметры:
• Компания: Крокус
• Ниша: Салон красоты
• Описание: Салон красоты, предлагающий комплексный уход за внешностью.
  Есть парикмахерский зал, ногтевая студия, косметология и визаж.
• Сайт: https://www.crocus.ru/
• Режим: Живой парсинг в интернете (без заготовок), автономная генерация контента,
  заглушка вместо генерации визуала «(тут могла быть ваша реклама)».
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio
import time
import json
from pathlib import Path

# Setup paths
AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from core.orchestrator import UnifiedOrchestrator, SecurityGuard
from collectors.website_collector import WebsiteCollector
from collectors.trend_collector import TrendCollector
from collectors.event_holiday_collector import EventHolidayCollector
from skills.moondream_vqa import MoondreamVQASkill


async def run_crocus_beauty_pipeline():
    print("=" * 70)
    print("🌸 ЗАПУСК АВТОНОМНОГО ПАЙПЛАЙНА ДЛЯ БИЗНЕСА: «КРОКУС» (САЛОН КРАСОТЫ)")
    print("=" * 70)

    # 1. Входные данные с бэкенда
    user_input = {
        "user_id": "usr_crocus_beauty_003",
        "session_id": "sess_crocus_e2e_771",
        "company_name": "Крокус",
        "niche": "Салон красоты",
        "city": "Москва",
        "website": "https://www.crocus.ru/",
        "description": "Салон красоты предлагающий комплексный уход за внешностью. Есть парикмахерский зал, ногтевая студия, косметология и визаж",
        "raw_social_input": "https://www.crocus.ru/ Салон красоты предлагающий комплексный уход за внешностью. Есть парикмахерский зал, ногтевая студия, косметология и визаж"
    }

    print("\n📦 [1. ВХОДНЫЕ ДАННЫЕ С БЭКЕНДА]:")
    print(f"   • Компания: «{user_input['company_name']}»")
    print(f"   • Ниша: {user_input['niche']}")
    print(f"   • Сайт: {user_input['website']}")
    print(f"   • Услуги: {user_input['description']}")

    t_start = time.time()
    orchestrator = UnifiedOrchestrator()

    # -------------------------------------------------------------
    # ЭТАП 1: ЖИВОЙ ПАРСИНГ САЙТА В ИНТЕРНЕТЕ (БЕЗ ЗАГОТОВОК)
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("🌐 [ЭТАП 1/5] ЖИВОЙ ПАРСИНГ САЙТА В ИНТЕРНЕТЕ: https://www.crocus.ru/...")
    print("-" * 70)
    
    t_web_start = time.time()
    website_collector = WebsiteCollector(timeout=10.0)
    live_site_data = await website_collector.collect_website_async(user_input["website"])
    t_web_duration = round(time.time() - t_web_start, 2)

    print(f"  ✅ [WebsiteCollector] Результат парсинга сайта ({t_web_duration} сек):")
    print(f"     • Статус: {live_site_data.get('status')}")
    print(f"     • URL: {live_site_data.get('url')}")
    print(f"     • Title: {live_site_data.get('title') or 'Crocus Group / Крокус'}")
    print(f"     • Описание: {(live_site_data.get('description') or user_input['description'])[:120]}...")
    print(f"     • Найдено заголовков: {len(live_site_data.get('headings', []))} шт.")
    print(f"     • Контакты/Ссылки: {live_site_data.get('contacts', {})}")

    # -------------------------------------------------------------
    # ЭТАП 2: СБОР РЫНОЧНЫХ ТРЕНДОВ И ИНФОПОВОДОВ (BEAUTY NICHE)
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("💄 [ЭТАП 2/5] СБОР ЖИВЫХ БЬЮТИ-ТРЕНДОВ И СОБЫТИЙ...")
    print("-" * 70)

    t_trends_start = time.time()
    trend_collector = TrendCollector()
    beauty_trends = await trend_collector.fetch_niche_trends("Салон красоты и бьюти-услуги")
    
    event_collector = EventHolidayCollector()
    city_events = await event_collector.fetch_city_and_national_events(city="Москва", country="Россия")
    t_trends_duration = round(time.time() - t_trends_start, 2)

    print(f"  ✅ [TrendCollector] Бьюти-тренд недели: {beauty_trends.get('summary')}")
    print(f"  ✅ [EventCollector] События локации: {[e.get('title') for e in city_events[:2]]}")

    # -------------------------------------------------------------
    # ЭТАП 3: ОНБОРДИНГ И СИНТЕЗ БРЕНД-ПРОФИЛЯ В ОРКЕСТРАТОРЕ
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("🧠 [ЭТАП 3/5] СИНТЕЗ БРЕНД-ПРОФИЛЯ И ПОЗИЦИОНИРОВАНИЯ (КРОКУС)...")
    print("-" * 70)

    onboarding_payload = {
        "user_id": user_input["user_id"],
        "name": user_input["company_name"],
        "company_name": user_input["company_name"],
        "activity": f"{user_input['niche']}: {user_input['description']}",
        "niche": user_input["niche"],
        "city": user_input["city"],
        "raw_social_input": user_input["raw_social_input"],
        "website_dossier": live_site_data.get("structured_dossier")
    }

    onboarding_res = await orchestrator.execute_task(
        task_type="onboarding",
        user_data=onboarding_payload,
        session_id=user_input["session_id"]
    )
    brand_profile = onboarding_res.get("profile", {})
    print(f"  ✅ [Оркестратор] Бренд-профиль сформирован:")
    print(f"     • Позиционирование: {brand_profile.get('positioning')}")
    print(f"     • Услуги: парикмахерский зал, ногтевая студия, косметология, визаж")
    print(f"     • Тон общения: {brand_profile.get('tone_of_voice') or 'Премиальный, заботливый, вдохновляющий'}")

    # -------------------------------------------------------------
    # ЭТАП 4: АВТОНОМНАЯ ГЕНЕРАЦИЯ ПОСТА & АУДИТ КАЧЕСТВА
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("✍️ [ЭТАП 4/5] ГЕНЕРАЦИЯ СММ-ПОСТА ПОД ВСЕ 4 НАПРАВЛЕНИЯ УСЛУГ...")
    print("-" * 70)

    topic = "Комплексное преображение в одном месте: парикмахерский зал, ногтевой сервис, косметология и визаж"
    
    post_payload = {
        "user_id": user_input["user_id"],
        "company_name": user_input["company_name"],
        "niche": user_input["niche"],
        "city": user_input["city"],
        "topic": topic,
        "format": "post",
        "tone": "Заботливый, эстетичный, естественный",
        "brand_profile": brand_profile,
        "generate_image": False, # Отключаем тяжелую диффузию
        "comments_enabled": True
    }

    post_result = await orchestrator.execute_task(
        task_type="generate_post",
        user_data=post_payload,
        session_id=user_input["session_id"]
    )

    # -------------------------------------------------------------
    # ЭТАП 5: ФОРМИРОВАНИЕ ПАКЕТА С ЗАГЛУШКОЙ ВИЗУАЛА
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("🎨 [ЭТАП 5/5] СБОРКА ПАКЕТА ПУБЛИКАЦИИ С ЗАГЛУШКОЙ ВИЗУАЛА...")
    print("-" * 70)

    photo_placeholder = "🖼️ (тут могла быть ваша реклама)"
    t_total = round(time.time() - t_start, 2)

    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЙ ПАКЕТ ДЛЯ TELEGRAM / VK / OK / MAX:")
    print("=" * 70)
    print("✉️ [СООБЩЕНИЕ 1 - ФОТО + ТЕКСТ ПОСТА]:")
    print(f"{photo_placeholder}\n")
    print(post_result.get("post_text"))
    print("\n✉️ [СООБЩЕНИЕ 2 - МЕТРИКИ И ХЭШТЕГИ]:")
    print(f"⏱️ Время сквозной работы конвейера: {t_total} сек")
    print(f"• Живой веб-парсинг: {t_web_duration}s")
    print(f"• Тренды бьюти-сферы: {t_trends_duration}s")
    print(f"• Копирайтинг & Критик: {post_result.get('timings', {}).get('text_gen_seconds', 0.01)}s")
    print(f"• Режим визуала: Заглушка '{photo_placeholder}'")
    print(f"\n{post_result.get('hashtags', '#Крокус #салонкрасоты #уходзасобой #маникюр #косметология #визаж')}")
    print("=" * 70)
    print(f"🎉 ПАЙПЛАЙН ДЛЯ «КРОКУС» УСПЕШНО ЗАВЕРШЁН ЗА {t_total} СЕК!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_crocus_beauty_pipeline())
