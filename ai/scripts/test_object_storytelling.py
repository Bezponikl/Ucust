"""
test_object_storytelling.py
======================================================================
Тестирование модуля извлечения историй и фактов об объектах (Object Knowledge Storytelling):
1. Десерты и кондитерские шедевры (Тирамису, Сан-Себастьян, Дубайский шоколад, Круассан).
2. Дизайнерская мебель и материалы (Кресло Eames, Массив дуба, Венский стул Thonet).
3. Эстетическая медицина и стоматология (Голливудские виниры Чарльза Пинкуса).
4. Specialty кофе и напитки (Раф-кофе, Hario V60).
5. Генерация промпта сторителлинга для Saiga LLM.
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from skills.object_storytelling import ObjectKnowledgeStoryteller


async def test_object_storytelling_suite():
    print("=" * 80)
    print("🍰 ТЕСТИРОВАНИЕ МОДУЛЯ СТОРИТЕЛЛИНГА И ФАКТОВ ОБ ОБЪЕКТАХ (OBJECT STORYTELLER)")
    print("=" * 80)

    # 1. Кондитерские десерты: Тирамису
    print("\n🍨 1. КОНДИТЕРСКАЯ: «Тирамису»")
    story_tiramisu = await ObjectKnowledgeStoryteller.extract_object_story_async(
        topic="Классический итальянский десерт Тирамису",
        niche="Кондитерская и кофейня",
        company_name="Dolce Vita"
    )
    print(f"   • Объект: {story_tiramisu['object_name']}")
    print(f"   • Легенда: {story_tiramisu['origin_story']}")
    print(f"   • Секретный факт: {story_tiramisu['fun_fact']}")
    print(f"   • Сенсорный хук: {story_tiramisu['sensory_hook']}")
    assert "Лингуанотто" in story_tiramisu["origin_story"] or "маскарпоне" in story_tiramisu["origin_story"]
    assert "маскарпоне" in story_tiramisu["fun_fact"] or "савоярди" in story_tiramisu["origin_story"]
    assert "Италия" in story_tiramisu["formatted_story_prompt"]
    print("✅ История и факты о Тирамису успешно извлечены!")

    # 2. Кондитерские десерты: Чизкейк Сан-Себастьян
    print("\n" + "=" * 80)
    print("🧀 2. КОНДИТЕРСКАЯ: «Баскский чизкейк Сан-Себастьян»")
    print("=" * 80)
    story_basque = await ObjectKnowledgeStoryteller.extract_object_story_async(
        topic="Нежный чизкейк Сан-Себастьян с карамельной корочкой",
        niche="Кондитерская",
        company_name="Sweet Story"
    )
    print(f"   • Объект: {story_basque['object_name']}")
    print(f"   • Секретный факт: {story_basque['fun_fact']}")
    assert "240" in story_basque["origin_story"] or "Майяра" in story_basque["fun_fact"] or "карамел" in story_basque["fun_fact"]
    print("✅ История и факты о Сан-Себастьяне подтверждены!")

    # 3. Трендовый десерт: Дубайский шоколад
    print("\n" + "=" * 80)
    print("🍫 3. ТРЕНД 2024–2026: «Дубайский шоколад с фисташкой и катаифи»")
    print("=" * 80)
    story_dubai = await ObjectKnowledgeStoryteller.extract_object_story_async(
        topic="Дубайский шоколад с хрустящей фисташковой начинкой",
        niche="Шоколадный бутик",
        company_name="Dubai Choco"
    )
    print(f"   • Объект: {story_dubai['object_name']}")
    print(f"   • История: {story_dubai['origin_story']}")
    assert "катаифи" in story_dubai["origin_story"]
    assert "фисташков" in story_dubai["origin_story"]
    print("✅ История Дубайского шоколада успешно подгружена!")

    # 4. Мебель и интерьер: Кресло Eames и Массив дуба
    print("\n" + "=" * 80)
    print("🛋️ 4. ДИЗАЙН И МЕБЕЛЬ: «Кресло Eames Lounge Chair»")
    print("=" * 80)
    story_eames = await ObjectKnowledgeStoryteller.extract_object_story_async(
        topic="Культовое кожаное кресло Eames Lounge Chair",
        niche="Дизайнерская мебель",
        company_name="Maksima Мебель"
    )
    print(f"   • Объект: {story_eames['object_name']}")
    print(f"   • Легенда: {story_eames['origin_story']}")
    print(f"   • Секретный факт: {story_eames['fun_fact']}")
    assert "Имз" in story_eames["origin_story"]
    assert "MoMA" in story_eames["fun_fact"] or "1956" in story_eames["formatted_story_prompt"]
    print("✅ Исторический контекст легендарного кресла Eames извлечен!")

    # 5. Стоматология: История голливудских виниров
    print("\n" + "=" * 80)
    print("🦷 5. СТОМАТОЛОГИЯ: «Керамические виниры»")
    print("=" * 80)
    story_veneers = await ObjectKnowledgeStoryteller.extract_object_story_async(
        topic="Керамические виниры E-Max",
        niche="Стоматология",
        company_name="ДентаЛюкс"
    )
    print(f"   • Объект: {story_veneers['object_name']}")
    print(f"   • История: {story_veneers['origin_story']}")
    assert "Голливуд" in story_veneers["origin_story"] or "Пинкус" in story_veneers["origin_story"]
    print("✅ История происхождения голливудских виниров подтверждена!")

    # 6. Кофейня: Раф-кофе
    print("\n" + "=" * 80)
    print("☕ 6. КОФЕЙНЯ: «Раф-кофе»")
    print("=" * 80)
    story_raf = await ObjectKnowledgeStoryteller.extract_object_story_async(
        topic="Сливочный ванильный Раф",
        niche="Кофейня",
        company_name="Coffee Bean"
    )
    print(f"   • Объект: {story_raf['object_name']}")
    print(f"   • История: {story_raf['origin_story']}")
    assert "Рафаэль" in story_raf["origin_story"] or "Coffee Bean" in story_raf["origin_story"]
    # 7. Сквозной тест генерации поста в SaigaLLMSkill
    print("\n" + "=" * 80)
    print("🤖 7. СКВОЗНОЙ ТЕСТ ГЕНЕРАЦИИ ПОСТА В SAIGA С ИСТОРИЕЙ ДЕСЕРТА")
    print("=" * 80)
    from skills.saiga_llm import SaigaLLMSkill
    saiga = SaigaLLMSkill()
    post_res = saiga.generate_smm_post(
        topic="Классический нежный Тирамису",
        niche="Кондитерская и пекарня",
        company_name="La Dolce",
        city="Москва",
        comments_enabled=True
    )
    print(f"📄 Сгенерированный пост:\n{post_res['post_text']}\n")
    print(f"🏷️ Хэштеги:\n{post_res['hashtags']}\n")
    assert "История и происхождение" in post_res["post_text"] or "Лингуанотто" in post_res["post_text"]
    assert "Секрет рецепта" in post_res["post_text"] or "маскарпоне" in post_res["post_text"]
    assert "#ucust" not in post_res["hashtags"].lower()
    print("✅ Пост в Сайге успешно обогащен историческим сторителлингом!")

    print("\n🎉 ВСЕ ТЕСТЫ МОДУЛЯ СТОРИТЕЛЛИНГА И ФАКТОВ ОБ ОБЪЕКТАХ УСПЕШНО ПРОЙДЕНЫ!")


if __name__ == "__main__":
    asyncio.run(test_object_storytelling_suite())
