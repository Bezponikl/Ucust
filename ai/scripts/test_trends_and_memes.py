"""
test_trends_and_memes.py
======================================================================
Тестирование базы знаний современных трендов и мемов 2024-2026 гг.
и еженедельного коллектора TrendsAndMemesCollector:
1. Загрузка и валидация trends_and_memes.json.
2. Подбор и адаптация мемов под ниши (Мебель, Кофейня, Автосервис, Стоматология).
3. Формирование промпт-директив для SaigaLLM с Anti-Cringe правилами.
4. Еженедельное обновление и синхронизация в Clean RAG.
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

from collectors.trends_collector import TrendsAndMemesCollector
from rag import CleanRAGPipeline


async def test_trends_and_memes_system():
    print("=" * 80)
    print("🔥 ТЕСТИРОВАНИЕ БАЗЫ ЗНАНИЙ ТРЕНДОВ И МЕМОВ ДЛЯ LLM 2023 г.")
    print("=" * 80)

    # 1. Инициализация коллектора
    collector = TrendsAndMemesCollector()
    all_memes = collector.get_all_memes()
    slang = collector.get_slang_lexicon()

    print(f"✅ База знаний успешно загружена из JSON:")
    print(f"   • Всего актуальных мемов и форматов: {len(all_memes)}")
    print(f"   • Слов современного сленга: {len(slang)} ({', '.join(list(slang.keys())[:5])}...)")
    assert len(all_memes) >= 5
    assert "вайб" in slang
    assert "база" in slang

    # 2. Тестирование адаптации под ниши
    niches_to_test = [
        ("Maksima Мебель", "Дизайнерская мебель из массива дуба"),
        ("CoffeeBean", "Кофейня и свежая выпечка"),
        ("ДентаЛюкс", "Стоматология и имплантация"),
        ("Apex Auto", "Автосервис и диагностика")
    ]

    print("\n" + "=" * 80)
    print("🎭 2. ТЕСТИРОВАНИЕ АДАПТАЦИИ МЕМОВ ПОД НИШИ И ГЕНЕРАЦИИ ДИРЕКТИВ")
    print("=" * 80)

    for comp, niche in niches_to_test:
        trends = collector.get_trends_for_niche(niche)
        print(f"\n🏢 Компания: «{comp}» | Ниша: {niche}")
        print(f"   Найдено подходящих трендов: {len(trends)}")
        assert len(trends) > 0

        directive = collector.generate_meme_prompt_directive(comp, niche, meme_id=trends[0]["id"])
        print("-" * 60)
        print(directive)
        print("-" * 60)
        assert comp in directive
        assert "Anti-Cringe" in directive

    # 3. Тестирование еженедельного обновления (Weekly Update)
    print("\n" + "=" * 80)
    print("📅 3. ТЕСТИРОВАНИЕ ЕЖЕНЕДЕЛЬНОГО ОБНОВЛЕНИЯ ТРЕНДОВ (WEEKLY SYNC)")
    print("=" * 80)

    import time
    dynamic_id = f"meme_autumn_coffee_vibes_{int(time.time())}"
    new_fresh_trend = {
        "id": dynamic_id,
        "name": "Осенний уютный вайб / Плед и тыквенный латте",
        "trend_period": "2026",
        "emotion": "Теплота, ностальгия, сезонный комфорт",
        "meaning": "Сезонное желание укутаться в тепло и порадовать себя согревающим напитком.",
        "business_adaptation": {
            "coffee": "Спешл-меню тыквенно-пряного латте с корицей.",
            "furniture": "Уютные мягкие пледы и кресла для осенних вечеров с книгой."
        },
        "viral_hooks": ["Тот самый день, когда официально пора доставать любимый свитер..."],
        "anti_cringe_rule": "Акцент на искренний визуальный уют и тепло."
    }

    update_res = collector.update_weekly_trends_sync([new_fresh_trend])
    print(f"✅ Результат еженедельного обновления: {update_res}")
    assert update_res["status"] == "success"
    assert update_res["new_added_count"] == 1

    # 4. Тестирование индексации в Clean RAG и поиска
    print("\n" + "=" * 80)
    print("🧠 4. ТЕСТИРОВАНИЕ ИНДЕКСАЦИИ В CLEAN RAG И СЕМАНТИЧЕСКОГО ПОИСКА")
    print("=" * 80)

    rag = CleanRAGPipeline(target_chunk_tokens=300, overlap_tokens=50, min_confidence_threshold=0.0)
    indexed_count = await collector.index_trends_to_rag(rag)
    print(f"✅ Успешно проиндексировано {indexed_count} документов о трендах в RAG-память.")

    query = "мем Скуф и Альтушка для рекламы мебели и кресла"
    context_result = await rag.query_async(query)
    print(f"\n🔍 Поисковый запрос в RAG: «{query}»")
    print(f"   Достаточность контекста: {context_result.has_sufficient_context}")
    print(f"   Top Score: {context_result.top_score:.3f}")
    print(f"   Форматированный контекст трендов:\n{context_result.formatted_context[:250]}...\n")
    assert context_result.has_sufficient_context is True
    assert "Мем" in context_result.formatted_context or "тренд" in context_result.formatted_context.lower()

    print("🎉 ВСЕ ТЕСТЫ БАЗЫ ЗНАНИЙ ТРЕНДОВ И МЕМОВ УСПЕШНО ПРОЙДЕНЫ!")


if __name__ == "__main__":
    asyncio.run(test_trends_and_memes_system())
