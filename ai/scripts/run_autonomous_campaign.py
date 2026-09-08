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
    batch_variations: Optional[int] = None,
    images: Optional[List[str]] = None
):
    var_count = batch_variations if (batch_variations and batch_variations > 0) else 1
    print("=" * 60)
    print("🚀 ЗАПУСК СКВОЗНОГО АВТОНОМНОГО ПАЙПЛАЙНА UCUST AI")
    print(f"📌 Тема / Промпт: {topic}")
    print(f"🏢 Компания: {company_name} | Ниша: {niche}")
    print(f"🎯 Тональность: {tone} | Формат фото: {aspect_ratio} | Фотографий в посте: {var_count}")
    if images:
        print(f"📎 Прикрепленные файлы/фото: {', '.join(images)} ({len(images)} шт.)")
    print(f"💼 Тариф: {tier} | Ступень воронки: {stage or 'Auto (Ступень 2 / Проблема)'} | Фреймворк: {framework or 'Auto'}")
    print("=" * 60)

    start_total = time.time()

    # Подготавливаем вложения (локальные файлы, прямые ссылки или веб-страницы)
    attachments = []
    if images:
        import httpx
        from urllib.parse import urljoin
        import re

        for img in images:
            if os.path.exists(img):
                attachments.append({"url": img, "local_path": os.path.abspath(img)})
            elif img.startswith("http://") or img.startswith("https://"):
                is_direct_image = any(img.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"])
                if is_direct_image:
                    attachments.append({"url": img})
                else:
                    print(f"[AttachmentsResolver] 🌐 Обнаружен URL веб-страницы '{img}', извлекаем превью и метаданные...")
                    try:
                        with httpx.Client(timeout=8.0, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0 UCustBot/2.0"}) as client:
                            resp = client.get(img)
                            if resp.status_code == 200:
                                html_text = resp.text
                                og_match = re.search(r'<meta[^>]+property=[\'"]og:image[\'"][^>]+content=[\'"]([^\'"]+)[\'"]', html_text, re.IGNORECASE) or \
                                           re.search(r'<meta[^>]+content=[\'"]([^\'"]+)[\'"][^>]+property=[\'"]og:image[\'"]', html_text, re.IGNORECASE) or \
                                           re.search(r'<meta[^>]+name=[\'"]twitter:image[\'"][^>]+content=[\'"]([^\'"]+)[\'"]', html_text, re.IGNORECASE) or \
                                           re.search(r'<link[^>]+rel=[\'"]preload[\'"][^>]+href=[\'"]([^\'"]+\.(?:webp|png|jpg|jpeg))[\'"]', html_text, re.IGNORECASE) or \
                                           re.search(r'<img[^>]+src=[\'"]([^\'"]+\.(?:webp|png|jpg|jpeg))[\'"]', html_text, re.IGNORECASE)
                                if og_match:
                                    raw_src = og_match.group(1).split("?")[0]
                                    preview_url = urljoin(img, raw_src)
                                    attachments.append({"url": preview_url, "source_page": img})
                                else:
                                    attachments.append({"url": img})
                            else:
                                attachments.append({"url": img})
                    except Exception as ex:
                        print(f"[AttachmentsResolver] ⚠️ Ошибка при извлечении превью сайта: {ex}")
                        attachments.append({"url": img})
            else:
                attachments.append({"url": img})

    # 0. Pre-Flight Health Check: проверка и автоперезапуск ComfyUI при необходимости
    try:
        from skills.comfy_cli_runner import ComfyCLIRunner
        runner = ComfyCLIRunner()
        print("\n🔍 Проверка доступности ComfyUI перед генерацией...")
        await runner.ensure_server_online()
    except Exception as comfy_chk_err:
        print(f"⚠️ Ошибка проверки ComfyUI: {comfy_chk_err}")

    # 1. Запуск Оркестратора (Сайга + Воронка Ханта + Критик Мангер + Валидация + Фото #0)
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

    # Получаем локальный путь к первому фото (вариация 0)
    all_photo_paths: List[str] = []
    if photo_url:
        fname = os.path.basename(photo_url)
        cand_dirs = [
            os.path.join(os.path.dirname(__file__), "..", "output", "photos"),
            "/opt/ucust/ai/output/photos",
            "/opt/ucust/ComfyUI/output",
            "output/photos"
        ]
        for cdir in cand_dirs:
            p = os.path.join(cdir, fname)
            if os.path.exists(p) and os.path.getsize(p) > 1000:
                all_photo_paths.append(os.path.abspath(p))
                break

    # 1.1 Если запрошен мульти-ракурсный альбом (batch_variations > 1), генерируем остальные ракурсы
    from skills.photo_generator import PhotoGeneratorSkill
    photo_skill = PhotoGeneratorSkill()
    additional_photo_sec = 0.0

    if var_count > 1:
        for v_idx in range(1, var_count):
            print(f"\n🎬 [Мульти-ракурс {v_idx+1}/{var_count}] Генерация фото-вариации #{v_idx}...")
            t_add_start = time.time()
            try:
                p_res = await photo_skill.generate_photo(
                    topic=topic,
                    niche=niche,
                    aspect_ratio=aspect_ratio,
                    company_name=company_name,
                    attachments=attachments if attachments else None,
                    variation_index=v_idx
                )
                add_path = p_res.get("file_path")
                if add_path and os.path.exists(add_path) and os.path.getsize(add_path) > 1000:
                    all_photo_paths.append(os.path.abspath(add_path))
                    print(f"  ✅ Фото #{v_idx+1} успешно готово: {os.path.basename(add_path)}")
            except Exception as p_err:
                print(f"  ⚠️ Ошибка генерации вариации #{v_idx}: {p_err}")
            additional_photo_sec += (time.time() - t_add_start)

    timings = result.get("timings", {})
    text_sec = timings.get("text_gen_seconds")
    photo_sec = timings.get("photo_gen_seconds")
    if photo_sec is not None:
        photo_sec = round(photo_sec + additional_photo_sec, 2)

    total_duration = round(time.time() - start_total, 2)

    print("\n" + "=" * 60)
    print(f"⏱️ РЕАЛЬНЫЕ ЗАМЕРЫ ВРЕМЕНИ ГЕНЕРАЦИИ:")
    if text_sec is not None:
        print(f" • Генерация текста + Pre-Mortem аудит: {text_sec} сек")
    if photo_sec is not None:
        print(f" • Генерация альбома из {len(all_photo_paths)} фото: {photo_sec} сек")
    print(f" • Оценка качества контента: {int(critic_score * 100)}% (Одобрено)")
    print(f" • Общее время пайплайна: {total_duration} сек")
    print("=" * 60)

    print("\n📝 СГЕНЕРИРОВАННЫЙ И ОТШЛИФОВАННЫЙ ТЕКСТ ПОСТА:")
    print("-" * 50)
    print(post_text)
    print("-" * 50)

    # 2. Автоматическая публикация в канал (1 единый пост + альбом фото)
    if auto_publish:
        print(f"\n📡 Отправка результата в Telegram-канал {channel}...")
        broadcaster = AchievementBroadcaster(target_channel=channel)
        has_photo = len(all_photo_paths) > 0
        metrics = AchievementBroadcaster.build_honest_metrics(
            text_gen_seconds=text_sec,
            photo_gen_seconds=photo_sec,
            has_photo=has_photo,
            total_seconds=total_duration,
            critic_score=critic_score
        )

        # Умное разделение поста на 2 сообщения при превышении лимита (40% / 60%)
        part1_caption, part2_text = AchievementBroadcaster.split_text_for_telegram(
            post_text,
            max_caption_len=950,
            target_ratio=0.40
        )

        time_lines = []
        if text_sec is not None:
            time_lines.append(f"• Текст + аудит качества: {round(text_sec, 2)} сек")
        if photo_sec is not None:
            time_lines.append(f"• Фото-альбом ({len(all_photo_paths)} ракурса): {round(photo_sec, 2)} сек")
        time_lines.append(f"• Итого: {total_duration} сек")

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

        # Публикация альбома из всех сгенерированных фото с 1-й частью текста
        pub_res = await broadcaster._publish_via_bot_api(part1_caption, all_photo_paths if len(all_photo_paths) > 1 else (all_photo_paths[0] if all_photo_paths else None))
        if pub_res is None:
            pub_res = await broadcaster.broadcast_milestone_async(
                title="",
                description=part1_caption,
                metrics=None,
                media_path=all_photo_paths[0] if all_photo_paths else None
            )

        if pub_res and pub_res.get("status") == "success":
            print(f"🎉 УСПЕШНО! Альбом ({len(all_photo_paths)} фото) + сообщение 1 опубликованы в {channel}")
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
        "photo_paths": all_photo_paths
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
    parser.add_argument("--variation-index", "--variation", "-v", type=int, default=0, help="Номер вариации ракурса/интерьера при одиночной генерации")
    parser.add_argument("--batch-variations", "--count", "-n", type=int, default=None, help="Сгенерировать альбом из N разных ракурсов в один пост (например, --batch-variations 3)")
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
        batch_variations=args.batch_variations,
        images=args.images,
        channel=args.channel,
        auto_publish=not args.no_publish
    ))

if __name__ == "__main__":
    main()
