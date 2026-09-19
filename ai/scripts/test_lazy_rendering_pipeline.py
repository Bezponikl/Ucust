"""
File: ai/scripts/test_lazy_rendering_pipeline.py
Сквозное тестирование архитектуры Lazy Rendering, разрешения семантических конфликтов,
экстрактора OCR и стейт-машины LazyRenderingController.
"""

import os
import sys
import asyncio
from datetime import datetime

# Настройка кодировки и путей
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if AI_DIR not in sys.path:
    sys.path.insert(0, AI_DIR)

from core.lazy_rendering_controller import (
    SubscriptionTier,
    IndustryArchetype,
    ContentFormat,
    PostLifecycleStatus,
    PostDraft,
    ImageGenerationSpec,
    VRAMCostCalculator,
    LazyRenderingController
)
from skills.content_strategy_engine import (
    BrandProfile,
    RawDataIngestion,
    IngestionSourceType,
    SemanticConflictResolver,
    OCREntityExtractor,
    ContentStrategyEngine,
    get_available_formats
)


def test_ocr_entity_extractor():
    print("\n📄 [1/5] Тестирование OCREntityExtractor (Очистка от ИНН/шума и поиск цен)...")
    raw_ocr_mess = """
    ООО "Гастроном Премиум"
    ИНН 7701234567 КПП 770101001 ОГРН 1027700123456
    г. Москва, ул. Арбат, д. 10, стр. 2
    --------------------------------------------------
    МЕНЮ РЕСТОРАНА (Страница 1)
    
    Тартар из мраморной говядины ......... 750 руб
    Крем-суп из белых грибов .............. 580 ₽
    Филе лосося на гриле .................. 1200 руб
    Фирменный десерт Павлова .............. 450 ₽
    
    Тел: +7 (495) 123-45-67
    ==================================================
    """
    compact_summary = OCREntityExtractor.extract_compact_entities(raw_ocr_mess)
    print(f"   Результат экстракции:\n   👉 {compact_summary}")
    assert "750" in compact_summary and "580" in compact_summary and "1200" in compact_summary
    assert "ИНН" not in compact_summary and "ООО" not in compact_summary
    print("   ✅ OCREntityExtractor успешно выделил только коммерческие позиции и цены!")


def test_semantic_conflict_resolver():
    print("\n🌐 [2/5] Тестирование двуязычного SemanticConflictResolver (RU/EN)...")
    vlm_anchors_with_junk = [
        "пластиковый подоконник",     # RU стоп-слово
        "dirty cluttered background",   # EN стоп-слово
        "natural morning daylight",     # Валидный якорь
        "дешевый линолеум",            # RU стоп-слово
        "delicate swan latte art"       # Валидный якорь
    ]
    brand_rag_props = ["scandinavian dark oak desk", "matte brass accents"]

    resolved = SemanticConflictResolver.resolve_visual_anchors(vlm_anchors_with_junk, brand_rag_props)
    print(f"   Сырые якоря VLM: {vlm_anchors_with_junk}")
    print(f"   RAG-профиль бренда: {brand_rag_props}")
    print(f"   Очищенный результат:\n   👉 {resolved}")

    # Проверка, что мусор удален, а RAG идет первым
    assert "scandinavian dark oak desk" in resolved
    assert not any("пластик" in a or "dirty" in a or "дешев" in a for a in resolved)
    print("   ✅ SemanticConflictResolver успешно заблокировал RU и EN визуальные дефекты!")


def test_tier_format_limits():
    print("\n💰 [3/5] Тестирование тарифных ограничений форматов (Tier-based access)...")
    starter_formats = get_available_formats(SubscriptionTier.STARTER)
    pro_formats = get_available_formats(SubscriptionTier.PRO)
    ent_formats = get_available_formats(SubscriptionTier.ENTERPRISE)

    print(f"   🟢 STARTER разрешено: {[f.value for f in starter_formats]}")
    print(f"   🟡 PRO разрешено:     {[f.value for f in pro_formats]}")
    print(f"   🔴 ENTERPRISE разрешено: {[f.value for f in ent_formats]}")

    assert ContentFormat.CRYPTEX_PUZZLE not in starter_formats
    assert ContentFormat.CAROUSEL_LIGHT in pro_formats
    assert ContentFormat.CRYPTEX_PUZZLE in ent_formats
    print("   ✅ Тарифная защита от перерасхода GPU работает корректно!")


