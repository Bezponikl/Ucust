"""
test_visual_grid_onboarding.py
======================================================================
Сквозной тест работы Визуального Директора при парсинге и онбординге:
1. Сбор и кэширование картинок через WebsiteCollector.
2. Анализ 3x3 сетки (Grid DNA), палитры Hex и композиционного ритма через AdvancedVisualDirector.
3. Полный онбординг через UnifiedOrchestrator с сохранением visual_grid_dna в профиль.
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio
from PIL import Image

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from collectors.website_collector import WebsiteCollector, CleanHTMLParser
from skills.advanced_visual_director import AdvancedVisualDirector
from core.orchestrator import UnifiedOrchestrator


def create_sample_test_images() -> list:
    """Создает временные тестовые изображения с разными брендовыми цветами."""
    temp_dir = os.path.join(AI_ROOT, "output", "temp_cache")
    os.makedirs(temp_dir, exist_ok=True)
    
    test_files = []
    colors = [
        (230, 57, 70),   # Красный (#E63946)
        (241, 250, 238), # Белый/Светлый (#F1FAEE)
        (168, 218, 220), # Бирюзовый (#A8DADC)
        (69, 123, 157),  # Синий (#457B9D)
        (29, 53, 87),    # Темно-синий (#1D3557)
    ]
    
    for i, rgb in enumerate(colors, 1):
        img_path = os.path.join(temp_dir, f"test_grid_sample_{i}.jpg")
        img = Image.new("RGB", (200, 200), color=rgb)
        img.save(img_path)
        test_files.append(img_path)
        
    return test_files


async def test_grid_analysis_pipeline():
    print("=" * 75)
    print("🎨 ТЕСТИРОВАНИЕ ВИЗУАЛЬНОГО ДИРЕКТОРА И АНАЛИЗА СЕТКИ (GRID DNA)")
    print("=" * 75)

    # -------------------------------------------------------------
    # ТЕСТ 1: ПАРСЕР HTML И ИЗВЛЕЧЕНИЕ КАРТИНОК
    # -------------------------------------------------------------
    print("\n--- [ТЕСТ 1] Парсинг HTML и извлечение картинок ---")
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Салон красоты Crocus Beauty</title>
        <meta name="description" content="Премиальный уход за волосами и маникюр в центре Москвы">
        <meta property="og:image" content="https://crocus.ru/assets/hero_banner.jpg">
    </head>
    <body>
        <h1>Crocus Beauty - Студия эстетики</h1>
        <p>Мы создаем безупречные образы и заботимся о вашем комфорте.</p>
        <img src="https://crocus.ru/img/salon_interior.jpg" alt="Интерьер">
        <img data-src="https://crocus.ru/img/nails_macro.jpg" alt="Маникюр">
        <img src="https://crocus.ru/img/stylist_work.jpg" alt="Мастер">
    </body>
    </html>
    """
    parser = CleanHTMLParser()
    parser.feed(sample_html)
    
    print(f"✅ Заголовок: {parser.title or parser.og_title}")
    print(f"✅ OG Image: {parser.og_image}")
    print(f"✅ Извлеченные изображения (HTML tags): {parser.images}")
    
    assert parser.og_image == "https://crocus.ru/assets/hero_banner.jpg"
    assert len(parser.images) == 3
    assert "https://crocus.ru/img/nails_macro.jpg" in parser.images

    # -------------------------------------------------------------
    # ТЕСТ 2: АНАЛИЗ СЕТКИ В ADVANCED VISUAL DIRECTOR
    # -------------------------------------------------------------
    print("\n--- [ТЕСТ 2] Анализ 3x3 Сетки и Hex-палитры (AdvancedVisualDirector) ---")
    test_images = create_sample_test_images()
    
    director = AdvancedVisualDirector()
    grid_dna = director.analyze_visual_grid(test_images, niche="Салон красоты")
    
    palette = grid_dna.get("brand_hex_palette", [])
    slots = grid_dna.get("grid_3x3_slots", [])
    next_rec = grid_dna.get("next_post_recommendation", {})
    
    print(f"🎨 Извлеченная палитра бренда (Hex): {palette}")
    print(f"🎯 Доминирующий цвет: {grid_dna.get('dominant_color')}")
    print(f"📐 Слотов в матрице 3x3: {len(slots)}")
    print(f"💡 Рекомендация для следующего поста:\n   {next_rec.get('advice')}")
    print(f"   Промпт-модификаторы: {next_rec.get('suggested_prompt_modifiers')}")

    assert len(palette) >= 3, "Ошибка: палитра содержит менее 3 цветов!"
    assert len(slots) == 9, "Ошибка: матрица 3x3 должна содержать ровно 9 слотов!"
    assert next_rec.get("target_slot") == 1
    assert "authentic" in next_rec.get("suggested_prompt_modifiers")

    # -------------------------------------------------------------
    # ТЕСТ 3: СКВОЗНОЙ ОНБОРДИНГ ЧЕРЕЗ UNIFIED ORCHESTRATOR
    # -------------------------------------------------------------
    print("\n--- [ТЕСТ 3] Сквозной Онбординг с сохранением Grid DNA ---")
    orchestrator = UnifiedOrchestrator()
    
    onboarding_payload = {
        "user_id": "usr_grid_test_100",
        "company_name": "Crocus Beauty",
        "niche": "Салон красоты",
        "activity": "Услуги красоты и уход",
        "city": "Москва",
        "attachments": test_images,
        "raw_social_input": "https://example.com"
    }
    
    res = await orchestrator.execute_task(
        task_type="onboarding",
        user_data=onboarding_payload,
        session_id="sess_test_grid_onboarding"
    )
    
    profile = res.get("profile", {})
    visual_dna = profile.get("visual_grid_dna", {})
    
    print(f"\n📋 Результат онбординга:")
    print(f"   • Название: {profile.get('company_name') or 'Crocus Beauty'}")
    print(f"   • Ниша: {profile.get('field')}")
    print(f"   • Цвета бренда в профиле: {profile.get('brand_colors')}")
    print(f"   • Visual Grid DNA статус: {visual_dna.get('status')}")
    print(f"   • Проанализировано изображений: {visual_dna.get('analyzed_images_count')}")

    assert visual_dna.get("status") == "success"
    assert len(profile.get("brand_colors", [])) >= 3
    assert len(visual_dna.get("grid_3x3_slots", [])) == 9

    print("\n" + "=" * 75)
    print("🎉 ВСЕ ТЕСТЫ АНАЛИЗА СЕТКИ И ВИЗУАЛЬНОГО ДИРЕКТОРА УСПЕШНО ПРОЙДЕНЫ!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(test_grid_analysis_pipeline())
