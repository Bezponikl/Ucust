# File: scripts/run_autonomous_campaign.py
"""
Полный сквозной запуск автономного пайплайна UCust AI:
1. Агент Сайга генерирует продающий пост по теме/промпту
2. Агент-Критик (Чарли Мангер) проводит аудит и полировку качества
3. Замеряются реальные тайминги генерации
4. Результат автоматически отправляется в Telegram-канал @UcustAi
"""

import os
import sys
import time
import asyncio
import argparse
from typing import Optional, Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.orchestrator import UnifiedOrchestrator
from publishers.achievement_broadcaster import AchievementBroadcaster

async def run_pipeline(
    topic: str,
    company_name: str = "UCust",
    niche: str = "Автономный AI-маркетинг и мульти-агентные системы",
    tone: str = "Дерзкий, уверенный, вдохновляющий",
    channel: str = "@testaipublisher",
    auto_publish: bool = True,
    stage: Optional[str] = None,
    framework: Optional[str] = None,
    trigger: Optional[str] = None,
    tier: str = "BUSINESS",
    aspect_ratio: str = "1:1",
    variation_index: int = 0,
    images: Optional[List[str]] = None
):
    print("=" * 60)
    print("🚀 ЗАПУСК СКВОЗНОГО АВТОНОМНОГО ПАЙПЛАЙНА UCUST AI")
    print(f"📌 Тема / Промпт: {topic}")
    print(f"🏢 Компания: {company_name} | Ниша: {niche}")
    print(f"🎯 Тональность: {tone} | Формат фото: {aspect_ratio} | Вариация: #{variation_index}")
    if images:
        print(f"📎 Прикрепленные файлы/фото: {', '.join(images)} ({len(images)} шт.)")
    print(f"💼 Тариф: {tier} | Ступень воронки: {stage or 'Auto (Ступень 2 / Проблема)'} | Фреймворк: {framework or 'Auto'}")
    print("=" * 60)

    start_total = time.time()

    # Подготавливаем вложения (локальные файлы или URL)
    attachments = []
    if images:
        for img in images:
            if os.path.exists(img):
                attachments.append({"url": img, "local_path": os.path.abspath(img)})
            else:
                attachments.append({"url": img})

    # 1. Запуск Оркестратора (Сайга + Воронка Ханта + Критик Мангер + Валидация)
    orch = UnifiedOrchestrator()
    task_data = {
        "topic": topic,
        "company_name": company_name,
        "niche": niche,
        "tone": tone,
        "hunt_stage": stage,
        "framework": framework,
        "trigger": trigger,
        "tier": tier,
        "generate_image": True,
        "aspect_ratio": aspect_ratio,
        "variation_index": variation_index,
        "attachments": attachments if attachments else None
    }

    t0 = time.time()
    result = await orch.execute_task("generate_post", task_data, session_id=f"auto_run_{int(time.time())}")
    gen_duration = round(time.time() - t0, 2)

    post_text = result.get("post_text", "")
    critic_review = result.get("critic_review", {})
    critic_score = critic_review.get("score", 0.95)
    photo_prompt = result.get("photo_prompt", "")
    photo_url = result.get("photo_url") or result.get("image_url")
    post_hashtags = result.get("hashtags", "#UCust #ИИмаркетинг")

    # Получаем локальный путь к созданному фото
    photo_local_path = None
    if photo_url:
        fname = os.path.basename(photo_url)
        cand_path = os.path.join(os.path.dirname(__file__), "..", "output", "photos", fname)
        if os.path.exists(cand_path):
            photo_local_path = cand_path

    timings = result.get("timings", {})
    text_sec = timings.get("text_gen_seconds")
    photo_sec = timings.get("photo_gen_seconds")

    total_duration = round(time.time() - start_total, 2)

    print("\n" + "=" * 60)
    print(f"⏱️ РЕАЛЬНЫЕ ЗАМЕРЫ ВРЕМЕНИ ГЕНЕРАЦИИ:")
    if text_sec is not None:
        print(f" • Генерация текста + Pre-Mortem аудит: {text_sec} сек")
    if photo_sec is not None:
        print(f" • Генерация мобильного фото-креатива: {photo_sec} сек")
    print(f" • Оценка качества контента: {int(critic_score * 100)}% (Одобрено)")
    print(f" • Общее время пайплайна: {total_duration} сек")
    print("=" * 60)

    print("\n📝 СГЕНЕРИРОВАННЫЙ И ОТШЛИФОВАННЫЙ ТЕКСТ ПОСТА:")
    print("-" * 50)
    print(post_text)
    print("-" * 50)

    # 2. Автоматическая публикация в канал
    if auto_publish:
        print(f"\n📡 Отправка результата в Telegram-канал {channel}...")
        broadcaster = AchievementBroadcaster(target_channel=channel)
        has_photo = photo_local_path is not None and os.path.exists(photo_local_path)
        metrics = AchievementBroadcaster.build_honest_metrics(
            text_gen_seconds=text_sec,
            photo_gen_seconds=photo_sec,
            has_photo=has_photo,
            total_seconds=total_duration,
            critic_score=critic_score
        )

        # ── Умное разделение поста на 2 сообщения при превышении лимита (40% / 60%) ──
        part1_caption, part2_text = AchievementBroadcaster.split_text_for_telegram(
            post_text,
            max_caption_len=950,
            target_ratio=0.40
        )

        # ── Сообщение 2: продолжение текста (если пост большой) + время генерации + хэштеги ──
        time_lines = []
        if text_sec is not None:
            time_lines.append(f"• Текст + аудит качества: {round(text_sec, 2)} сек")
        if photo_sec is not None:
            time_lines.append(f"• Фото-креатив: {round(photo_sec, 2)} сек")
        time_lines.append(f"• Итого: {total_duration} сек")

        # Платформы из метрик (HTML-ссылки уже готовы в build_honest_metrics)
        platforms_line = next((m for m in metrics if m.startswith("Платформы")), None)
        if platforms_line:
            time_lines.append(f"• {platforms_line}")
        time_lines.append("• Режим работы: 24/7 автономно")

        telemetry_block = (
            f"⏱️ <b>Время генерации этого поста:</b>\n"
            + "\n".join(time_lines)
            + f"\n\n{post_hashtags}"
        )

        if part2_text:
            metrics_message = f"{part2_text}\n\n---\n{telemetry_block}"
        else:
            metrics_message = telemetry_block

        # Отправка фото с 1-й частью текста (или полным постом)
        pub_res = await broadcaster._publish_via_bot_api(part1_caption, photo_local_path)
        if pub_res is None:
            pub_res = await broadcaster.broadcast_milestone_async(
                title="",
                description=part1_caption,
                metrics=None,
                media_path=photo_local_path
            )

        if pub_res and pub_res.get("status") == "success":
            print(f"🎉 УСПЕШНО! Фото + сообщение 1 (40%) опубликованы в {channel}")
            # Небольшая пауза, затем сообщение 2 (60% + метрики + хэштеги)
            import asyncio
            await asyncio.sleep(2)
            text_res = await broadcaster._publish_via_bot_api(metrics_message, None)
            if text_res and text_res.get("status") == "success":
                print(f"⏱️ Сообщение 2 (60% текста + метрики + хэштеги) опубликовано в {channel}")
            else:
                print(f"⚠️ Не удалось отправить сообщение 2: {text_res}")
        else:
            print(f"⚠️ Статус публикации: {pub_res}")

    return {
        "status": "success",
        "post_text": post_text,
        "gen_duration": gen_duration,
        "total_duration": total_duration,
        "critic_score": critic_score,
        "photo_prompt": photo_prompt,
        "photo_path": photo_local_path
    }

