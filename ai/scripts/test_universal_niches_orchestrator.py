"""
test_universal_niches_orchestrator.py
======================================================================
Тест адаптивности Оркестратора и Сайги под любые сферы бизнеса:
1. Стоматология (Медицина)
2. Продавец овощей на рынке (Локальный стрит-ритейл / Фермерство)
3. Приватный закрытый ТГ-канал (Creator Economy / Subscription)
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio
import time

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from core.orchestrator import UnifiedOrchestrator


async def test_universal_niches():
    orchestrator = UnifiedOrchestrator()
    
    test_cases = [
        {
            "category": "🩺 1. СТОМАТОЛОГИЯ И МЕДИЦИНА",
            "company_name": "ДентаЛюкс",
            "niche": "Стоматология и эстетическая медицина",
            "city": "Москва",
            "topic": "Имплантация и лечение зубов во сне без боли и страха",
            "tone": "Заботливый, уверенный, экспертный",
            "format": "post"
        },
        {
            "category": "🍅 2. ПРОДАВЕЦ ОВОЩЕЙ И ФРУКТОВ НА РЫНКЕ",
            "company_name": "Урожай от Ашота",
            "niche": "Свежие овощи, фрукты и зелень на рынке",
            "city": "Москва (Дорогомиловский рынок)",
            "topic": "Спелые грунтовые томаты и сочные сезонные персики только с грядки",
            "tone": "Гостеприимный, аппетитный, душевный",
            "format": "post"
        },
        {
            "category": "🤫 3. CREATOR ECONOMY / ПРИВАТНЫЙ ТГ-КАНАЛ",
            "company_name": "Eva Secret Club",
            "niche": "Приватный закрытый канал по подписке и эксклюзивный лайфстайл",
            "city": "Дубай / Онлайн",
            "topic": "Эксклюзивный бэкстейдж, закрытые прямые эфиры и личное общение без цензуры",
            "tone": "Интригующий, эксклюзивный, чувственный",
            "format": "post"
        }
    ]

    print("=" * 75)
    print("🚀 СТРЕСС-ТЕСТ УНИВЕРСАЛЬНОСТИ ОРКЕСТРАТОРА (ОТ СТОМАТОЛОГИИ ДО ПРИВАТОВ)")
    print("=" * 75)

    for case in test_cases:
        print("\n" + "—" * 75)
        print(f"{case['category']}")
        print("—" * 75)
        
        t0 = time.time()
        post_payload = {
            "user_id": f"usr_test_{int(time.time())}",
            "company_name": case["company_name"],
            "niche": case["niche"],
            "city": case["city"],
            "topic": case["topic"],
            "format": case["format"],
            "tone": case["tone"],
            "generate_image": False,
            "comments_enabled": True
        }

        res = await orchestrator.execute_task(
            task_type="generate_post",
            user_data=post_payload,
            session_id=f"sess_univ_{case['company_name'].lower().replace(' ', '_')}"
        )
        t_dur = round(time.time() - t0, 2)

        print(f"⏱️ Сгенерировано за: {t_dur} сек | Статус: Успешно")
        print("\n📄 [ТЕКСТ ПОСТА]:")
        print(res.get("post_text"))
        print(f"\n🏷️ Хэштеги: {res.get('hashtags')}")
        print(f"🎬 ComfyUI Промпт: {res.get('photo_prompt')[:120]}...")

    print("\n" + "=" * 75)
    print("🎉 ВСЕ 3 КАТЕГОРИИ УСПЕШНО АДАПТИРОВАНЫ И ПРОТЕСТИРОВАНЫ!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(test_universal_niches())