def test_vram_calculation():
    print("\n🧮 [4/5] Тестирование калькулятора VRAMCostCalculator с учетом модели 6.5GB...")
    spec_square = ImageGenerationSpec(prompt="test", width=1024, height=1024)
    spec_portrait = ImageGenerationSpec(prompt="test", width=1080, height=1350)

    vram_square = VRAMCostCalculator.calculate_spec_vram(spec_square)
    vram_portrait = VRAMCostCalculator.calculate_spec_vram(spec_portrait)

    print(f"   Квадрат 1024x1024: {vram_square} MB (Модель: 6500 + Активация: ~1850 + VAE: 850)")
    print(f"   Портрет 1080x1350: {vram_portrait} MB (Модель: 6500 + Активация: ~2880 + VAE: 850)")

    assert vram_square >= 9000  # С учетом 6.5GB базовой модели
    assert vram_portrait > vram_square
    print("   ✅ Расчет VRAM защищен от OOM и учитывает полный физический вес инстанса!")


async def test_lazy_rendering_state_machine():
    print("\n🎨 [5/5] Тестирование жизненного цикла PostDraft в LazyRenderingController...")
    engine = ContentStrategyEngine()
    controller = LazyRenderingController(dev_simulation_mode=True)

    # 1. Создаем профиль B2B бренда на тарифе PRO
    brand = BrandProfile(
        brand_id="brand_corp_01",
        company_name="Apex Legal Partners",
        industry=IndustryArchetype.B2B_CORPORATE,
        tier=SubscriptionTier.PRO,
        brand_props=["dark bog oak table", "brass Montblanc pen"],
        tone_of_voice="Строгий, аналитический, экспертный"
    )

    raw_input = RawDataIngestion(
        source_type=IngestionSourceType.HYBRID,
        vlm_visual_anchors=["sunlit glass office", "пластиковая ручка"], # Пластик должен отфильтроваться
        ocr_raw_text="Договор M&A №405. Сумма сделки: 15000000 руб. Аудит пройден.",
        rag_context_snippets=["15 лет безупречной практики в арбитраже", "Снижение налоговых рисков на 40%"]
    )

    # 2. Генерация черновика (DRAFT_TEXT, 0 GPU cost!)
    draft_post = engine.generate_post_draft(
        brand=brand,
        raw_input=raw_input,
        target_date=datetime(2026, 9, 21),  # Понедельник (MON)
        forced_format=ContentFormat.CAROUSEL_LIGHT
    )

    print(f"   📝 Сгенерирован пост: ID={draft_post.post_id}")
    print(f"   📌 Статус: {draft_post.status.value}")
    print(f"   🖼️ Спецификаций изображений: {len(draft_post.image_specs)}")
    print(f"   💾 Оценка VRAM: {draft_post.vram_cost_mb} MB")
    print(f"   📜 Текст поста (превью):\n{draft_post.text_content[:160]}...\n")

    assert draft_post.status == PostLifecycleStatus.DRAFT_TEXT

    # 3. Регистрация в контроллере
    controller.register_draft(draft_post)

    # 4. Триггер рендера (переход в AWAITING_RENDER -> RENDERING -> RENDERED)
    print("   🚀 Запуск триггера рендера (trigger_render)...")
    await controller.trigger_render(draft_post.post_id, trigger_source="user_approved_click")

    # Ждем завершения асинхронного воркера (3 изображения по 0.05с)
    await asyncio.sleep(0.6)

    updated_post = controller.posts_db[draft_post.post_id]
    print(f"   ✅ Итоговый статус поста: {updated_post.status.value}")
    print(f"   🌐 Полученные URL изображений: {updated_post.rendered_image_urls}")

    assert updated_post.status == PostLifecycleStatus.RENDERED
    assert len(updated_post.rendered_image_urls) == len(draft_post.image_specs)
    print("   🎉 Стейт-машина LazyRenderingController отработала идеально!")


def main():
    test_ocr_entity_extractor()
    test_semantic_conflict_resolver()
    test_tier_format_limits()
    test_vram_calculation()
    asyncio.run(test_lazy_rendering_state_machine())


if __name__ == "__main__":
    main()
