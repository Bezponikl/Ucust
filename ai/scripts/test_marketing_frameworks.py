"""
test_marketing_frameworks.py
======================================================================
Тестирование усиления маркетинговых навыков без дообучения нейросети:
1. 7 формул копирайтинга: AIDA, PAS, BAB, 4P, StoryBrand, Hook-Story-Offer, FAB.
2. 5 ступеней прогрева по Лестнице Ханта (Unaware -> Most Aware).
3. 5 психологических триггеров Чалдини (Social Proof, Scarcity, Authority, Reciprocity, Risk Reversal).
4. Автоматическая раскладка 30-дневного контент-плана по фреймворкам.
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
    MarketingFramework,
    HuntStage,
    PsychologicalTrigger
)
from skills.content_strategy_engine import ContentStrategyEngine


def test_all_frameworks_generation():
    print("=" * 80)
    print("🧠 1. ТЕСТИРОВАНИЕ 7 МАРКЕТИНГОВЫХ ФРЕЙМВОРКОВ И ТРИГГЕРОВ ЧАЛДИНИ")
    print("=" * 80)

    frameworks_to_test = [
        (MarketingFramework.AIDA, HuntStage.STAGE_5_MOST_AWARE, PsychologicalTrigger.SCARCITY_FOMO),
        (MarketingFramework.PAS, HuntStage.STAGE_2_PROBLEM_AWARE, PsychologicalTrigger.AUTHORITY),
        (MarketingFramework.BAB, HuntStage.STAGE_1_UNAWARE, PsychologicalTrigger.RECIPROCITY),
        (MarketingFramework.FOUR_P, HuntStage.STAGE_4_PRODUCT_AWARE, PsychologicalTrigger.SOCIAL_PROOF),
        (MarketingFramework.STORYBRAND, HuntStage.STAGE_4_PRODUCT_AWARE, PsychologicalTrigger.RISK_REVERSAL),
        (MarketingFramework.HOOK_STORY_OFFER, HuntStage.STAGE_3_SOLUTION_AWARE, PsychologicalTrigger.SCARCITY_FOMO),
        (MarketingFramework.FAB, HuntStage.STAGE_3_SOLUTION_AWARE, PsychologicalTrigger.AUTHORITY)
    ]

    for f_enum, stage_enum, trig_enum in frameworks_to_test:
        res = MarketingFrameworkDirector.generate_post_with_framework(
            company_name="Maksima Мебель",
            niche="Дизайнерская мебель из массива",
            topic="Обеденные столы из массива дуба",
            framework=f_enum,
            hunt_stage=stage_enum,
            trigger=trig_enum
        )
        print(f"\n✨ Фреймворк: {res['framework_name']} | Ступень: {res['hunt_stage']} | Триггер: {res['psychological_trigger']}")
        print("-" * 60)
        print(res["post_text"])
        print("-" * 60)
        assert len(res["post_text"]) > 150
        assert "Maksima" in res["post_text"]

    print("\n✅ ВСЕ 7 МАРКЕТИНГОВЫХ ФРЕЙМВОРКОВ УСПЕШНО СГЕНЕРИРОВАЛИ ЭТАЛОННЫЕ ТЕКСТЫ!")


def test_content_plan_framework_integration():
    print("\n" + "=" * 80)
    print("📅 2. ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ ФРЕЙМВОРКОВ В 7-ДНЕВНЫЙ КОНТЕНТ-ПЛАН")
    print("=" * 80)

    engine = ContentStrategyEngine()
    plan = engine.generate_content_plan(
        company_name="ДентаЛюкс",
        niche="Стоматология и имплантация",
        days_count=7,
        city="Москва"
    )

    items = plan["plan_days"]
    print(f"✅ Успешно сгенерирован контент-план на {len(items)} дней:")
    for item in items:
        print(f"   • День {item['day']} [{item['stage']}]: Ступень: {item['hunt_stage'].upper()} | Фреймворк: {item['marketing_framework']} | Триггер: {item['psychological_trigger']}")
        print(f"     Тема: {item['topic'][:65]}...")
        assert "prompt_directive" in item
        assert item["marketing_framework"] in [f.value for f in MarketingFramework]

    print("\n🎉 ВСЕ ТЕСТЫ МАРКЕТИНГОВОГО ДИРЕКТОРА УСПЕШНО ПРОЙДЕНЫ!")


if __name__ == "__main__":
    test_all_frameworks_generation()
    test_content_plan_framework_integration()
