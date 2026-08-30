# File: scripts/post_milestone.py
"""
CLI Tool to broadcast milestones and achievements to Telegram Channel @UcustAi.
Usage:
  python ai/scripts/post_milestone.py --title "Успешный запуск 2.0" --desc "Запущена автономная мульти-агентная сеть"
"""

import sys
import os
import argparse
import asyncio

# Setup PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from publishers.achievement_broadcaster import AchievementBroadcaster

async def main():
    default_metrics = AchievementBroadcaster.build_honest_metrics(
        text_gen_seconds=2.11,
        photo_gen_seconds=None,
        video_gen_seconds=None
    )
    
    parser = argparse.ArgumentParser(description="Broadcast milestones to @UcustAi")
    parser.add_argument("--title", type=str, default="Старт проекта UCust AI: открытый вызов корпорациям", help="Заголовок достижения")
    parser.add_argument("--desc", type=str, default="Пока неповоротливые агентства согласовывают брифы неделями — автономная связка ИИ-агентов UCust закрывает полный цикл маркетинга и генерации контента в разы быстрее раздутых отделов крупных компаний.", help="Описание достижения")
    parser.add_argument("--metrics", nargs="*", default=default_metrics, help="Список метрик")
    parser.add_argument("--media", type=str, default=None, help="Путь к фото или видео файлу")
    parser.add_argument("--channel", type=str, default="@UcustAi", help="Целевой Telegram-канал")

    args = parser.parse_args()

    broadcaster = AchievementBroadcaster(target_channel=args.channel)
    print(f"📡 Публикация достижения в канал {args.channel}...")
    res = await broadcaster.broadcast_milestone_async(
        title=args.title,
        description=args.desc,
        metrics=args.metrics,
        media_path=args.media
    )
    print(f"Результат: {res}")

if __name__ == "__main__":
    asyncio.run(main())
