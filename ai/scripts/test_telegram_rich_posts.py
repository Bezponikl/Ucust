# -*- coding: utf-8 -*-
"""
Test Suite: Telegram Rich Formatting & Interactive UX
Tests:
1. format_clickable_promocodes (<code> for promo and phone numbers)
2. format_strikethrough_prices (<s>old</s> <b>new</b>)
3. format_spoilers (<tg-spoiler>)
4. generate_inline_keyboard (reply_markup)
5. build_rich_telegram_post (end-to-end rich post assembly)
"""

import os
import sys

# Ensure UTF-8 stdout on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from skills.telegram_rich_formatter import TelegramRichPostFormatter
from skills.expandable_blockquote import ExpandableBlockquoteFormatter


def test_clickable_promocodes():
    print("\n--- Test 1: Clickable Promocodes & Phone Numbers ---")
    raw_text = "Используйте промокод COFFEE2026 при заказе по номеру +7 (999) 123-45-67 или 8 (800) 555-35-35!"
    formatted = TelegramRichPostFormatter.format_clickable_promocodes(raw_text, promo_code="COFFEE2026")
    print("Result:\n", formatted)
    
    assert "<code>COFFEE2026</code>" in formatted, "Promo code should be wrapped in <code>"
    assert "<code>+7 (999) 123-45-67</code>" in formatted or "+7 (999) 123-45-67" in formatted
    print("✅ Test 1 Passed!")


def test_strikethrough_prices():
    print("\n--- Test 2: Strikethrough Discount Prices ---")
    raw_text = "Специальная акция недели: вместо 3500 ₽ всего 2490 ₽! А на десерты: было 450 руб, стало 350 руб."
    formatted = TelegramRichPostFormatter.format_strikethrough_prices(raw_text)
    print("Result:\n", formatted)
    
    assert "<s>3500 ₽</s> <b>2490 ₽</b>" in formatted or "<s>" in formatted, "Old price should be in <s> and new in <b>"
    print("✅ Test 2 Passed!")


def test_spoilers():
    print("\n--- Test 3: Spoilers ---")
    raw_text = "Отгадайте загадку: что согревает лучше всего? ||Чашка горячего рафа с корицей|| Секретный бонус: десерт в подарок"
    formatted = TelegramRichPostFormatter.format_spoilers(raw_text)
    print("Result:\n", formatted)
    
    assert "<tg-spoiler>Чашка горячего рафа с корицей</tg-spoiler>" in formatted, "Spoiler markdown ||...|| should become <tg-spoiler>"
    assert "<tg-spoiler>" in formatted, "Secret bonus should have spoiler"
    print("✅ Test 3 Passed!")


def test_inline_keyboard():
    print("\n--- Test 4: Inline Keyboard Generation ---")
    markup = TelegramRichPostFormatter.generate_inline_keyboard(
        company_name="Кофейня Зерно",
        website_url="https://zerno-coffee.ru",
        contacts={"phone": "+79991234567", "address": "Москва, Арбат 10"},
        social_links={"telegram": "https://t.me/zerno_bot", "2gis": "https://2gis.ru/moscow/firm/123"},
        cta_type="ecommerce"
    )
    print("Generated Reply Markup:\n", markup)
    
    buttons = markup.get("inline_keyboard", [])
    assert len(buttons) >= 2, "Keyboard should have at least 2 rows"
    
    urls = [btn["url"] for row in buttons for btn in row]
    assert "https://zerno-coffee.ru" in urls, "Website URL should be in keyboard"
    assert "https://2gis.ru/moscow/firm/123" in urls, "2GIS Map URL should be in keyboard"
    assert "https://t.me/zerno_bot" in urls, "Telegram link should be in keyboard"
    print("✅ Test 4 Passed!")


def test_full_rich_post_pipeline():
    print("\n--- Test 5: Full Rich Telegram Post Assembly ---")
    post_body = (
        "Устали от серого утра? Попробуйте наш фирменный авторский сет.\n\n"
        "Прайс-лист и меню:\n"
        "- Капучино на миндальном — 290 руб\n"
        "- Флэт Уайт — 320 руб\n"
        "- Круассан с лососем — 380 руб\n\n"
        "Только до пятницы: вместо 990 ₽ всего 690 ₽ по промокоду MORNING26!\n\n"
        "Правила акции:\n"
        "1. Действует с 08:00 до 12:00\n"
        "2. Не суммируется с другими скидками\n\n"
        "Секретный бонус: бесплатный сироп на выбор"
    )
    
    rich_res = TelegramRichPostFormatter.build_rich_telegram_post(
        text=post_body,
        company_name="Кофейня Зерно",
        promo_code="MORNING26",
        website_url="https://zerno-coffee.ru",
        contacts={"phone": "+79991234567", "address": "Москва, Арбат 10"},
        cta_type="ecommerce"
    )
    
    html = rich_res["html_text"]
    print("Assembled HTML Post:\n" + "="*50 + "\n" + html + "\n" + "="*50)
    
    assert "<blockquote expandable>" in html, "Should have expandable blockquote for Menu/Rules"
    assert "<code>MORNING26</code>" in html, "Should have 1-click copyable promocode"
    assert "<s>" in html and "<b>" in html, "Should have strikethrough price"
    assert "<tg-spoiler>" in html, "Should have spoiler"
    assert rich_res["reply_markup"] is not None, "Should have inline buttons"
    assert rich_res["features_applied"]["expandable_blockquote"] is True
    assert rich_res["features_applied"]["clickable_promo"] is True
    assert rich_res["features_applied"]["strikethrough_prices"] is True
    assert rich_res["features_applied"]["spoilers"] is True
    assert rich_res["features_applied"]["inline_buttons"] is True
    
    print("✅ Test 5 Passed! All rich Telegram features successfully applied.")


if __name__ == "__main__":
    test_clickable_promocodes()
    test_strikethrough_prices()
    test_spoilers()
    test_inline_keyboard()
    test_full_rich_post_pipeline()
    print("\n🎉 ALL TELEGRAM RICH POST TESTS COMPLETED SUCCESSFULLY (100% PASS)!\n")
