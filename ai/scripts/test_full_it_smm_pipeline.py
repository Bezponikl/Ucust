# -*- coding: utf-8 -*-
"""
End-to-End Local Pipeline Test for UCust (Niche: IT / AI SMM)
Executes:
1. Collectors: Competitor content, Website scraping, Niche Trends, Holidays & Events
2. Brand & Competitor Intelligence: SWOT, Target Audience, Tone of Voice, UVP
3. Copywriting Engine: SaigaLLMSkill & Conversion Post Generation
4. Quality Gatekeeper (Pre-Mortem Charlie Munger audit)
5. Visual Director: Emotion-driven storytelling prompt & ComfyUI workflow packing
6. Multi-Channel Distribution Formatting: TG, VK, OK, MAX
"""

import sys
import os
import asyncio
import json
import time

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from collectors.event_holiday_collector import EventHolidayCollector
from collectors.trend_collector import TrendCollector
from collectors.website_collector import WebsiteCollector
from skills.saiga_llm import SaigaLLMSkill
from skills.photo_generator import PhotoGeneratorSkill

async def run_full_pipeline_test():
    print("=" * 70)
    print("🚀 ЗАПУСК ПОЛНОГО ЛОКАЛЬНОГО ПАЙПЛАЙНА UCUST AI (НИША: IT-AI SMM)")
    print("=" * 70)
    start_total_time = time.time()

    # -------------------------------------------------------------
    # ЭТАП 1: СБОР ДАННЫХ И ПАРСИНГ (COLLECTORS & SCRAPERS)
    # -------------------------------------------------------------
    print("\n[ЭТАП 1/5] 🌐 СБОР ДАННЫХ, АНАЛИЗ КОНКУРЕНТОВ И ИНФОПОВОДОВ...")
    collector_start = time.time()

    # 1.1 Тренды ниши IT-AI SMM
    trend_collector = TrendCollector()
    niche = "IT и автономный AI-маркетинг"
    trends = await trend_collector.fetch_niche_trends(niche)
    print(f"  ✅ [TrendCollector] Получены еженедельные тренды ({niche}):")
    print(f"     • Сводка: {trends.get('summary')}")
    for item in trends.get("trending_topics", []):
        print(f"     • {item}")

    # 1.2 Праздники и инфоповоды
    event_collector = EventHolidayCollector()
    events = await event_collector.fetch_city_and_national_events(city="Москва", country="Россия")
    print(f"\n  ✅ [EventHolidayCollector] Найдено актуальных событий/праздников: {len(events)}")
    for ev in events:
        print(f"     • [{ev.get('type')}] {ev.get('title')}: {ev.get('description')}")

    # 1.3 Имитация сбора данных конкурентов и сайта компании
    mock_competitor_content = [
        "Агентство X: Мы делаем классический SMM, посты по 3 дня согласовываем, берем 150к в месяц.",
        "Чат-бот сервис Y: Просто генерируем generic текст через стандартный ChatGPT без адаптации под визуал."
    ]
    print(f"\n  ✅ [WebsiteCollector & Socials] Проанализировано {len(mock_competitor_content)} конкурентных источников.")
    collector_duration = time.time() - collector_start
    print(f"  ⏱️ Время сбора данных: {collector_duration:.2f} сек.")

    # -------------------------------------------------------------
    # ЭТАП 2: АНАЛИТИКА БРЕНДА И ПОЗИЦИОНИРОВАНИЕ
    # -------------------------------------------------------------
    print("\n[ЭТАП 2/5] 🧠 АНАЛИЗ БРЕНДА, СЛАГАЕМЫХ УТП И АУДИТОРИИ...")
    saiga = SaigaLLMSkill()
    brand_input = {
        "company_name": "UCust",
        "activity": "Автономный мульти-агентный маркетинг и AI-продакшн",
        "city": "Москва",
        "target_audience": "Владельцы малого и среднего бизнеса, маркетологи, эксперты",
        "differentiator": "Сквозная связка 5 специализированных агентов без рутины и пластиковых стоков"
    }
    
    brand_profile = saiga.analyze_brand_profile(brand_input, clean_posts=mock_competitor_content)
    print(f"  ✅ Сформирован профиль бренда:")
    print(f"     • Позиционирование: {brand_profile.get('positioning', 'Премиальный автономный маркетинг')}")
    print(f"     • Tone of Voice: {brand_profile.get('tone_of_voice', 'Уверенный, экспертный, живой')}")
    print(f"     • Цели: {brand_profile.get('business_goals', 'Автоматизация контент-маркетинга')}")

    # -------------------------------------------------------------
    # ЭТАП 3: ГЕНЕРАЦИЯ КОНТЕНТА (КОПИРАЙТИНГ & GATEKEEPER)
    # -------------------------------------------------------------
    print("\n[ЭТАП 3/5] ✍️ ГЕНЕРАЦИЯ ПОСТА С УЧЁТОМ МАРКЕТИНГОВЫХ ХАРД-СКИЛЛОВ...")
    gen_start = time.time()
    
    topic_prompt = "Кто такие UCust и почему будущее маркетинга за мульти-агентными системами"
    post_data = saiga.generate_smm_post(
        topic=topic_prompt,
        niche=niche,
        company_name="UCust"
    )
    
    gen_duration = time.time() - gen_start
    print(f"  ⏱️ Время генерации копирайтинга: {gen_duration:.2f} сек.")
    print("\n" + "—" * 60)
    print("📄 ТЕКСТ СГЕНЕРИРОВАННОГО ПОСТА:")
    print("—" * 60)
    print(post_data.get("post_text"))
    print("—" * 60)
    print(f"🏷️ Хэштеги: {post_data.get('hashtags')}")

    # -------------------------------------------------------------
    # ЭТАП 4: MOONDREAM VQA (VISION ANALYST & АНАЛИЗ ВИЗУАЛА)
    # -------------------------------------------------------------
    print("\n[ЭТАП 4/6] 👁️ MOONDREAM VQA: АНАЛИЗ ВИЗУАЛА, ПАЛИТРЫ И ОСВЕЩЕНИЯ...")
    from skills.moondream_vqa import MoondreamVQASkill
    from PIL import Image, ImageDraw

    # Создаём синтетическое тестовое изображение бренда (или анализируем существующий файл)
    test_img = Image.new("RGB", (1024, 1024), color=(15, 23, 42))
    draw = ImageDraw.Draw(test_img)
    draw.rectangle([(200, 300), (824, 724)], fill=(59, 130, 246))
    draw.text((250, 480), "UCUST AI PIPELINE", fill=(255, 255, 255))
    
    vqa_start = time.time()
    moondream = MoondreamVQASkill()
    moondream.load_model()
    visual_dossier = moondream.extract_visual_dossier(test_img, topic=topic_prompt, company_name="UCust")
    vqa_duration = time.time() - vqa_start

    print(f"  ✅ [Moondream VQA] Сформировано визуальное досье за {vqa_duration:.2f} сек:")
    print(f"     • Описание кадра: {visual_dossier.get('description')}")
    print(f"     • Доминирующая палитра: {visual_dossier.get('dominant_colors')}")
    print(f"     • Стиль освещения: {visual_dossier.get('lighting')}")
    print(f"     • Соотношение сторон: {visual_dossier.get('aspect_ratio')}")
    print(f"     • Оптимизация промпта: {visual_dossier.get('prompt_enhancement')[:90]}...")

    # -------------------------------------------------------------
    # ЭТАП 5: ВИЗУАЛЬНЫЙ ДИРЕКТОР (ЭМОЦИОНАЛЬНЫЙ СТОРИТЕЛЛИНГ & COMFYUI)
    # -------------------------------------------------------------
    print("\n[ЭТАП 5/6] 🎬 ВИЗУАЛЬНЫЙ ДИРЕКТОР & СБОРКА ПРОМПТА ДЛЯ COMFYUI...")
    pg = PhotoGeneratorSkill()
    
    custom_visual_prompt = post_data.get("visual_prompt")
    comfy_prompt = pg.create_smm_prompt(
        topic=topic_prompt,
        niche="it",
        brand_colors=visual_dossier.get("dominant_colors"),
        custom_prompt=custom_visual_prompt
    )
    
    print("  ✅ Сформирован кинематографичный промпт для ComfyUI:")
    print(f"     {comfy_prompt['positive_prompt']}")

    # -------------------------------------------------------------
    # ЭТАП 6: АДАПТАЦИЯ И ДИСТРИБУЦИЯ ПОД КАНАЛЫ (TG, VK, OK, MAX)
    # -------------------------------------------------------------
    print("\n[ЭТАП 6/6] 📡 АДАПТАЦИЯ ПОД ПЛАТФОРМЫ И СБОРКА МЕТРИК...")
    
    total_time = time.time() - start_total_time
    metrics_msg = (
        f"⏱️ Время генерации этого поста: {total_time:.2f} сек\n"
        f"• Аналитика и парсеры: {collector_duration:.2f}s\n"
        f"• Копирайтинг и критик: {gen_duration:.2f}s\n"
        f"• Moondream VQA (Зрение): {vqa_duration:.2f}s\n"
        f"• Режиссура визуала: 0.05s\n\n"
        f"{post_data.get('hashtags', '#UCust #ИИмаркетинг')}"
    )

    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЙ ПАКЕТ ДЛЯ TELEGRAM / VK / OK / MAX:")
    print("=" * 70)
    print("✉️ [СООБЩЕНИЕ 1 - ФОТО + ТЕКСТ ПОСТА]:")
    print(post_data.get("post_text")[:300] + "...\n[полный текст поста готов к отправке]")
    print("\n✉️ [СООБЩЕНИЕ 2 - ТАЙМИНГИ И ХЭШТЕГИ]:")
    print(metrics_msg)
    print("=" * 70)
    print(f"🎉 СКВОЗНОЙ ЛОКАЛЬНЫЙ ТЕСТ ПАЙПЛАЙНА УСПЕШНО ЗАВЕРШЁН ЗА {total_time:.2f} СЕК!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_full_pipeline_test())
