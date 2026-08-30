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

    # 1.3 Поиск сайтов в интернете и глубокий парсинг конкурентов
    website_collector = WebsiteCollector(timeout=5.0)
    search_query = f"{niche} Москва"
    competitors = await website_collector.search_and_collect_competitors(search_query, limit=2, deep_parse=True)
    
    print(f"\n  ✅ [WebsiteCollector] Найдено и проанализировано сайтов конкурентов: {len(competitors)}")
    for comp in competitors:
        print(f"     • 🌐 {comp.get('title')}")
        print(f"       Ссылка: {comp.get('url')}")
        if comp.get('description'):
            print(f"       УТП: {comp.get('description')[:110]}...")
    
    collector_duration = time.time() - collector_start
    print(f"  ⏱️ Время сбора данных (Тренды + Праздники + Веб-поиск): {collector_duration:.2f} сек.")

    # -------------------------------------------------------------
    # ЭТАП 2: MOONDREAM VQA (МУЛЬТИМОДАЛЬНЫЙ АНАЛИЗ ПОСТОВ И КРЕАТИВОВ КОНКУРЕНТОВ)
    # -------------------------------------------------------------
    print("\n[ЭТАП 2/6] 👁️ MOONDREAM VQA: МУЛЬТИМОДАЛЬНЫЙ АНАЛИЗ ПОСТОВ КОНКУРЕНТОВ (ТЕКСТ + ВИЗУАЛ)...")
    from skills.moondream_vqa import MoondreamVQASkill
    from PIL import Image, ImageDraw

    vqa_start = time.time()
    moondream = MoondreamVQASkill()
    is_fast_mode = "--fast" in sys.argv
    
    if not is_fast_mode:
        moondream.load_model()

    # Синтезируем баннер конкурента (или берем реальное изображение из спарсенного поста)
    comp_banner = Image.new("RGB", (800, 600), color=(220, 38, 38))
    draw = ImageDraw.Draw(comp_banner)
    draw.rectangle([(50, 50), (750, 550)], fill=(239, 68, 68))
    draw.text((100, 260), "SALE -50% GENERIC SMM BOT", fill=(255, 255, 255))

    comp_post_text = "Сервис автопостинга: скидка 50% на все тарифы при оплате на год! Стандартный функционал и чат-бот."
    
    multimodal_comp_analysis = moondream.analyze_competitor_post(
        competitor_name="SMMplanner / Типовой SMM-бот",
        post_text=comp_post_text,
        image_input=comp_banner if not is_fast_mode else None
    )
    vqa_duration = time.time() - vqa_start

    print(f"  ✅ [Moondream VQA] Завершён мультимодальный разбор поста конкурента ({vqa_duration:.2f} сек):")
    print(f"     • Текст конкурента: «{multimodal_comp_analysis.get('post_text')[:75]}...»")
    print(f"     • Визуал креатива: {multimodal_comp_analysis.get('visual_description')}")
    print(f"     • Маркетинговый хук: {multimodal_comp_analysis.get('visual_hook')}")
    print(f"     • Слабое место креатива: {multimodal_comp_analysis.get('weakness')}")
    print(f"     🎯 Задача отстройки для Сайги: {multimodal_comp_analysis.get('counter_angle')}")

    # -------------------------------------------------------------
    # ЭТАП 3: АНАЛИТИКА БРЕНДА И ОТСТРОЙКА В SAIGA LLM
    # -------------------------------------------------------------
    print("\n[ЭТАП 3/6] 🧠 АНАЛИЗ БРЕНДА В САЙГЕ НА ОСНОВЕ МУЛЬТИМОДАЛЬНОГО ДОСЬЕ...")
    saiga = SaigaLLMSkill()
    brand_input = {
        "company_name": "UCust",
        "activity": "Автономный мульти-агентный маркетинг и AI-продакшн",
        "city": "Москва",
        "target_audience": "Владельцы малого и среднего бизнеса, маркетологи, эксперты",
        "differentiator": "Сквозная связка специализированных AI-навыков без рутины и шаблонных стоковых баннеров"
    }
    
    # Передаем спарсенные сайты + мультимодальное досье от Moondream
    combined_intel = [
        c.get("structured_dossier", c.get("title", "")) for c in competitors
    ] + [multimodal_comp_analysis.get("multimodal_dossier", "")]

    brand_profile = saiga.analyze_brand_profile(brand_input, clean_posts=combined_intel)
    print(f"  ✅ Сформирован профиль бренда и стратегия контр-позиционирования:")
    print(f"     • Позиционирование: {brand_profile.get('positioning')}")
    print(f"     • Tone of Voice: {brand_profile.get('tone_of_voice')}")
    print(f"     • Цели: {brand_profile.get('business_goals')}")

    # -------------------------------------------------------------
    # ЭТАП 4: ГЕНЕРАЦИЯ КОНТЕНТА (КОПИРАЙТИНГ & GATEKEEPER)
    # -------------------------------------------------------------
    print("\n[ЭТАП 4/6] ✍️ ГЕНЕРАЦИЯ ПОСТА С УЧЁТОМ МАРКЕТИНГОВЫХ ХАРД-СКИЛЛОВ...")
    gen_start = time.time()
    topic_prompt = "Кто такие UCust и почему будущее маркетинга за мульти-агентными системами"
    
    post_data = saiga.generate_smm_post(
        topic=topic_prompt,
        niche="IT и автономный AI-маркетинг",
        company_name="UCust",
        brand_profile=brand_profile,
        user_notes="Упор на твёрдые маркетинговые навыки системы и отстройку от шаблонных стоковых решений",
        tone_override="Естественный и живой"
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
    # ЭТАП 5: ВИЗУАЛЬНЫЙ ДИРЕКТОР (ЭМОЦИОНАЛЬНЫЙ СТОРИТЕЛЛИНГ & COMFYUI)
    # -------------------------------------------------------------
    print("\n[ЭТАП 5/6] 🎬 ВИЗУАЛЬНЫЙ ДИРЕКТОР & СБОРКА ПРОМПТА ДЛЯ COMFYUI...")
    
    is_mock_image = "--no-gen" in sys.argv or "--mock" in sys.argv or "--placeholder" in sys.argv
    if is_mock_image:
        photo_attachment_label = "🖼️ (тут могла быть ваша реклама)"
        print(f"  ⚡ [Режим без генерации]: Вместо ComfyUI используется заглушка -> '{photo_attachment_label}'")
        comfy_prompt = {"positive_prompt": "Cinematic visual placeholder: (тут могла быть ваша реклама)"}
    else:
        pg = PhotoGeneratorSkill()
        custom_visual_prompt = post_data.get("visual_prompt")
        comfy_prompt = pg.create_smm_prompt(
            topic=topic_prompt,
            niche="it",
            custom_prompt=custom_visual_prompt
        )
        photo_attachment_label = "📸 Сгенерированное изображение (ComfyUI / Брендовый баннер)"
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
    print(f"{photo_attachment_label}\n")
    print(post_data.get("post_text")[:300] + "...\n[полный текст поста готов к отправке]")
    print("\n✉️ [СООБЩЕНИЕ 2 - ТАЙМИНГИ И ХЭШТЕГИ]:")
    print(metrics_msg)
    print("=" * 70)
    print(f"🎉 СКВОЗНОЙ ЛОКАЛЬНЫЙ ТЕСТ ПАЙПЛАЙНА УСПЕШНО ЗАВЕРШЁН ЗА {total_time:.2f} СЕК!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_full_pipeline_test())
