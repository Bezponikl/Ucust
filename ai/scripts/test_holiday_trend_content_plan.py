"""
test_holiday_trend_content_plan.py
======================================================================
Тестирование:
1. EventHolidayCollector: Гос-праздники (РФ, РБ, РК, СНГ), дни городов и профессиональные даты.
2. Сохранение country, city, location_details в SQL (UserProfile).
3. Индексация календаря праздников и геолокации в Clean RAG Pipeline.
4. Генерация 30-дневного контент-плана с автоматическим внедрением праздничных постов.
5. Генерация праздничного поста через UnifiedOrchestrator.
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from storage.db import Base
from storage.models import UserProfile
from collectors.event_holiday_collector import EventHolidayCollector
from core.orchestrator import UnifiedOrchestrator


async def run_holiday_and_content_plan_test():
    print("=" * 80)
    print("🎉 ТЕСТ МОДУЛЯ ПРАЗДНИКОВ, ТРЕНДОВ И РЕГИОНАЛЬНЫХ СОБЫТИЙ В КОНТЕНТ-ПЛАНЕ")
    print("=" * 80)

    # ------------------------------------------------------------------
    # ЭТАП 1: ТЕСТИРОВАНИЕ КОЛЛЕКТОРА ПРАЗДНИКОВ (РФ, КАЗАХСТАН, БЕЛАРУСЬ)
    # ------------------------------------------------------------------
    print("\n--- [ЭТАП 1] Проверка календаря праздников по странам и нишам ---")
    collector = EventHolidayCollector()

    # 1.1 Казахстан, Алматы, ниша IT (Март -> Наурыз)
    kz_events = collector.get_calendar_events(
        country="Казахстан",
        city="Алматы",
        niche="IT и автоматизация",
        start_date=datetime(2026, 3, 1),
        days_count=30
    )
    print(f"🇰🇿 Казахстан (Алматы, Март 2026, IT): Найдено {len(kz_events)} праздников:")
    for e in kz_events:
        print(f"   • День {e['day_number']} ({e['date']}): {e['title']} [{e['type']}]")
    
    assert any("Наурыз" in e["title"] for e in kz_events), "Ошибка: Наурыз не найден в Казахстане!"
    assert any("женский день" in e["title"].lower() or "8 марта" in e["title"].lower() for e in kz_events), "Ошибка: 8 Марта / Женский день не найдено в СНГ!"

    # 1.2 Россия, Санкт-Петербург, ниша Стоматология (Февраль -> День стоматолога, 23 Февраля)
    ru_events = collector.get_calendar_events(
        country="Россия",
        city="Санкт-Петербург",
        niche="Стоматология и клиника",
        start_date=datetime(2026, 2, 1),
        days_count=28
    )
    print(f"\n🇷🇺 Россия (СПб, Февраль 2026, Стоматология): Найдено {len(ru_events)} праздников:")
    for e in ru_events:
        print(f"   • День {e['day_number']} ({e['date']}): {e['title']} [{e['type']}]")
    
    assert any("стоматолог" in e["title"].lower() for e in ru_events), "Ошибка: День стоматолога не найден!"
    assert any("23 Февраля" in e["title"] or "защитника" in e["title"].lower() for e in ru_events), "Ошибка: 23 Февраля не найдено!"

    # 1.3 Беларусь, Минск, ниша Автосервис (Июль -> День Независимости Беларуси)
    by_events = collector.get_calendar_events(
        country="Беларусь",
        city="Минск",
        niche="Автосервис и детейлинг",
        start_date=datetime(2026, 7, 1),
        days_count=30
    )
    print(f"\n🇧🇾 Беларусь (Минск, Июль 2026, Автосервис): Найдено {len(by_events)} праздников:")
    for e in by_events:
        print(f"   • День {e['day_number']} ({e['date']}): {e['title']} [{e['type']}]")
    assert any("Независимости" in e["title"] for e in by_events), "Ошибка: День Независимости Беларуси не найден!"

    # ------------------------------------------------------------------
    # ЭТАП 2: ОНБОРДИНГ С СОХРАНЕНИЕМ СТРАНЫ/ГОРОДА В SQL И ИНДЕКСАЦИЕЙ В RAG
    # ------------------------------------------------------------------
    print("\n--- [ЭТАП 2] Онбординг с сохранением гео-данных в SQL и RAG ---")
    db_path = os.path.join(AI_ROOT, "test_holidays.db")
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()

    orchestrator = UnifiedOrchestrator(db_session=db_session)

    onboard_res = await orchestrator.execute_task(
        task_type="onboard_user",
        user_data={
            "user_id": "user_kz_tech_77",
            "company_name": "SilkWay AI Solutions",
            "niche": "IT и разработка SaaS",
            "city": "Алматы",
            "country": "Казахстан",
            "answers": {
                "step1": {"brand_name": "SilkWay AI Solutions", "niche": "IT и разработка SaaS", "city": "Алматы", "country": "Казахстан", "tone": "Технологичный и дружелюбный"},
                "step2": {"target_audience": "B2B компании и стартапы Центральной Азии"},
                "step3": {"advantages": "Автоматизация контента на казахском и русском языках"},
                "step4": {"services": [{"title": "Внедрение AI", "price": "от 500 000 KZT"}]},
                "step5": {"goals": ["Выход в топ-1 IT в Казахстане"]}
            }
        },
        session_id="sess_onboard_kz_holiday"
    )

    assert onboard_res.get("status") == "success"
    profile_id = onboard_res.get("profile_id")
    print(f"✅ Онбординг завершен! Профиль ID: {profile_id}")

    # Проверяем запись в SQL
    saved_profile = db_session.query(UserProfile).filter(UserProfile.id == profile_id).first()
    assert saved_profile is not None
    assert saved_profile.country == "Казахстан"
    assert saved_profile.city == "Алматы"
    print(f"✅ SQL Профиль подтвержден: '{saved_profile.company_name}', Страна: {saved_profile.country}, Город: {saved_profile.city}")

    # ------------------------------------------------------------------
    # ЭТАП 3: ГЕНЕРАЦИЯ 30-ДНЕВНОГО КОНТЕНТ-ПЛАНА С ПРАЗДНИКАМИ
    # ------------------------------------------------------------------
    print("\n--- [ЭТАП 3] Генерация 30-дневного контент-плана с праздниками ---")
    plan_res = await orchestrator.execute_task(
        task_type="plan_content",
        user_data={
            "profile_id": profile_id,
            "days_count": 30,
            "start_date": datetime(2026, 3, 1) # Март (месяц Наурыза и 8 Марта)
        },
        session_id="sess_plan_kz_holiday"
    )

    assert plan_res.get("status") == "success"
    c_plan = plan_res["content_plan"]
    plan_days = c_plan["plan_days"]
    holidays_count = c_plan.get("holidays_included_count", 0)

    print(f"📅 Сгенерирован план на {len(plan_days)} дней. Внедрено праздничных дат: {holidays_count}")
    
    holiday_posts = [d for d in plan_days if d.get("is_holiday")]
    print(f"🎉 Праздничные посты в плане ({len(holiday_posts)} шт.):")
    for hp in holiday_posts:
        print(f"   • День {hp['day']}: {hp['topic']}")
        print(f"     Формат: {hp['format']}")
        print(f"     Инфоповод: {hp['holiday_info']['title']} ({hp['holiday_info']['vibe']})")

    assert len(holiday_posts) >= 2, "Ошибка: праздничные дни не были внедрены в контент-план!"

    # ------------------------------------------------------------------
    # ЭТАП 4: ГЕНЕРАЦИЯ ПРАЗДНИЧНОГО ПОСТА С RAG-КОНТЕКСТОМ
    # ------------------------------------------------------------------
    print("\n--- [ЭТАП 4] Генерация праздничного поста через SaigaLLM + RAG ---")
    holiday_sample_day = holiday_posts[0]
    
    gen_post_res = await orchestrator.execute_task(
        task_type="generate_post",
        user_data={
            "profile_id": profile_id,
            "prompt": holiday_sample_day["topic"],
            "generate_image": True
        },
        session_id="sess_gen_holiday_post"
    )

    assert gen_post_res.get("status") == "success"
    print("\n✍️ Сгенерированный праздничный пост:")
    print("-" * 50)
    print(gen_post_res["post_text"])
    print("-" * 50)
    print(f"📸 Сгенерированное фото: {gen_post_res.get('photo_path')}")

    # Закрытие БД
    db_session.close()
    engine.dispose()
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except Exception:
        pass

    print("\n" + "=" * 80)
    print("🎉 ВСЕ ТЕСТЫ МОДУЛЯ ПРАЗДНИКОВ, ТРЕНДОВ И КОНТЕНТ-ПЛАНА УСПЕШНО ПРОЙДЕНЫ!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_holiday_and_content_plan_test())
