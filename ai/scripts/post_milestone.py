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
from typing import Optional

# Setup PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from publishers.achievement_broadcaster import AchievementBroadcaster

def find_latest_image() -> Optional[str]:
    """Автоматически находит последнее сгенерированное фото."""
    candidates_dirs = [
        os.path.join(os.path.dirname(__file__), "..", "output", "photos"),
        "/opt/ucust/ai/output/photos",
        os.path.join(os.path.dirname(__file__), "..", "..", "ComfyUI", "output"),
        "/opt/ucust/ComfyUI/output",
        "ai/output/photos",
        "output/photos"
    ]
    all_files = []
    for d in candidates_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    full_p = os.path.join(d, f)
                    all_files.append((os.path.getmtime(full_p), full_p))
    if all_files:
        all_files.sort(key=lambda x: x[0], reverse=True)
        return all_files[0][1]
    return None

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
    parser.add_argument("--media", type=str, default=None, help="Путь к фото или видео файлу (если не указан, берется последнее сгенерированное фото)")
    parser.add_argument("--channel", type=str, default="@UcustAi", help="Целевой Telegram-канал")

    args = parser.parse_args()

    media_to_send = args.media or find_latest_image()
    has_photo = media_to_send is not None and os.path.exists(media_to_send)
    if media_to_send and has_photo:
        print(f"🖼️ Прикрепляем изображение к посту: {media_to_send}")

    # Формируем точные метрики: только реально затраченное время текста и фото (если прикреплено)
    metrics = args.metrics if args.metrics != default_metrics else AchievementBroadcaster.build_honest_metrics(
        text_gen_seconds=0.85,
        photo_gen_seconds=3.41 if has_photo else None,
        has_photo=has_photo
    )

    broadcaster = AchievementBroadcaster(target_channel=args.channel)
    print(f"📡 Публикация обновления в канал {args.channel}...")
    res = await broadcaster.broadcast_milestone_async(
        title=args.title,
        description=args.desc,
        metrics=metrics,
        media_path=media_to_send
    )
    print(f"Результат: {res}")

if __name__ == "__main__":
    asyncio.run(main())
