"""
test_tariff_orchestration.py
======================================================================
Тестирование квотирования и синхронизации календаря генераций с тарифом:
1. Запрос квоты тарифа клиента из Бэкенда (Start, Business, Enterprise).
2. Расчет календарной сетки с учетом разрешенных дней недели (Пн/Ср/Пт или Пн-Пт).
3. Проверка часовых поясов и лимита постов.
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio
from datetime import datetime

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from bridge.backend_posting_bridge import BackendPostingBridge


async def test_tariff_orchestration_suite():
    print("=" * 80)
    print("💳 ТЕСТИРОВАНИЕ КВОТИРОВАНИЯ И КАЛЕНДАРЯ ГЕНЕРАЦИЙ ПО ТАРИФУ КЛИЕНТА")
    print("=" * 80)

    bridge = BackendPostingBridge()

    # 1. Запрос тарифа Business
    print("\n📦 1. ЗАПРОС ТАРИФА КЛИЕНТА (BUSINESS: 20 постов/мес, Пн–Пт)")
    quota_biz = await bridge.fetch_client_subscription_quota_async("client_dentallux_101")
    print(f"   • Тариф: {quota_biz['tier_name']}")
    print(f"   • Лимит постов в месяц: {quota_biz['monthly_post_limit']}")
    print(f"   • Разрешенные дни недели: {quota_biz['allowed_days_of_week']} (Пн-Пт)")
    print(f"   • Часовой пояс: {quota_biz['client_timezone']}")
    assert quota_biz["monthly_post_limit"] == 20

    # 2. Расчет календарных слотов для тарифа Business
    print("\n" + "=" * 80)
    print("📅 2. ГЕНЕРАЦИЯ КАЛЕНДАРНОЙ СЕТКИ ПО ТАРИФУ BUSINESS")
    print("=" * 80)
    slots_biz = bridge.calculate_allowed_calendar_dates(quota_biz, start_date=datetime(2026, 9, 1))
    print(f"   • Сгенерировано слотов в календаре: {len(slots_biz)}")
    print(f"   • Первый слот: {slots_biz[0]['date']} {slots_biz[0]['time']} ({slots_biz[0]['weekday']})")
    print(f"   • Пятый слот:  {slots_biz[4]['date']} {slots_biz[4]['time']} ({slots_biz[4]['weekday']})")
    print(f"   • Последний:   {slots_biz[-1]['date']} {slots_biz[-1]['time']} ({slots_biz[-1]['weekday']})")
    assert len(slots_biz) == 20
    # Проверяем, что нет выходных (Saturday / Sunday)
    for s in slots_biz:
        assert s["weekday"] not in ["Saturday", "Sunday"]
    print("✅ Все 20 постов распределены строго по будним дням (Пн-Пт)!")

    # 3. Тест тарифа Start (12 постов, только Пн, Ср, Пт)
    print("\n" + "=" * 80)
    print("📦 3. ТАРИФ START (12 постов/мес, 3 раза в неделю: Пн, Ср, Пт)")
    print("=" * 80)
    quota_start = {
        "client_id": "client_cafe_02",
        "tier_name": "START",
        "monthly_post_limit": 12,
        "allowed_days_of_week": [0, 2, 4], # Пн(0), Ср(2), Пт(4)
        "preferred_hours": ["09:30"],
        "client_timezone": "Asia/Tashkent"
    }
    slots_start = bridge.calculate_allowed_calendar_dates(quota_start, start_date=datetime(2026, 9, 1))
    print(f"   • Сгенерировано слотов: {len(slots_start)}")
    for s in slots_start[:4]:
        print(f"     -> Слот #{s['slot_index']}: {s['date']} {s['time']} ({s['weekday']})")
    assert len(slots_start) == 12
    for s in slots_start:
        assert s["weekday"] in ["Monday", "Wednesday", "Friday"]
    print("✅ Сетка тарифа START строго следует дням Пн, Ср, Пт без перелимита!")

    print("\n🎉 ВСЕ ТЕСТЫ ТАРИФНОЙ СИНХРОНИЗАЦИИ КАЛЕНДАРЯ УСПЕШНО ПРОЙДЕНЫ!")


if __name__ == "__main__":
    asyncio.run(test_tariff_orchestration_suite())
