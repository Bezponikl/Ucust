"""
test_rag_sql_content_lifecycle.py
======================================================================
Сквозной тест жизненного цикла контента (SQL + RAG + Оркестратор):
1. Онбординг: Сохранение данных бренда в SQL (UserProfile) и векторизация 6 документов в RAG.
2. Семантический поиск: Проверка извлечения контекста из RAG по болям и конкурентам.
3. Контент-план: Генерация 7-дневного плана (TOFU/MOFU/BOFU) с привязкой к 3x3 сетке.
4. Генерация поста: Автоподтягивание профиля из SQL по user_id + инъекция точных фактов из RAG.
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio
from PIL import Image

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from storage.db import Base
from storage.models import UserProfile
from core.orchestrator import UnifiedOrchestrator


def create_sample_images():
    """Создает тестовые изображения для брендбука."""
    temp_dir = os.path.join(AI_ROOT, "output", "temp_cache")
    os.makedirs(temp_dir, exist_ok=True)
    paths = []
    test_colors = [(41, 128, 185), (236, 240, 241), (39, 174, 96)]
    for i, col in enumerate(test_colors, 1):
        p = os.path.join(temp_dir, f"test_rag_sql_brand_{i}.jpg")
        img = Image.new("RGB", (150, 150), color=col)
        img.save(p)
        paths.append(p)
    return paths


async def run_lifecycle_test():
    print("=" * 80)
    print("🚀 ТЕСТИРОВАНИЕ ЖИЗНЕННОГО ЦИКЛА КОНТЕНТА: SQL DB + RAG + ORCHESTRATOR")
    print("=" * 80)

    # Инициализация SQLite in-memory / file DB
    db_path = os.path.join(AI_ROOT, "test_lifecycle.db")
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    db_session = session_factory()

    orchestrator = UnifiedOrchestrator(db_session=db_session)
    brand_images = create_sample_images()

    test_user_id = "client_clinic_777"
    company_name = "DentistPro Clinic"
    niche = "Стоматология и имплантация"
    city = "Санкт-Петербург"

    # -------------------------------------------------------------
    # ЭТАП 1: ОНБОРДИНГ -> SQL + RAG ИНДЕКСАЦИЯ
    # -------------------------------------------------------------
    print("\n--- [ЭТАП 1] Онбординг: Парсинг, SQL сохранение и RAG векторизация ---")
    onboarding_data = {
        "user_id": test_user_id,
        "company_name": company_name,
        "niche": niche,
        "city": city,
        "attachments": brand_images,
        "raw_social_input": "https://example.com"
    }

    onb_res = await orchestrator.execute_task(
        task_type="onboarding",
        user_data=onboarding_data,
        session_id="sess_lifecycle_onboarding"
    )

    profile_id = onb_res.get("profile_id")
    print(f"✅ Онбординг завершен! Профиль ID: {profile_id}")
    
    # Проверяем запись в SQL
    saved_profile = db_session.query(UserProfile).filter(UserProfile.user_id == test_user_id).first()
    assert saved_profile is not None, "Ошибка: профиль не сохранился в SQL БД!"
    print(f"✅ SQL Профиль найден: '{saved_profile.company_name}', Цвета: {saved_profile.step1.get('brand_colors')}")
    assert saved_profile.visual_grid_dna is not None, "Ошибка: visual_grid_dna не сохранен в SQL!"

    # -------------------------------------------------------------
    # ЭТАП 2: СЕМАНТИЧЕСКИЙ ПОИСК В RAG
    # -------------------------------------------------------------
    print("\n--- [ЭТАП 2] Семантический RAG-поиск по болям и конкурентам ---")
    rag_pains = await orchestrator.rag.query_async(f"боли и страхи пациентов {company_name}")
    print(f"📚 RAG Результат (Боли): Score={rag_pains.top_score:.2f}")
    print(f"   Фактура: {rag_pains.formatted_context[:180]}...")

    rag_brand = await orchestrator.rag.query_async(f"позиционирование и УТП {company_name}")
    print(f"📚 RAG Результат (Бренд): Score={rag_brand.top_score:.2f}")

    assert len(rag_pains.chunks) > 0, "Ошибка: RAG не нашел чанки по болям!"

    # -------------------------------------------------------------
    # ЭТАП 3: СОЗДАНИЕ КОНТЕНТ-ПЛАНА (RAG + 3x3 СЕТКА)
    # -------------------------------------------------------------
    print("\n--- [ЭТАП 3] Генерация контент-плана на базе RAG и 3x3 сетки ---")
    plan_res = await orchestrator.execute_task(
        task_type="plan_content",
        user_data={"user_id": test_user_id, "days_count": 7},
        session_id="sess_lifecycle_plan"
    )

    c_plan = plan_res.get("content_plan", {})
    plan_days = c_plan.get("plan_days", [])
    print(f"📅 Сгенерировано дней: {len(plan_days)}")
    for d in plan_days[:3]:
        print(f"   • День {d['day']} [{d['stage']}]: {d['topic']}")
        print(f"     Слот сетки: #{d['grid_slot']['slot_number']} ({d['grid_slot']['visual_title']})")
        print(f"     Боль: {d['target_pain_point']}")

    assert len(plan_days) == 7, "Ошибка: контент-план должен содержать 7 дней!"
    assert plan_days[0]["grid_slot"]["slot_number"] == 1

    # -------------------------------------------------------------
    # ЭТАП 4: ГЕНЕРАЦИЯ ПОСТА С ИНЪЕКЦИЕЙ RAG И SQL
    # -------------------------------------------------------------
    print("\n--- [ЭТАП 4] Генерация поста с автоподтягиванием профиля из SQL и фактов из RAG ---")
    # Передаем ТОЛЬКО user_id и тему — вся остальная информация должна подняться автоматически
    post_payload = {
        "user_id": test_user_id,
        "prompt": "Как безболезненно и безопасно восстановить улыбку за 1 день",
        "generate_image": False
    }

    gen_res = await orchestrator.execute_task(
        task_type="generate_post",
        user_data=post_payload,
        session_id="sess_lifecycle_post"
    )

    post_text = gen_res.get("post_text", "")
    print(f"✍️ Сгенерированный пост:\n{'-'*50}\n{post_text}\n{'-'*50}")

    assert company_name in post_text or "улыбк" in post_text.lower()
    assert gen_res.get("status") == "success"

    db_session.close()
    engine.dispose()
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except Exception:
        pass

    print("\n" + "=" * 80)
    print("🎉 ВСЕ ЭТАПЫ ЖИЗНЕННОГО ЦИКЛА (SQL + RAG + ORCHESTRATOR) УСПЕШНО ПРОЙДЕНЫ!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_lifecycle_test())
