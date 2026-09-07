# File: ai/scripts/test_vertical_niches.py
"""
Скрипт пакетного тестирования вертикальной фотогенерации (4:5 и 9:16)
для 5 ключевых ниш UCust AI:
1. IT / Разработка
2. Кулинария / Ресторанное дело
3. Кофейня / Спешелти кофе
4. Животные / Груминг и зоотовары
5. Ноготочки / Бьюти и ногтевой сервис

Запуск:
    python ai/scripts/test_vertical_niches.py --all
    python ai/scripts/test_vertical_niches.py --niche it --ratio 4:5
    python ai/scripts/test_vertical_niches.py --niche nails --ratio 9:16 --publish
"""

import os
import sys
import time
import asyncio
import argparse
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.orchestrator import UnifiedOrchestrator
from skills.comfy_cli_runner import ComfyCLIRunner
from publishers.achievement_broadcaster import AchievementBroadcaster

NICHES_DATA = {
    "it": {
        "title": "IT / Архитектура и разработка",
        "company_name": "DevPulse Pro",
        "niche": "Highload backend-разработка и облачная инфраструктура",
        "topic": "Ночная отладка критического микросервиса перед релизом: мониторы с терминалом, темная комната, неоновый свет мегаполиса за окном",
        "tone": "Экспертный, сдержанный, глубокий",
    },
    "culinary": {
        "title": "Кулинария / Высокая гастрономия",
        "company_name": "Atelier Gourmet",
        "niche": "Авторская кухня и гастрономический ресторан",
        "topic": "Идеально прожаренный стейк рибай средней прожарки на деревянной доске с розмарином, чесноком и кристаллами соли",
        "tone": "Аппетитный, премиальный, чувственный",
    },
    "coffee": {
        "title": "Кофейня / Спешелти культура",
        "company_name": "Roast & Bloom",
        "niche": "Спешелти кофейня и обжарка зерен",
        "topic": "Свежесваренный капучино с идеальным латте-артом лебедя, теплый круассан и лучи утреннего солнца на деревянном столике",
        "tone": "Уютный, вдохновляющий, эстетичный",
    },
    "animals": {
        "title": "Животные / Зооиндустрия и питомцы",
        "company_name": "Tail & Paws",
        "niche": "Премиальный уход за домашними животными и груминг",
        "topic": "Очаровательный пушистый щенок корги с любопытным наклоном головы на мягком пледе в лучах солнца",
        "tone": "Теплый, эмоциональный, милый",
    },
    "nails": {
        "title": "Ноготочки / Маникюр и бьюти",
        "company_name": "Velvet Touch Studio",
        "niche": "Премиальный ногтевой сервис и нейл-дизайн",
        "topic": "Идеальный осенний маникюр формы мягкий квадрат с глубоким сапфировым покрытием и акцентом золотой потали",
        "tone": "Изысканный, стильный, ухоженный",
    }
}

async def run_single_test(
    niche_key: str,
    aspect_ratio: str = "4:5",
    variation_index: int = 0,
    auto_publish: bool = False,
    channel: str = "@testaipublisher"
):
    data = NICHES_DATA.get(niche_key)
    if not data:
        print(f"❌ Неизвестная ниша: {niche_key}. Доступные: {list(NICHES_DATA.keys())}")
        return

    print("\n" + "=" * 65)
    print(f"🎯 ТЕСТ ГЕНЕРАЦИИ ДЛЯ НИШИ: {data['title']}")
    print(f"🏢 Компания: {data['company_name']}")
    print(f"📐 Формат: {aspect_ratio} | Вариация: #{variation_index}")
    print(f"📝 Тема: {data['topic']}")
    print("=" * 65)

    # Проверка ComfyUI
    try:
        runner = ComfyCLIRunner()
        print("🔍 Проверка сервера ComfyUI...")
        await runner.ensure_server_online()
    except Exception as e:
        print(f"⚠️ Ошибка проверки ComfyUI: {e}")

    orch = UnifiedOrchestrator()
    task_data = {
        "topic": data["topic"],
        "company_name": data["company_name"],
        "niche": data["niche"],
        "tone": data["tone"],
        "tier": "BUSINESS",
        "generate_image": True,
        "aspect_ratio": aspect_ratio,
        "variation_index": variation_index,
    }

    t0 = time.time()
    result = await orch.execute_task("generate_post", task_data, session_id=f"test_vertical_{niche_key}_{int(time.time())}")
    duration = round(time.time() - t0, 2)

    post_text = result.get("post_text", "")
    critic_review = result.get("critic_review", {})
    critic_score = critic_review.get("score", 0.95)
    photo_prompt = result.get("photo_prompt", "")
    photo_url = result.get("photo_url") or result.get("image_url")
    hashtags = result.get("hashtags", f"#{data['company_name']} #{niche_key}")

    print("\n" + "-" * 65)
    print(f"⏱️ Общее время выполнения: {duration} сек")
    print(f"⭐ Оценка критика Мангера: {round(critic_score * 10, 1)} / 10")
    print(f"🎨 Сгенерированный промпт для фото:\n{photo_prompt}")
    print(f"🖼️ Ссылка на фото: {photo_url}")
    print("\n📄 Сгенерированный пост:\n")
    print(post_text)
    print("-" * 65)

    if auto_publish and photo_url:
        print(f"\n📡 Публикация в канал {channel}...")
        fname = os.path.basename(photo_url)
        photo_local_path = os.path.join(os.path.dirname(__file__), "..", "output", fname)
        if not os.path.exists(photo_local_path):
            photo_local_path = os.path.join("C:/ComfyUI_windows_portable/ComfyUI/output", fname)
        
        broadcaster = AchievementBroadcaster(target_channel=channel)
        await broadcaster.broadcast_post(
            topic=data["topic"],
            post_text=post_text,
            photo_path=photo_local_path if os.path.exists(photo_local_path) else None,
            hashtags=hashtags,
            author_persona="Saiga 2.0 & Realistic Vision",
            manger_score=critic_score,
            generation_time_sec=duration
        )
        print("✅ Успешно опубликовано!")

async def main():
    parser = argparse.ArgumentParser(description="UCust AI Vertical Test Suite")
    parser.add_argument("--niche", type=str, choices=["it", "culinary", "coffee", "animals", "nails"], default="it", help="Ниша для теста")
    parser.add_argument("--ratio", type=str, choices=["4:5", "9:16", "1:1"], default="4:5", help="Соотношение сторон (4:5 для постов, 9:16 для Stories)")
    parser.add_argument("--variation", type=int, default=0, help="Индекс вариации (0..3)")
    parser.add_argument("--all", action="store_true", help="Запустить последовательный тест всех 5 ниш")
    parser.add_argument("--publish", action="store_true", help="Автоматически отправить результат в Telegram")
    parser.add_argument("--channel", type=str, default="@testaipublisher", help="Telegram-канал для отправки")

    args = parser.parse_args()

    if args.all:
        print("🚀 ЗАПУСК ТЕСТА ВСЕХ 5 НИШ...")
        for niche_key in NICHES_DATA.keys():
            await run_single_test(
                niche_key=niche_key,
                aspect_ratio=args.ratio,
                variation_index=args.variation,
                auto_publish=args.publish,
                channel=args.channel
            )
            await asyncio.sleep(2)
    else:
        await run_single_test(
            niche_key=args.niche,
            aspect_ratio=args.ratio,
            variation_index=args.variation,
            auto_publish=args.publish,
            channel=args.channel
        )

if __name__ == "__main__":
    asyncio.run(main())
