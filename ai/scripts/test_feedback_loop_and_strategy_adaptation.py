"""
test_feedback_loop_and_strategy_adaptation.py
======================================================================
Тестирование:
1. FeedbackLoopEngine: расчет ER, анализ тональности, извлечение FAQ и возражений.
2. Сохранение метрик публикации и комментариев в SQL (PublicationHistory).
3. Индексация обратной связи в Clean RAG Pipeline.
4. Автоматическая адаптация контент-плана под реальные вопросы и возражения.
5. Генерация поста, закрывающего конкретное возражение аудитории.
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
from storage.models import UserProfile, ProjectMetadata, PublicationHistory
from analytics.feedback_loop import FeedbackLoopEngine
from core.orchestrator import UnifiedOrchestrator


async def run_feedback_loop_test():
    print("=" * 80)
    print("🔄 ТЕСТ ТРЕКИНГА ПОСТОВ, АНАЛИЗА КОММЕНТАРИЕВ И АДАПТАЦИИ СТРАТЕГИИ")
    print("=" * 80)

    # ------------------------------------------------------------------
    # ЭТАП 1: ТЕСТИРОВАНИЕ АНАЛИЗАТОРА КОММЕНТАРИЕВ И ER
    # ------------------------------------------------------------------
    print("\n--- [ЭТАП 1] Анализ комментариев, тональности и возражений ---")
    engine_fl = FeedbackLoopEngine()

    sample_comments = [
        "Отличный сервис, делал полировку кузова, блестит просто огонь! 🔥",
        "А сколько стоит керамическое покрытие для кроссовера и даете ли вы официальную гарантию?",
        "Слишком дорого, у дяди Васи в гараже в 2 раза дешевле.",
        "Подскажите, а где вы находитесь в Санкт-Петербурге и работаете ли по выходным?",
        "Качественно, но запись пришлось ждать 3 дня. В остальном супер 👍"
    ]

    er = engine_fl.calculate_engagement_rate(views=1250, likes=84, comments=5, shares=12)
    analysis = engine_fl.analyze_comments(sample_comments)

    print(f"📊 Расчетный ER: {er}% (Просмотры: 1250, Лайки: 84, Комментарии: 5, Шеры: 12)")
    print(f"💬 Тональность: {analysis['sentiment']} {analysis['sentiment_breakdown']}")
    print(f"❓ Извлеченные вопросы клиентов ({len(analysis['top_questions'])} шт.):")
    for q in analysis["top_questions"]:
        print(f"   • {q}")
    print(f"🛡️ Выявленные возражения и барьеры ({len(analysis['top_objections'])} шт.):")
    for obj in analysis["top_objections"]:
        print(f"   • {obj}")

    assert er > 0
    assert len(analysis["top_questions"]) >= 2
    assert any("Высокая цена" in obj for obj in analysis["top_objections"])
    assert any("гарантии" in obj.lower() for obj in analysis["top_objections"])

    # ------------------------------------------------------------------
    # ЭТАП 2: СОХРАНЕНИЕ МЕТРИК В SQL И ИНДЕКСАЦИЯ В RAG ЧЕРЕЗ ОРКЕСТРАТОР
    # ------------------------------------------------------------------
    print("\n--- [ЭТАП 2] Сохранение метрик в SQL и синхронизация в RAG ---")
    db_path = os.path.join(AI_ROOT, "test_feedback_loop.db")
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    engine_db = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine_db)
    SessionLocal = sessionmaker(bind=engine_db)
    db_session = SessionLocal()

    # Создаем тестового пользователя и проект в SQL
    test_user = UserProfile(
        user_id="user_detailing_pro_99",
        company_name="Royal Detailing Club",
        niche="Детейлинг и защита кузова",
        city="Санкт-Петербург",
        country="Россия",
        step1={"brand_name": "Royal Detailing Club", "tone": "Премиальный и экспертный"},
        step2={"target_audience": "Владельцы премиальных авто"},
        step3={"advantages": "Немецкая химия, гарантия 3 года, чистая светлая студия"},
        step4={"services": [{"title": "Керамика 9H", "price": "от 45 000 руб."}]},
        step5={"goals": ["Привлечение премиум клиентов"]}
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    test_project = ProjectMetadata(
        user_profile_id=test_user.id,
        name="Royal Detailing Blog",
        niche="Детейлинг",
        platforms={"telegram": "@royaldetailing"}
    )
    db_session.add(test_project)
    db_session.commit()
    db_session.refresh(test_project)

    test_pub = PublicationHistory(
        project_id=test_project.id,
        platform="telegram",
        post_text="Новый фотоотчет по полировке Porsche 911 в нашей студии!",
        status="published"
    )
    db_session.add(test_pub)
    db_session.commit()
    db_session.refresh(test_pub)

    orchestrator = UnifiedOrchestrator(db_session=db_session)

    # Трекинг поста через задачу Orchestrator
    track_res = await orchestrator.execute_task(
        task_type="track_post_performance",
        user_data={
            "profile_id": test_user.id,
            "publication_id": test_pub.id,
            "company_name": test_user.company_name,
            "niche": test_user.niche,
            "views": 1500,
            "likes": 95,
            "shares": 14,
            "comments": sample_comments,
            "top_topics": [
                {"topic": "Кейс: полировка Porsche 911 До/После", "format": "Кейс До/После", "er": 10.4}
            ]
        },
        session_id="sess_track_metrics"
    )

    assert track_res.get("status") == "success"
    assert track_res.get("rag_indexed_count", 0) > 0
    print(f"✅ Трекинг завершен! ER: {track_res['engagement_rate']}%, RAG чанков создано: {track_res['rag_indexed_count']}")

    # Проверка обновления в SQL
    updated_pub = db_session.query(PublicationHistory).filter(PublicationHistory.id == test_pub.id).first()
    assert updated_pub.views_count == 1500
    assert updated_pub.engagement_rate > 0
    assert updated_pub.comments_analysis is not None
    print(f"✅ SQL PublicationHistory подтвержден: ER={updated_pub.engagement_rate}%, Views={updated_pub.views_count}")

    # ------------------------------------------------------------------
    # ЭТАП 3: ГЕНЕРАЦИЯ АДАПТИРОВАННОГО КОНТЕНТ-ПЛАНА
    # ------------------------------------------------------------------
    print("\n--- [ЭТАП 3] Генерация контент-плана, адаптированного под вопросы аудитории ---")
    plan_res = await orchestrator.execute_task(
        task_type="plan_content",
        user_data={
            "profile_id": test_user.id,
            "days_count": 7,
            "start_date": datetime(2026, 6, 1)
        },
        session_id="sess_plan_adapted"
    )

    assert plan_res.get("status") == "success"
    c_plan = plan_res["content_plan"]
    plan_days = c_plan["plan_days"]

    print(f"📅 Сгенерирован контент-план на {len(plan_days)} дней:")
    for d in plan_days:
        print(f"   • День {d['day']} [{d['stage']}]: {d['topic']}")
        print(f"     Фокус/Боль: {d['target_pain_point']}")
        print(f"     Формат: {d['format']}")

    # Проверяем, что в плане появились темы, закрывающие реальные вопросы и возражения
    qa_posts = [d for d in plan_days if "вопрос" in d["format"].lower() or "вопрос" in d["topic"].lower()]
    print(f"\n💡 Найдено постов-ответов на реальные вопросы аудитории: {len(qa_posts)} шт.")
    assert len(qa_posts) > 0, "Ошибка: посты-ответы на вопросы комментаторов не появились в плане!"

    # ------------------------------------------------------------------
    # ЭТАП 4: ГЕНЕРАЦИЯ ПОСТА НА БАЗЕ ИЗВЛЕЧЕННОГО ВОПРОСА
    # ------------------------------------------------------------------
    print("\n--- [ЭТАП 4] Генерация поста-ответа на реальный вопрос с RAG ---")
    adapted_topic = qa_posts[0]["topic"]
    
    post_res = await orchestrator.execute_task(
        task_type="generate_post",
        user_data={
            "profile_id": test_user.id,
            "prompt": adapted_topic,
            "generate_image": True
        },
        session_id="sess_generate_qa_post"
    )

    assert post_res.get("status") == "success"
    print("\n✍️ Сгенерированный адаптированный пост:")
    print("-" * 50)
    print(post_res["post_text"])
    print("-" * 50)
    print(f"📸 Сгенерированное фото: {post_res.get('photo_path')}")

    # Очистка
    db_session.close()
    engine_db.dispose()
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except Exception:
        pass

    print("\n" + "=" * 80)
    print("🎉 ВСЕ ТЕСТЫ FEEDBACK LOOP И АДАПТАЦИИ СТРАТЕГИИ УСПЕШНО ПРОЙДЕНЫ!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_feedback_loop_test())
