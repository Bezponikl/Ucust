"""
test_live_channel_posting.py
======================================================================
Универсальная CLI-команда для ручного тестирования генерации и автопостинга:
Принимает параметры бренда/темы и сразу публикует пост в тестовый Telegram-канал/группу.

Использование:
python ai/scripts/test_live_channel_posting.py --topic "Краффин с корицей" --company "Bakery Mood" --niche "Кондитерская" --channel "@your_test_channel"
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import argparse
import asyncio
from typing import Optional

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from skills.saiga_llm import SaigaLLMSkill
from skills.object_storytelling import ObjectKnowledgeStoryteller
from skills.competitor_hashtags import NicheCompetitorHashtagEngine
from skills.tech_sanitizer import TechSanitizer
from skills.zero_assumptions_guard import ZeroAssumptionsGuard
from publishers.telegram import TelegramPublisher


async def run_live_posting_test(
    topic: str,
    company_name: str = "Bakery Mood",
    niche: str = "Кондитерская и пекарня",
    city: str = "Москва",
    channel: Optional[str] = None,
    media_path: Optional[str] = None,
    format_type: str = "auto",
    bot_token: Optional[str] = None
):
    print("=" * 80)
    print("🚀 ЗАПУСК КОМАНДЫ ГЕНЕРАЦИИ И ТЕСТОВОГО АВТОПОСТИНГА")
    print(f"📌 Тема: {topic}")
    print(f"🏢 Бренд: {company_name} | Ниша: {niche} | Город: {city}")
    print(f"📢 Канал отправки: {channel or os.getenv('TELEGRAM_TARGET_CHANNEL', '@testaipublisher')}")
    print("=" * 80)

    # 1. Выбор и генерация контента
    topic_lower = topic.lower()
    if "миндал" in topic_lower or "ролл" in topic_lower:
        print("🥐 Использован формат: «Уравнение идеального вкуса»")
        res = ObjectKnowledgeStoryteller.generate_equation_formula_post(
            topic=topic,
            company_name=company_name,
            niche=niche,
            city=city
        )
        post_text = res["post_text"]
        hashtags = res["hashtags"]
        photo_prompt = res["visual_prompt"]
    elif "краффин" in topic_lower or "кориц" in topic_lower or "знали ли" in topic_lower:
        print("🥐 Использован формат: «Знали ли вы, что...»")
        res = ObjectKnowledgeStoryteller.generate_curated_did_you_know_post(
            topic=topic,
            company_name=company_name,
            niche=niche,
            city=city
        )
        post_text = res["post_text"]
        hashtags = res["hashtags"]
        photo_prompt = res["visual_prompt"]
    else:
        print("✍️ Использован генератор Сайга с маркетинговыми фреймворками")
        saiga = SaigaLLMSkill()
        res = saiga.generate_smm_post(
            topic=topic,
            company_name=company_name,
            niche=niche,
            city=city
        )
        post_text = res["post_text"]
        hashtags = res["hashtags"]
        photo_prompt = res["visual_prompt"]

    # 2. Фильтрация безопасности и анти-додумывания
    clean_text = TechSanitizer.sanitize_text(post_text)
    safe_text = ZeroAssumptionsGuard.sanitize_assumptions(clean_text)

    full_message = f"{safe_text}\n\n{hashtags}"

    print(f"\n📄 СФОРМИРОВАННЫЙ ПОСТ ДЛЯ ОТПРАВКИ:\n{'─' * 40}\n{full_message}\n{'─' * 40}")
    print(f"\n🎨 ПРОМПТ ДЛЯ ФОТО:\n{photo_prompt}\n")

    # 3. Публикация в тестовый канал
    target_channel = channel or os.getenv("TELEGRAM_TARGET_CHANNEL", "@testaipublisher")
    publisher = TelegramPublisher(target_channel=target_channel, bot_token=bot_token)

    print(f"📤 Отправка в канал {target_channel}...")
    try:
        success = await publisher.publish(text=full_message, media_path=media_path)
        if success:
            print(f"✅ Пост успешно сформирован и отправлен в {target_channel}!")
        else:
            print(f"\n❌ Не удалось отправить пост в Telegram. Возможные причины:")
            print(f"   1. Неверный токен бота (проверьте токен от @BotFather).")
            print(f"   2. Бот не добавлен в администраторы канала {target_channel}.")
            print(f"   3. У бота нет права на 'Публикацию сообщений' (Post Messages).")
    except Exception as e:
        print(f"⚠️ Ошибка при отправке в канал: {e}")

    return {
        "text": full_message,
        "photo_prompt": photo_prompt,
        "channel": target_channel
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UCust AI Live Channel Posting Tester")
    parser.add_argument("--topic", type=str, default="Идеальный ролл с миндалем и кремом Франжипан", help="Тема публикации")
    parser.add_argument("--company", type=str, default="Bakery Mood", help="Название компании")
    parser.add_argument("--niche", type=str, default="Кондитерская и пекарня", help="Ниша бизнеса")
    parser.add_argument("--city", type=str, default="Москва", help="Город")
    parser.add_argument("--channel", type=str, default=None, help="Целевой Telegram-канал (например @my_test_channel)")
    parser.add_argument("--bot-token", type=str, default=None, help="Telegram Bot Token (например 123456:ABC-DEF...)")
    parser.add_argument("--media", type=str, default=None, help="Путь к фото для прикрепления")

    args = parser.parse_args()
    asyncio.run(run_live_posting_test(
        topic=args.topic,
        company_name=args.company,
        niche=args.niche,
        city=args.city,
        channel=args.channel,
        media_path=args.media,
        bot_token=args.bot_token
    ))

