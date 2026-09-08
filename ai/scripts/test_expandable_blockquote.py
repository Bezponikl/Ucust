# -*- coding: utf-8 -*-
"""
test_expandable_blockquote.py
Тестирование модуля ExpandableBlockquoteFormatter и его интеграции с генерацией постов в UCust AI.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from skills.expandable_blockquote import ExpandableBlockquoteFormatter
from core.orchestrator import UnifiedOrchestrator


async def run_tests():
    print("=" * 75)
    print("🚀 ТЕСТИРОВАНИЕ EXPANDABLE BLOCKQUOTE (TELEGRAM BOT API 7.2+ & WEB UI)")
    print("=" * 75)

    # -------------------------------------------------------------
    # ТЕСТ 1: Базовые обёртки (HTML, MarkdownV2, Details)
    # -------------------------------------------------------------
    print("\n[ТЕСТ 1] Проверка базовых методов оборачивания...")
    content = "• Капучино — 250 ₽\n• Флэт Уайт — 290 ₽\n• Раф Цитрус — 320 ₽"
    
    html_res = ExpandableBlockquoteFormatter.wrap_html(content, title="Меню напитков:")
    print(f"\nHTML Output:\n{html_res}")
    assert "<blockquote expandable>" in html_res
    assert "<b>Меню напитков:</b>" in html_res
    assert "</blockquote>" in html_res

    md_res = ExpandableBlockquoteFormatter.wrap_markdown_v2(content, title="Меню напитков:")
    print(f"\nMarkdownV2 Output:\n{md_res}")
    assert "**>*Меню напитков:*" in md_res
    assert "**>• Капучино — 250 ₽" in md_res

    details_res = ExpandableBlockquoteFormatter.wrap_details(content, summary="Посмотреть всё меню ▾")
    print(f"\nWeb Details Output:\n{details_res}")
    assert "<details>" in details_res
    assert "<summary>Посмотреть всё меню ▾</summary>" in details_res
    assert "</details>" in details_res
    print("✅ [ТЕСТ 1 ПРОЙДЕН] Базовые обёртки работают корректно!")

    # -------------------------------------------------------------
    # ТЕСТ 2: Автоматическое обнаружение секций (Прайсы, Условия, FAQ)
    # -------------------------------------------------------------
    print("\n[ТЕСТ 2] Автоматическое распознавание прайсов и правил в тексте поста...")
    
    sample_post = (
        "Утро должно начинаться с правильного кофе! В «Maison Cafe» мы обновили сезонное меню ☕✨\n\n"
        "Прайс-лист на авторские напитки:\n"
        "• Черничный Латте — 320 ₽\n"
        "• Фисташковый Раф — 350 ₽\n"
        "• Матча на кокосовом — 290 ₽\n\n"
        "Условия нашей программы лояльности:\n"
        "• Приходи со своей кружкой и получай скидку 15%\n"
        "• 6-й кофе в подарок по карте гостя\n\n"
        "Ждём вас ежедневно с 8:00 до 22:00 на Арбате, 10! 👇"
    )

    wrapped_post, count = ExpandableBlockquoteFormatter.auto_wrap_sections(sample_post, mode="html")
    print(f"\nАвтоматически оформленный пост (Найдено блоков: {count}):\n")
    print(wrapped_post)
    
    assert count >= 2, f"Ожидалось минимум 2 блока, найдено: {count}"
    assert wrapped_post.count("<blockquote expandable>") == count
    print(f"\n✅ [ТЕСТ 2 ПРОЙДЕН] Успешно свернуто {count} смысловых блока!")

    # -------------------------------------------------------------
    # ТЕСТ 3: Извлечение структурированных блоков и очистка (Strip)
    # -------------------------------------------------------------
    print("\n[ТЕСТ 3] Извлечение блоков в JSON DTO и очистка для VK/OK...")
    blocks = ExpandableBlockquoteFormatter.extract_blocks(wrapped_post)
    print(f"Извлеченные блоки ({len(blocks)} шт.):")
    for b in blocks:
        print(f"  • [{b['format']}] Title: '{b['title']}', Длина: {b['char_length']} симв.")
    
    assert len(blocks) == count
    
    # Очистка
    stripped = ExpandableBlockquoteFormatter.strip_expandable_blockquote(wrapped_post)
    assert "<blockquote" not in stripped
    assert "</blockquote>" not in stripped
    assert "Черничный Латте — 320 ₽" in stripped
    print("\n✅ [ТЕСТ 3 ПРОЙДЕН] Извлечение блоков и strip-очистка для мультиплатформенности работают без потерь текста!")

    # -------------------------------------------------------------
    # ТЕСТ 4: Сквозная генерация через UnifiedOrchestrator
    # -------------------------------------------------------------
    print("\n[ТЕСТ 4] Сквозная генерация поста через UnifiedOrchestrator с Expandable Blockquote...")
    orchestrator = UnifiedOrchestrator()
    
    post_req = {
        "company_name": "Maison Cafe",
        "niche": "Кофейня",
        "prompt": "хочу пост про наше новое меню и скидки со своей кружкой",
        "generate_image": False,
        "expandable_blockquote": True
    }
    
    res = await orchestrator.execute_task(task_type="generate_post", user_data=post_req)
    
    print("\nОтвет оркестратора:")
    print(f"  • Status: {res.get('status')}")
    print(f"  • Has Expandable: {res.get('has_expandable_blockquote')}")
    print(f"  • Blocks count: {len(res.get('expandable_blocks', []))}")
    print(f"  • HTML Preview:\n{res.get('post_text_html')[:250]}...\n")
    
    assert res.get("status") == "success"
    assert "post_text" in res
    assert "post_text_html" in res
    assert "post_text_tg_markdown" in res
    assert "expandable_blocks" in res
    
    print("=" * 75)
    print("🎉 ВСЕ ТЕСТЫ EXPANDABLE BLOCKQUOTE УСПЕШНО ПРОЙДЕНЫ (PASS 100%)!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(run_tests())
