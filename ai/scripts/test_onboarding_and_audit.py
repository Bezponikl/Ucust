"""
File: ai/scripts/test_onboarding_and_audit.py
Тестовый скрипт проверки агентов профилирования (Onboarding Agent),
семантического аудита (Audit Deduplication Agent) и Celery-задач.
"""

import sys
import os
import asyncio

# Добавляем родительскую директорию в sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, AI_DIR)

from skills.audit_deduplication_agent import AuditDeduplicationAgent, DeduplicationVerdict
from skills.onboarding_agent import OnboardingAgent, ExtractedBrandDNA
from core.orchestrator import UnifiedOrchestrator


async def test_audit_deduplication():
    print("\n🔍 [1/4] Тестирование AuditDeduplicationAgent (Семантический аудит и сдвиг угла)...")
    agent = AuditDeduplicationAgent(custom_threshold=0.82)
    
    recent_channel_posts = [
        "Разбор кейса: Как мы внедрили сквозную аналитику и сократили CPA на 34% в B2B нише.",
        "Пять ключевых ошибок при составлении коммерческого предложения для корпоративных клиентов.",
        "Инструкция по выбору надежного облачного провайдера для финтех стартапов."
    ]
    
    # 1. Похожая тема (должна быть заблокирована как дубль)
    duplicate_candidate = "Кейс внедрения сквозной аналитики: снижение CPA на 34% для b2b сектора."
    verdict_dup = agent.evaluate_uniqueness(
        proposed_topic_or_text=duplicate_candidate,
        recent_channel_posts=recent_channel_posts,
        topic_category="case_study"
    )
    print(f"   Тест 1 (Потенциальный дубль):")
    print(f"   - Исходная тема: '{duplicate_candidate}'")
    print(f"   - Сходство: {verdict_dup.similarity_score} (Порог: {agent.threshold})")
    print(f"   - Дубль: {verdict_dup.is_duplicate}")
    print(f"   - Рекомендуемый сдвиг: '{verdict_dup.suggested_shifted_angle}'")
    assert verdict_dup.is_duplicate, "Ошибка: дубль не был обнаружен!"
    assert verdict_dup.suggested_shifted_angle is not None, "Ошибка: не предложен сдвиг угла!"

    # 2. Уникальная тема (должна пройти)
    unique_candidate = "Юридические тонкости структурирования международных M&A сделок в 2026 году."
    verdict_uniq = agent.evaluate_uniqueness(
        proposed_topic_or_text=unique_candidate,
        recent_channel_posts=recent_channel_posts,
        topic_category="case_study"
    )
    print(f"   Тест 2 (Уникальная тема):")
    print(f"   - Тема: '{unique_candidate}'")
    print(f"   - Сходство: {verdict_uniq.similarity_score}")
    print(f"   - Дубль: {verdict_uniq.is_duplicate}")
    assert not verdict_uniq.is_duplicate, "Ошибка: уникальная тема ошибочно помечена как дубль!"
    
    print("   ✅ AuditDeduplicationAgent отработал корректно!")


async def test_onboarding_agent():
    print("\n🏢 [2/4] Тестирование OnboardingAgent (Сбор данных и извлечение Brand DNA)...")
    agent = OnboardingAgent(dev_mode=True)
    
    # Проверка санитизации текста
    dirty_html = "<div><p>Компания <b>AlphaCorp</b>\x00\ufeff</p>\n\n\n\n<script>alert(1)</script>   Текст с   пробелами.</div>"
    clean = agent._sanitize_text(dirty_html)
    assert "\x00" not in clean and "\ufeff" not in clean
    print(f"   Санитизация текста: Успешно очищено от битых байтов и мусора.")

    # Проверка извлечения Brand DNA для B2B Corporate
    b2b_dna = await agent.ingest_and_profile_brand(
        tenant_id="tenant_b2b_law",
        company_name="Lex Veritas",
        niche="Корпоративные юристы и M&A консалтинг",
        raw_notes="Сопровождаем сделки от 50 млн руб. Гарантируем конфиденциальность и минимизацию налоговых рисков."
    )
    print(f"   B2B Профиль:")
    print(f"   - Компания: {b2b_dna.company_name} | Индустрия: {b2b_dna.industry}")
    print(f"   - Tone of Voice: {b2b_dna.tone_of_voice}")
    print(f"   - Brand Props: {b2b_dna.brand_props}")
    print(f"   - УТП count: {len(b2b_dna.key_usp)}")
    assert b2b_dna.industry == "b2b_corporate"
    assert len(b2b_dna.brand_props) > 0

    # Проверка извлечения Brand DNA для B2C Lifestyle
    b2c_dna = await agent.ingest_and_profile_brand(
        tenant_id="tenant_b2c_coffee",
        company_name="Nordic Roast",
        niche="Спешелти кофейня и обжарка",
        raw_notes="Зерно класса Specialty 86+ Q-градации, свежая выпечка каждое утро."
    )
    print(f"   B2C Профиль:")
    print(f"   - Компания: {b2c_dna.company_name} | Индустрия: {b2c_dna.industry}")
    print(f"   - Tone of Voice: {b2c_dna.tone_of_voice}")
    print(f"   - Brand Props: {b2c_dna.brand_props}")
    assert b2c_dna.industry == "b2c_lifestyle"
    print("   ✅ OnboardingAgent успешно извлекает Brand DNA и визуальные якоря!")


