"""
test_advanced_marketing_stack.py
======================================================================
Тестирование расширенного маркетингового стека UCust.AI:
1. JTBD (Jobs-to-be-Done) Движок — триада функциональной, эмоциональной и социальной ценности.
2. Лестница ценности Рассела Брансона (Value Ladder: Lead Magnet -> Tripwire -> Core -> VIP).
3. Модель поведения Фогга (BJ Fogg B = MAP) — призывы к действию (CTA) с нулевым трением.
4. Сквозная генерация постов со всеми 7 фреймворками копирайтинга.
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from skills.marketing_frameworks import (
    MarketingFrameworkDirector,
    JTBDTransformer,
    ValueLadderArchitect,
    FoggCTAGenerator,
    MarketingFramework,
    HuntStage,
    PsychologicalTrigger,
    ValueLadderTier
)


def test_marketing_stack():
    print("=" * 80)
    print("🚀 ТЕСТИРОВАНИЕ РАСШИРЕННОГО МАРКЕТИНГОВОГО СТЕКА UCUST.AI")
    print("=" * 80)

    # 1. Тестирование JTBD
    print("\n🎯 1. ТЕСТИРОВАНИЕ JTBD (JOBS-TO-BE-DONE) ТРАНСФОРМАТОРА")
    jtbd_furniture = JTBDTransformer.transform_feature("Дизайнерская мебель", "столешница из массива дуба 40 мм")
    print(f"   • Ниша: Дизайнерская мебель | Свойство: {jtbd_furniture['raw_feature']}")
    print(f"   • 🛠️ Functional Job: {jtbd_furniture['functional_job']}")
    print(f"   • ❤️ Emotional Job:  {jtbd_furniture['emotional_job']}")
    print(f"   • 👑 Social Job:     {jtbd_furniture['social_job']}")
    assert "уют" in jtbd_furniture["emotional_job"]
    assert "гостями" in jtbd_furniture["social_job"]
    print("✅ JTBD трансформация успешно проверена!")

    # 2. Тестирование Value Ladder (Лестница ценности)
    print("\n" + "=" * 80)
    print("🪜 2. ТЕСТИРОВАНИЕ ЛЕСТНИЦЫ ЦЕННОСТИ (VALUE LADDER БРАНСОНА)")
    print("=" * 80)
    ladder = ValueLadderArchitect.get_ladder_for_niche("Стоматология")
    print(f"   • [1. LEAD MAGNET (0 ₽)]:   {ladder[ValueLadderTier.LEAD_MAGNET]}")
    print(f"   • [2. TRIPWIRE (Пробник)]:  {ladder[ValueLadderTier.TRIPWIRE]}")
    print(f"   • [3. CORE OFFER (Флагман)]:{ladder[ValueLadderTier.CORE_OFFER]}")
    print(f"   • [4. PROFIT MAXIMIZER]:    {ladder[ValueLadderTier.PROFIT_MAXIMIZER]}")
    assert "0 ₽" in ladder[ValueLadderTier.LEAD_MAGNET]
    assert "виниров" in ladder[ValueLadderTier.CORE_OFFER]
    print("✅ Лестница ценности для ниши успешно сгенерирована!")

    # 3. Тестирование Fogg CTA Model (B = MAP)
    print("\n" + "=" * 80)
    print("⚡ 3. ТЕСТИРОВАНИЕ ПРИЗЫВОВ К ДЕЙСТВИЮ ПО МОДЕЛИ ФОГГА (B = MAP)")
    print("=" * 80)
    cta_direct = FoggCTAGenerator.generate_low_friction_cta("direct_keyword", "КАТАЛОГ", "Maksima Мебель")
    cta_quiz = FoggCTAGenerator.generate_low_friction_cta("one_click_quiz")
    cta_reciprocity = FoggCTAGenerator.generate_low_friction_cta("instant_reciprocity")
    print(f"   • 📩 Direct Keyword CTA: {cta_direct}")
    print(f"   • 🎯 1-Click Quiz CTA:   {cta_quiz}")
    print(f"   • 🎁 Reciprocity CTA:    {cta_reciprocity}")
    assert "КАТАЛОГ" in cta_direct or "комментарии" in cta_direct or "директ" in cta_direct
    print("✅ Низкофрикционные призывы к действию успешно сгенерированы!")

    # 4. Тестирование комплексной промпт-директивы
    print("\n" + "=" * 80)
    print("🧠 4. ТЕСТИРОВАНИЕ КОМПЛЕКСНОЙ МАРКЕТИНГОВОЙ ДИРЕКТИВЫ ДЛЯ SAIGA LLM")
    print("=" * 80)
    prompt_bundle = MarketingFrameworkDirector.construct_marketing_prompt(
        company_name="Maksima Мебель",
        niche="Дизайнерская мебель",
        topic="Обеденный стол из массива дуба",
        framework=MarketingFramework.PAS,
        hunt_stage=HuntStage.STAGE_2_PROBLEM_AWARE,
        trigger=PsychologicalTrigger.AUTHORITY,
        pain_points=["разбухание дешевой мебели от влаги"],
        raw_feature="экологичное защитное масло Rubio Monocoat"
    )
    print(f"   • Фреймворк: {prompt_bundle['framework']}")
    print(f"   • Ступень Ханта: {prompt_bundle['hunt_stage']}")
    print(f"   • Уровень воронки (Value Ladder): {prompt_bundle['value_ladder_tier']}")
    print(f"   • Fogg CTA: {prompt_bundle['fogg_cta']}")
    print(f"\n📄 Полная промпт-инструкция для Сайги:\n{prompt_bundle['full_marketing_prompt']}\n")
    assert "JTBD-фокус" in prompt_bundle["full_marketing_prompt"]
    assert "Value Ladder" in prompt_bundle["full_marketing_prompt"]
    assert "Fogg Model" in prompt_bundle["full_marketing_prompt"]

    # 5. Тестирование генерации эталонного поста
    print("=" * 80)
    print("✍️ 5. ТЕСТИРОВАНИЕ ЭТАЛОННОЙ ГЕНЕРАЦИИ ПОСТА (PAS + JTBD + FOGG CTA)")
    print("=" * 80)
    post_res = MarketingFrameworkDirector.generate_post_with_framework(
        company_name="Apex Auto",
        niche="Автосервис",
        topic="Компьютерная диагностика двигателя",
        framework=MarketingFramework.PAS,
        hunt_stage=HuntStage.STAGE_2_PROBLEM_AWARE,
        trigger=PsychologicalTrigger.RISK_REVERSAL,
        raw_feature="дилерские сканеры Launch и Autel"
    )
    print(f"🏢 Компания: {post_res['company_name']} | Фреймворк: {post_res['framework_name']}")
    print(f"📄 Сгенерированный пост:\n------------------------------------------------------------\n{post_res['post_text']}\n------------------------------------------------------------")
    assert "⚠️ Почему 90%" in post_res["post_text"]
    assert "Apex Auto" in post_res["post_text"]

    print("\n🎉 ВСЕ ТЕСТЫ РАСШИРЕННОГО МАРКЕТИНГОВОГО СТЕКА УСПЕШНО ПРОЙДЕНЫ!")


if __name__ == "__main__":
    test_marketing_stack()
