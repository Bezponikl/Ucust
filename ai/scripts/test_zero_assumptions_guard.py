"""
test_zero_assumptions_guard.py
======================================================================
Тестирование модуля защиты от додумываний и галлюцинаций (ZeroAssumptionsGuard):
1. Защита от вымышленных скидок (скидка 70% без источника -> специальные приятные условия).
2. Защита от вымышленного графика 24/7.
3. Защита от нереалистичной доставки (доставим за 5 минут).
4. Защита от опасных псевдо-медицинских обещаний.
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from skills.zero_assumptions_guard import ZeroAssumptionsGuard


def test_zero_assumptions_guard_suite():
    print("=" * 80)
    print("🛡️ ТЕСТИРОВАНИЕ СТРАЖА ЗАЩИТЫ ОТ ДОДУМЫВАНИЙ И ГАЛЛЮЦИНАЦИЙ (ZERO ASSUMPTIONS)")
    print("=" * 80)

    # 1. Тест на вымышленную скидку
    raw_discount_text = "Только сегодня дарим скидку на 70% на весь ассортимент!"
    cleaned_discount = ZeroAssumptionsGuard.sanitize_assumptions(raw_discount_text, rag_facts="")
    print(f"📥 Исходный текст со скидкой 70%: {raw_discount_text}")
    print(f"📤 Очищенный текст:               {cleaned_discount}")
    assert "70%" not in cleaned_discount
    print("✅ Вымышленная скидка успешно нивелирована!")

    # 2. Тест на неподтвержденный график 24/7
    raw_24_7_text = "Ждем вас круглосуточно 24/7 в нашем шоуруме!"
    cleaned_24_7 = ZeroAssumptionsGuard.sanitize_assumptions(raw_24_7_text, contacts={})
    print(f"\n📥 Исходный текст 24/7: {raw_24_7_text}")
    print(f"📤 Очищенный текст:     {cleaned_24_7}")
    assert "24/7" not in cleaned_24_7
    assert "круглосуточно" not in cleaned_24_7
    print("✅ Неподтвержденный график 24/7 успешно заменен на безопасный!")

    # 3. Тест на доставку за 5 минут
    raw_delivery_text = "Быстрая доставка за 5 минут прямо к вашей двери!"
    cleaned_delivery = ZeroAssumptionsGuard.sanitize_assumptions(raw_delivery_text)
    print(f"\n📥 Исходный текст доставки: {raw_delivery_text}")
    print(f"📤 Очищенный текст:         {cleaned_delivery}")
    assert "за 5 минут" not in cleaned_delivery
    print("✅ Нереалистичные сроки доставки успешно сглажены!")

    # 4. Тест валидации безопасности
    report = ZeroAssumptionsGuard.validate_content_safety("Скидка на 80% и 100% излечение всех болезней")
    print(f"\n📊 Отчет валидации безопасности:\n   • Безопасен: {report['is_safe']}\n   • Проблемы: {report['issues']}")
    assert not report["is_safe"]
    assert len(report["issues"]) >= 2
    print("✅ Валидатор безопасности точно выявил потенциальные риски!")

    print("\n🎉 ВСЕ ТЕСТЫ ZERO-ASSUMPTIONS GUARD УСПЕШНО ПРОЙДЕНЫ!")


if __name__ == "__main__":
    test_zero_assumptions_guard_suite()
