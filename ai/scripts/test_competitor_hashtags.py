"""
test_competitor_hashtags.py
======================================================================
Тестирование поискового движка хэштегов конкурентов (Niche Competitor Hashtags):
1. Гео-коммерческие поисковые теги конкурентов (#мебельташкент, #стоматологияспб, #автосервисмосква).
2. Категорийные теги для поиска аналогичных постов других пользователей (#столыизмассива, #лофтмебель).
3. Предметные теги по конкретной теме публикации (#обеденныйстол, #винирыдопосле, #заменамасла).
4. Защита от спама и утечек (Anti-Leak & Anti-Spam): 100% блокировка #UCust, #AI, #нейросеть, #вкуснаяеда, #праздник.
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from skills.competitor_hashtags import NicheCompetitorHashtagEngine
from skills.saiga_llm import SaigaLLMSkill
from skills.marketing_frameworks import MarketingFrameworkDirector, MarketingFramework, HuntStage, PsychologicalTrigger


def test_competitor_hashtags_suite():
    print("=" * 80)
    print("🔍 ТЕСТИРОВАНИЕ ПОИСКОВОГО ДВИЖКА ХЭШТЕГОВ КОНКУРЕНТОВ (NICHE COMPETITOR HASHTAGS)")
    print("=" * 80)

    # 1. Тестирование ниши «Мебель» (Ташкент)
    print("\n🛋️ 1. НИША: «Дизайнерская мебель» (г. Ташкент)")
    tags_furniture = NicheCompetitorHashtagEngine.get_competitor_hashtags(
        niche="Дизайнерская мебель",
        topic="Обеденный стол из массива дуба в гостиную",
        city="Ташкент",
        company_name="Maksima Мебель"
    )
    print(f"   • Сгенерированные теги:\n     {tags_furniture}")
    assert "#мебельташкент" in tags_furniture or "#мебельназаказташкент" in tags_furniture
    assert "#столыизмассива" in tags_furniture or "#обеденныйстол" in tags_furniture
    assert "#ucust" not in tags_furniture.lower()
    print("✅ Теги для мебели точно соответствуют поисковым запросам конкурентов!")

    # 2. Тестирование ниши «Стоматология» (Санкт-Петербург)
    print("\n" + "=" * 80)
    print("🦷 2. НИША: «Стоматология и виниры» (г. Санкт-Петербург)")
    print("=" * 80)
    tags_dental = NicheCompetitorHashtagEngine.get_competitor_hashtags(
        niche="Стоматология",
        topic="Установка керамических виниров E-Max",
        city="Санкт-Петербург",
        company_name="ДентаЛюкс"
    )
    print(f"   • Сгенерированные теги:\n     {tags_dental}")
    assert "#стоматологияспб" in tags_dental or "#стоматологиявиниры" in tags_dental or "стоматолог" in tags_dental
    assert "виниры" in tags_dental
    print("✅ Теги для стоматологии сформированы по коммерческим шаблонам!")

    # 3. Тестирование ниши «Автосервис» (Москва)
    print("\n" + "=" * 80)
    print("🚗 3. НИША: «Автосервис и диагностика» (г. Москва)")
    print("=" * 80)
    tags_auto = NicheCompetitorHashtagEngine.get_competitor_hashtags(
        niche="Автосервис",
        topic="Комплексная компьютерная диагностика и замена масла",
        city="Москва",
        company_name="Apex Auto"
    )
    print(f"   • Сгенерированные теги:\n     {tags_auto}")
    assert "#автосервисмосква" in tags_auto or "#стомосква" in tags_auto or "автосервис" in tags_auto
    assert "диагностика" in tags_auto or "масл" in tags_auto
    print("✅ Теги для автосервиса сформированы корректно!")

    # 4. Проверка строгого Anti-Leak и Anti-Spam фильтра
    print("\n" + "=" * 80)
    print("🛡️ 4. ТЕСТИРОВАНИЕ ANTI-LEAK & ANTI-SPAM ФИЛЬТРАЦИИ")
    print("=" * 80)
    blocked_test_list = ["#UCust", "#ai", "#нейросеть", "#вкуснаяеда", "#шефповар", "#праздник", "#лайк"]
    for blocked in blocked_test_list:
        clean_tag = blocked.replace("#", "").lower()
        assert clean_tag in NicheCompetitorHashtagEngine.BLOCKED_TAGS
    print("✅ Все бессмысленные и спам-теги (#UCust, #вкуснаяеда, #праздник) надежно заблокированы!")

    # 5. Сквозной тест через SaigaLLMSkill и MarketingFrameworkDirector
    print("\n" + "=" * 80)
    print("🤖 5. СКВОЗНОЙ ТЕСТ ГЕНЕРАЦИИ ПОСТА В SAIGA & MARKETING DIRECTOR")
    print("=" * 80)
    fw_post = MarketingFrameworkDirector.generate_post_with_framework(
        company_name="Maksima Мебель",
        niche="Дизайнерская мебель",
        topic="Обеденный стол из дуба",
        framework=MarketingFramework.PAS,
        hunt_stage=HuntStage.STAGE_2_PROBLEM_AWARE,
        trigger=PsychologicalTrigger.AUTHORITY,
        contacts={"city": "Ташкент"}
    )
    print(f"📄 Хэштеги из MarketingFrameworkDirector:\n   {fw_post['hashtags']}")
    assert "#мебельташкент" in fw_post['hashtags'] or "#столыизмассива" in fw_post['hashtags'] or "#дизайнерскаямебель" in fw_post['hashtags']
    assert "#ucust" not in fw_post['hashtags'].lower()

    print("\n🎉 ВСЕ ТЕСТЫ ДВИЖКА ХЭШТЕГОВ КОНКУРЕНТОВ УСПЕШНО ПРОЙДЕНЫ!")


if __name__ == "__main__":
    test_competitor_hashtags_suite()