def main():
    parser = argparse.ArgumentParser(description="Run autonomous UCust AI pipeline from prompt to post")
    parser.add_argument(
        "--prompt", "--topic",
        type=str,
        default="Команда UCust собрана, начинает активную работу над проектом и бросает вызов крупным IT-корпорациям и неповоротливым маркетинговым агентствам",
        help="Тема или промпт для генерации"
    )
    parser.add_argument("--company", type=str, default="UCust", help="Название компании")
    parser.add_argument("--niche", type=str, default="Автономный AI-маркетинг и мульти-агентные системы", help="Ниша")
    parser.add_argument("--tone", type=str, default="Дерзкий, уверенный, вдохновляющий", help="Тон общения")
    parser.add_argument("--stage", type=str, default="problem_aware", choices=["unaware", "problem_aware", "solution_aware", "product_aware", "most_aware"], help="Ступень воронки Бена Ханта (1..5)")
    parser.add_argument("--framework", type=str, default=None, choices=["AIDA", "PAS", "BAB", "4P", "StoryBrand", "HSO", "FAB"], help="Формула копирайтинга")
    parser.add_argument("--trigger", type=str, default=None, choices=["social_proof", "scarcity_fomo", "authority", "reciprocity", "risk_reversal"], help="Психологический триггер Чалдини")
    parser.add_argument("--tier", type=str, default="BUSINESS", choices=["START", "BUSINESS", "ENTERPRISE", "CUSTOM"], help="Тариф медиа-оснащения")
    parser.add_argument("--aspect-ratio", "--ratio", type=str, default="1:1", choices=["1:1", "4:5", "9:16", "16:9", "3:4", "4:3"], help="Формат соотношения сторон фото")
    parser.add_argument("--variation-index", "--variation", "-v", type=int, default=0, help="Номер вариации ракурса/интерьера при перегенерации (0, 1, 2, 3...)")
    parser.add_argument("--images", "--files", "-i", "-f", nargs="+", default=None, help="Пути к локальным файлам/фото или URL вложений для анализа Vision (Moondream) и генерации (ComfyUI)")
    parser.add_argument("--channel", type=str, default="@testaipublisher", help="Целевой Telegram-канал")
    parser.add_argument("--no-publish", action="store_true", help="Не отправлять в Telegram, только вывести в консоль")

    args = parser.parse_args()

    asyncio.run(run_pipeline(
        topic=args.prompt,
        company_name=args.company,
        niche=args.niche,
        tone=args.tone,
        stage=args.stage,
        framework=args.framework,
        trigger=args.trigger,
        tier=args.tier,
        aspect_ratio=args.aspect_ratio,
        variation_index=args.variation_index,
        images=args.images,
        channel=args.channel,
        auto_publish=not args.no_publish
    ))

if __name__ == "__main__":
    main()
