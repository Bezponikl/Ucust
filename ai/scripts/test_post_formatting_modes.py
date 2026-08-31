"""
test_post_formatting_modes.py
======================================================================
Тест двух режимов генерации и публикации постов в UCust AI:

1. Режим Showcase (@UcustAi / @testaipublisher / t.me/UcustAi):
   - Сообщение 1: Фото + Шапка «🚀 Старт проекта UCust AI: открытый вызов корпорациям» + Текст поста
   - Сообщение 2: Подпись «⏱️ Время генерации этого поста...» + Платформы + Хэштеги

2. Режим Клиента (Пользователь / Frontend):
   - Строго ТОЛЬКО фото и чистый текст поста без шапок, без хэштегов в тексте и без телеметрии!
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from publishers.achievement_broadcaster import AchievementBroadcaster
from core.orchestrator import UnifiedOrchestrator


async def test_formatting_modes():
    print("=" * 75)
    print("📢 ТЕСТИРОВАНИЕ РЕЖИМОВ ГЕНЕРАЦИИ И ПУБЛИКАЦИИ ПОСТОВ")
    print("=" * 75)

    broadcaster = AchievementBroadcaster(target_channel="@testaipublisher")
    orchestrator = UnifiedOrchestrator()

    # -------------------------------------------------------------
    # ТЕСТ 1: РЕЖИМ SHOWCASE (@UcustAi / @testaipublisher)
    # -------------------------------------------------------------
    print("\n" + "-" * 75)
    print("🚀 [ТЕСТ 1] РЕЖИМ ДЛЯ КАНАЛА @UcustAi / @testaipublisher (2 СООБЩЕНИЯ)")
    print("-" * 75)

    sample_post = (
        "С Днём Государственного флага Российской Федерации! 🇷🇺\n\n"
        "Белый, синий и красный — цвета чести, благородства, верности и силы. "
        "Они напоминают нам о богатой истории, сплочённости и уверенности в будущем.\n\n"
        "Пусть этот день вдохновляет на новые достижения и масштабные идеи!"
    )

    sample_timings = {
        "text_gen_seconds": 0.0,
        "photo_gen_seconds": 196.93,
        "total_seconds": 198.31
    }

    sample_hashtags = "#ДеньФлага #Россия #триколор #праздник #UCust"

    # Форматируем 1-е и 2-е сообщения
    msg1 = broadcaster.format_showcase_message_1(sample_post, category="Обновление")
    msg2 = broadcaster.format_showcase_message_2(timings=sample_timings, hashtags=sample_hashtags)

    print("📄 [СООБЩЕНИЕ 1 (Фото + Шапка + Текст)]:\n")
    print(msg1)
    print("\n" + "~" * 60)
    print("📄 [СООБЩЕНИЕ 2 (Телеметрия + Платформы + Хэштеги)]:\n")
    print(msg2)

    # Проверки сообщения 1
    assert "🚀 <b>Старт проекта UCust AI: открытый вызов корпорациям</b>" in msg1
    assert "#Обновление" in msg1
    assert "С Днём Государственного флага" in msg1

    # Проверки сообщения 2
    assert "⏱️ <b>Время генерации этого поста:</b>" in msg2
    assert "• Текст + аудит качества: 0.0 сек" in msg2
    assert "• Фото-креатив: 196.93 сек" in msg2
    assert "• Итого: 198.31 сек" in msg2
    assert "TG" in msg2 and "MAX" in msg2 and "VK" in msg2 and "OK" in msg2
    assert "Режим работы: 24/7 автономно" in msg2
    assert "#ДеньФлага #Россия #триколор #праздник #UCust" in msg2

    print("\n✅ [ТЕСТ 1 ПРОЙДЕН]: Структура 2-х сообщений для @UcustAi сформирована строго по ТЗ!")

    # -------------------------------------------------------------
    # ТЕСТ 2: РЕЖИМ КЛИЕНТА (ЧИСТЫЙ ТЕКСТ ПОСТА + ФОТО ДЛЯ ЮЗЕРА)
    # -------------------------------------------------------------
    print("\n" + "-" * 75)
    print("👤 [ТЕСТ 2] РЕЖИМ ГЕНЕРАЦИИ ДЛЯ КЛИЕНТА / ПОЛЬЗОВАТЕЛЯ")
    print("-" * 75)

    client_request = {
        "user_id": "usr_client_beauty_12",
        "company_name": "Crocus Beauty",
        "niche": "Салон красоты",
        "topic": "Комплексный уход за внешностью и летний сезонный маникюр",
        "generate_image": True,
        "format": "post"
    }

    post_res = await orchestrator.execute_task(
        task_type="generate_post",
        user_data=client_request,
        session_id="sess_client_test_clean"
    )

    clean_text = post_res.get("post_text", "")
    print(f"📄 [ЧИСТЫЙ ТЕКСТ ДЛЯ КЛИЕНТА]:\n{clean_text}\n")
    print(f"🖼️ [ПРИКРЕПЛЕННОЕ ФОТО]: {post_res.get('image_url')}")
    print(f"🏷️ [ОТДЕЛЬНЫЕ МЕТА-ХЭШТЕГИ]: {post_res.get('hashtags')}")

    # Проверки чистоты текста для клиента
    assert "Старт проекта UCust AI" not in clean_text, "Ошибка: корпоративная шапка попала в пост клиента!"
    assert "Время генерации этого поста" not in clean_text, "Ошибка: телеметрия времени попала в пост клиента!"
    assert "24/7 автономно" not in clean_text, "Ошибка: технические подписи попали в пост клиента!"
    assert not any(line.strip().startswith("#") for line in clean_text.splitlines()), "Ошибка: хэштеги в теле поста клиента!"

    print("\n✅ [ТЕСТ 2 ПРОЙДЕН]: Текст для пользователя очищен от всех служебных шапок, подписей и хэштегов!")

    print("\n" + "=" * 75)
    print("🎉 ВСЕ ПРОВЕРКИ РЕЖИМОВ ОТОБРАЖЕНИЯ И ПУБЛИКАЦИИ УСПЕШНО ПРОЙДЕНЫ!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(test_formatting_modes())