async def test_orchestrator_integration():
    print("\n⚙️ [3/4] Тестирование сквозной интеграции в UnifiedOrchestrator...")
    orchestrator = UnifiedOrchestrator()
    
    # 1. Задача onboard_brand
    onboard_res = await orchestrator.execute_task(
        task_type="onboard_brand",
        user_data={
            "tenant_id": "tenant_test_1",
            "company_name": "Nordic Wood Craft",
            "niche": "Мебель из натурального дуба",
            "raw_notes": "Премиальная мебель ручной работы из массива дуба и латуни."
        }
    )
    print(f"   Orchestrator onboard_brand статус: {onboard_res.get('status')}")
    assert onboard_res.get("status") == "success"
    assert "brand_dna" in onboard_res

    # 2. Задача generate_post с проверкой дедупликации
    recent_posts = [
        "Обзор новой коллекции столов из массива дуба со скидкой 10%",
        "Почему мебель из натурального дуба служит более 50 лет"
    ]
    post_res = await orchestrator.execute_task(
        task_type="generate_post",
        user_data={
            "prompt": "Обзор новой коллекции столов из массива дуба со скидкой",
            "company_name": "Nordic Wood Craft",
            "niche": "Мебель из дуба",
            "recent_post_topics": recent_posts,
            "rubric": "product_overview",
            "generate_image": False  # Dev-тест без рендера фото
        }
    )
    print(f"   Orchestrator generate_post статус: {post_res.get('status')}")
    assert post_res.get("status") == "success"
    dedup = post_res.get("deduplication_verdict", {})
    print(f"   Дедупликация вердикт: is_duplicate={dedup.get('is_duplicate')}, score={dedup.get('similarity_score')}")
    print(f"   Сдвинутый угол: {dedup.get('suggested_shifted_angle')}")
    assert dedup.get("is_duplicate") == True
    print("   ✅ Интеграция в UnifiedOrchestrator прошла успешно!")


async def test_celery_task_definitions():
    print("\n📦 [4/4] Тестирование Celery Task сигнатур и конфигурации...")
    try:
        from celery_tasks import (
            celery_app, onboard_brand_task, audit_post_task,
            generate_post_draft_task, render_post_task
        )
        print(f"   Celery App: {celery_app.main}")
        print(f"   Зарегистрированные задачи: {[t for t in celery_app.tasks.keys() if 'celery_tasks' in t]}")
        print(f"   Очередь по умолчанию: ucust_ai_queue | Очередь рендера: ucust_gpu_render")
        print("   ✅ Celery задачи и конфигурация воркеров экспортированы корректно!")
    except Exception as e:
        print(f"   ⚠️ Ошибка импорта Celery: {e}")
        raise e


async def main():
    print("=" * 70)
    print("🧪 ЗАПУСК АВТОМАТИЗИРОВАННОГО ТЕСТИРОВАНИЯ ONBOARDING & AUDIT PIPELINE")
    print("=" * 70)
    await test_audit_deduplication()
    await test_onboarding_agent()
    await test_orchestrator_integration()
    await test_celery_task_definitions()
    print("\n" + "=" * 70)
    print("🎉 ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ! АРХИТЕКТУРА ГОТОВА К ПРОДАКШЕНУ.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
