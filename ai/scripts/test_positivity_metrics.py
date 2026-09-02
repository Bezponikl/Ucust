"""
test_positivity_metrics.py
======================================================================
Тестирование математических формул позитивности и качества восприятия:
1. Индекс чистого одобрения (Net Approval Index - NAI):
   NAI = L / (L + D + 1)
2. Взвешенный расчет с просмотрами (Weighted Positivity Rate - WPR %):
   WPR = ((1.0 * L + 1.5 * R - 2.0 * D) / V) * 100
3. Логарифмический масштабированный балл (Logarithmic Positivity Score):
   Score = log10(V + 1) * ((1.0 * L + 1.5 * R + 1) / (1.0 * D + 1))
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import math
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from storage.db import Base
from storage.models import ProjectMetadata, UserProfile, PublicationHistory
from analytics.feedback_loop import FeedbackLoopEngine
from core.orchestrator import UnifiedOrchestrator


def test_mathematical_examples():
    print("=" * 80)
    print("📊 1. ТЕСТИРОВАНИЕ БАЗОВЫХ МАТЕМАТИЧЕСКИХ ПРИМЕРОВ ПОЛЬЗОВАТЕЛЯ")
    print("=" * 80)

    # Пример 1: Маленький пост (100 просмотров, 10 лайков, 0 дизлайков)
    m1 = FeedbackLoopEngine.calculate_positivity_metrics(views=100, likes=10, dislikes=0, comments=0, shares=0)
    print(f"\n1️⃣ Маленький пост (V=100, L=10, D=0):")
    print(f"   • NAI (Индекс одобрения): {m1['net_approval_index']} (Ожидается: ~0.9091)")
    print(f"   • WPR (Взвешенная позитивность): {m1['weighted_positivity_rate']}% (Ожидается: 10.0%)")
    print(f"   • Score (Логарифмический балл): {m1['log_positivity_score']} (Ожидается: ~22.05)")
    print(f"   • Грейд: {m1['grade']} ({m1['summary']})")
    assert 0.90 <= m1['net_approval_index'] <= 0.92
    assert 21.9 <= m1['log_positivity_score'] <= 22.2

    # Пример 2: Средний пост (10,000 просмотров, 800 лайков, 20 дизлайков)
    m2 = FeedbackLoopEngine.calculate_positivity_metrics(views=10000, likes=800, dislikes=20, comments=0, shares=0)
    print(f"\n2️⃣ Средний пост (V=10,000, L=800, D=20):")
    print(f"   • NAI: {m2['net_approval_index']} (Ожидается: ~0.9744)")
    print(f"   • WPR: {m2['weighted_positivity_rate']}% (Ожидается: ~7.6%)")
    print(f"   • Score: {m2['log_positivity_score']} (Ожидается: ~152.57)")
    print(f"   • Грейд: {m2['grade']} ({m2['summary']})")
    assert 0.97 <= m2['net_approval_index'] <= 0.98
    assert 152.0 <= m2['log_positivity_score'] <= 153.0

    # Пример 3: Вирусный, но спорный пост (100,000 просмотров, 2,000 лайков, 1,500 дизлайков)
    m3 = FeedbackLoopEngine.calculate_positivity_metrics(views=100000, likes=2000, dislikes=1500, comments=0, shares=0)
    print(f"\n3️⃣ Вирусный, но спорный пост (V=100,000, L=2,000, D=1,500):")
    print(f"   • NAI: {m3['net_approval_index']} (Ожидается: ~0.5713)")
    print(f"   • WPR: {m3['weighted_positivity_rate']}% (Ожидается: -1.0%)")
    print(f"   • Score: {m3['log_positivity_score']} (Ожидается: ~6.67)")
    print(f"   • Грейд: {m3['grade']} ({m3['summary']})")
    assert 0.56 <= m3['net_approval_index'] <= 0.58
    assert 6.5 <= m3['log_positivity_score'] <= 6.8

    # Пример 4: Вирусный хит с активными комментариями и репостами (100,000 просмотров, 8,000 лайков, 500 комментов, 200 репостов, 50 дизлайков)
    m4 = FeedbackLoopEngine.calculate_positivity_metrics(views=100000, likes=8000, dislikes=50, comments=500, shares=200)
    print(f"\n4️⃣ Вирусный хит (V=100,000, L=8,000, R=700, D=50):")
    print(f"   • NAI: {m4['net_approval_index']}")
    print(f"   • WPR: {m4['weighted_positivity_rate']}%")
    print(f"   • Score: {m4['log_positivity_score']}")
    print(f"   • Грейд: {m4['grade']} ({m4['summary']})")
    assert m4['grade'] == "VIRAL_POSITIVE"
    assert m4['log_positivity_score'] > 800

    print("\n✅ ВСЕ МАТЕМАТИЧЕСКИЕ РАСЧЕТЫ ТОЧНО СООТВЕТСТВУЮТ СПЕЦИФИКАЦИИ!")


async def test_orchestrator_feedback_loop_pipeline():
    print("\n" + "=" * 80)
    print("🔄 2. ТЕСТИРОВАНИЕ СКВОЗНОЙ ИНТЕГРАЦИИ В UNIFIED ORCHESTRATOR И RAG")
    print("=" * 80)

    test_engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(test_engine)
    TestSession = sessionmaker(bind=test_engine)
    db = TestSession()

    try:
        profile = UserProfile(
            user_id="user_positivity_test",
            company_name="Maksima Furniture",
            niche="Мебель",
            city="Ташкент"
        )
        db.add(profile)
        db.flush()

        project = ProjectMetadata(
            user_profile_id=profile.id,
            name="Maksima Main Campaign",
            niche="Дизайн мебели",
            platforms={"telegram": True, "vk": True}
        )
        db.add(project)
        db.flush()

        pub = PublicationHistory(
            project_id=project.id,
            platform="Telegram",
            post_text="Новая коллекция столов из массива дуба со скидкой 15% до конца недели!",
            status="PUBLISHED"
        )
        db.add(pub)
        db.commit()
        db.refresh(pub)

        orchestrator = UnifiedOrchestrator(db_session=db)

        payload = {
            "task_type": "track_post_performance",
            "publication_id": pub.id,
            "views": 25000,
            "likes": 1200,
            "dislikes": 15,
            "shares": 80,
            "company_name": "Maksima Furniture",
            "niche": "Мебель",
            "comments": [
                "Очень красивый стол! Какая гарантия на покрытие?",
                "А если доставка в Самарканд, сколько стоит?",
                "Цена вполне адекватная за массив, молодцы!",
                "Слишком дорого для нашего региона..."
            ],
            "top_topics": [
                {"topic": "Обзор стола из массива", "format": "Видео-обзор", "log_positivity_score": 185.4, "er": 5.2, "net_approval_index": 0.98},
                {"topic": "Сравнение дуба и ясеня", "format": "Карусель", "log_positivity_score": 92.1, "er": 3.8, "net_approval_index": 0.95}
            ]
        }

        res = await orchestrator.execute_task("track_post_performance", payload)
        assert res["status"] == "success"

        pos = res["positivity_metrics"]
        print(f"✅ Результаты обработки публикации #{pub.id}:")
        print(f"   • NAI (Индекс чистого одобрения): {pos['net_approval_index']}")
        print(f"   • WPR (Взвешенная позитивность): {pos['weighted_positivity_rate']}%")
        print(f"   • Score (Логарифмический балл): {pos['log_positivity_score']}")
        print(f"   • Грейд: {pos['grade']} ({pos['summary']})")
        print(f"   • Выявленные возражения: {res['comments_analysis']['top_objections']}")
        print(f"   • Вопросы аудитории: {res['comments_analysis']['top_questions']}")

        # Проверяем сохранение в SQL
        db.refresh(pub)
        assert pub.likes_count == 1200
        assert pub.dislikes_count == 15
        assert pub.net_approval_index == pos['net_approval_index']
        assert pub.log_positivity_score == pos['log_positivity_score']
        assert pub.positivity_grade == pos['grade']

        print(f"✅ Данные успешно зафиксированы в SQL БД (PublicationHistory ID #{pub.id})")
        print("\n🎉 ВСЕ ТЕСТЫ СКВОЗНОГО ПАЙПЛАЙНА УСПЕШНО ПРОЙДЕНЫ!")

    finally:
        db.close()


if __name__ == "__main__":
    test_mathematical_examples()
    asyncio.run(test_orchestrator_feedback_loop_pipeline())
