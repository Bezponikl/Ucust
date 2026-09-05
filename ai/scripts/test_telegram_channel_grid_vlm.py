# File: scripts/test_telegram_channel_grid_vlm.py
"""
Скрипт для тестирования связки:
1. Парсер публичных медиа из Telegram-канала (https://t.me/s/dvachannel)
2. Moondream VQA (Vision Analyst) — извлечение объектов, света, контраста, палитры
3. AdvancedVisualDirector (Grid DNA) — построение сетки 3x3, аудит колористики и рекомендация следующего слота
"""

import os
import sys
import re
import urllib.request
import json
from pathlib import Path

# Enable UTF-8 console output for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root and ai dir to path
ai_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ai_dir not in sys.path:
    sys.path.insert(0, ai_dir)

from skills.moondream_vqa import MoondreamVQASkill
from skills.advanced_visual_director import AdvancedVisualDirector


def fetch_telegram_channel_images(channel_url: str, output_dir: str, max_images: int = 9) -> list:
    """
    Парсит публичную веб-версию канала t.me/s/<channel> и скачивает последние изображения.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Нормализуем URL в формат https://t.me/s/<channel>
    clean_url = channel_url.replace("https://t.me/", "https://t.me/s/").replace("http://t.me/", "https://t.me/s/")
    if "/s/" not in clean_url:
        parts = clean_url.rstrip("/").split("/")
        clean_url = f"https://t.me/s/{parts[-1]}"
        
    print(f"\n[1. TELEGRAM PARSER] [WEB] Запрос публичной веб-ленты: {clean_url}...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        req = urllib.request.Request(clean_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[1. TELEGRAM PARSER] [WARN] Ошибка загрузки канала через веб-превью: {e}")
        return []

    # Ищем фоновые изображения постов в Telegram Web:
    # <a class="tgme_widget_message_photo_wrap" ... style="background-image:url('https://cdn...')">
    # или <i class="link_preview_image" ... style="background-image:url('https://cdn...')">
    raw_urls = re.findall(r"background-image:url\('(https://[^']+)'\)", html)
    
    # Также ищем прямые теги img
    img_tags = re.findall(r'<img[^>]+src=["\'](https://[^"\']+)["\']', html)
    all_found = []
    
    for u in raw_urls + img_tags:
        if "cdn" in u or "telegram" in u or "telesco" in u:
            if u not in all_found:
                all_found.append(u)

    print(f"[1. TELEGRAM PARSER] [OK] Найдено {len(all_found)} медиа-ссылок в ленте канала.")
    
    # Берем последние N изображений
    selected_urls = all_found[-max_images:] if len(all_found) >= max_images else all_found
    downloaded_paths = []

    for idx, img_url in enumerate(selected_urls, start=1):
        ext = ".jpg"
        if ".png" in img_url:
            ext = ".png"
        elif ".webp" in img_url:
            ext = ".webp"
            
        file_path = os.path.join(output_dir, f"post_media_{idx:02d}{ext}")
        try:
            img_req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(img_req, timeout=10) as img_resp, open(file_path, "wb") as f:
                f.write(img_resp.read())
            downloaded_paths.append(file_path)
            print(f"   [DOWNLOAD] Скачано фото #{idx:02d}: {os.path.basename(file_path)} ({os.path.getsize(file_path)} bytes)")
        except Exception as err:
            print(f"   [WARN] Ошибка скачивания {img_url}: {err}")

    return downloaded_paths


def run_telegram_grid_audit():
    channel_url = "https://t.me/dvachannel"
    output_dir = os.path.join(ai_dir, "output", "temp_dvachannel")
    
    print("=" * 80)
    print(">> UCUST AI — ТЕСТ СКВОЗНОГО АНАЛИЗА ТЕЛЕГРАМ-КАНАЛА: PARSER + MOONDREAM VLM + GRID DNA")
    print("=" * 80)
    
    # Шаг 1. Парсинг
    images = fetch_telegram_channel_images(channel_url, output_dir=output_dir, max_images=9)
    
    if not images:
        print("\n[WARN] Не удалось скачать медиа напрямую. Создаем синтетические тестовые кадры для симуляции.")
        from PIL import Image, ImageDraw
        os.makedirs(output_dir, exist_ok=True)
        sample_colors = ["#ff5722", "#2196f3", "#4caf50", "#9c27b0", "#ffeb3b", "#e91e63", "#00bcd4", "#795548", "#607d8b"]
        for i, color in enumerate(sample_colors, 1):
            img = Image.new("RGB", (600, 600), color=color)
            d = ImageDraw.Draw(img)
            d.text((50, 50), f"Telegram Media #{i}", fill="white")
            p = os.path.join(output_dir, f"simulated_post_{i:02d}.jpg")
            img.save(p)
            images.append(p)

    # Шаг 2. Анализ через Moondream VQA
    print("\n" + "=" * 80)
    print("[2. MOONDREAM VLM / VISION ANALYST] Комплексный аудит изображений...")
    print("=" * 80)
    
    vqa_skill = MoondreamVQASkill()
    vqa_report = vqa_skill.analyze_attachments_batch(images, topic="Новостная лента Двач", company_name="Двач")
    
    print(f" Обработано кадров: {vqa_report.get('count')}")
    print(f" Извлеченная фирменная палитра: {vqa_report.get('colors')}")
    print("\n Разбор каждого кадра:")
    for idx, item in enumerate(vqa_report.get("items", []), start=1):
        print(f"  • Кадр #{idx:02d} [{item.get('dimensions')}, {item.get('aspect_ratio')}]:")
        print(f"    - Освещение / Контраст: {item.get('lighting')} | {item.get('contrast')}")
        print(f"    - Цвета: {item.get('dominant_colors')}")
        print(f"    - Смысловое описание: {item.get('description')}")
        print(f"    - Prompt Keywords: {item.get('prompt_enhancement')[:90]}...")

    # Шаг 3. Анализ сетки Grid DNA через AdvancedVisualDirector
    print("\n" + "=" * 80)
    print("[3. ADVANCED VISUAL DIRECTOR] Построение матрицы Grid DNA 3x3...")
    print("=" * 80)
    
    director = AdvancedVisualDirector()
    grid_audit = director.analyze_visual_grid(images, niche="Медиа / Новости / Мемы")
    
    print(f" Фирменная Brand-палитра (Hex): {grid_audit.get('brand_hex_palette')}")
    print(f" Доминантный цвет: {grid_audit.get('dominant_color')}")
    print(f" Акцентный цвет: {grid_audit.get('accent_color')}")
    
    print("\n РАСКЛАДКА 3x3 GRID MATRIX (Instagram / Галерея):")
    for slot in grid_audit.get("grid_3x3_slots", []):
        print(f"  [Слот #{slot['slot']}] {slot['type'].upper()} — {slot['title']}: {slot['description']}")
        
    print("\n РЕКОМЕНДАЦИЯ ДЛЯ СЛЕДУЮЩЕГО ПОСТА:")
    rec = grid_audit.get("next_post_recommendation", {})
    print(f"  • Целевой слот: #{rec.get('target_slot')}")
    print(f"  • Рекомендуемый тип плана: {rec.get('recommended_shot_type')}")
    print(f"  • Правило композиции: {rec.get('composition_rule')}")
    print(f"  • Модификаторы промпта: {rec.get('suggested_prompt_modifiers')}")
    print(f"  • Арт-дирекшн совет: {rec.get('advice')}")

    # Шаг 4. Сборка адаптивного промпта под следующий слот
    print("\n" + "=" * 80)
    print("[4. PROMPT ENGINEERING] Генерация photorealistic prompt для следующего слота...")
    print("=" * 80)
    
    generated_prompt = director.create_photorealistic_prompt(
        topic="Репортажный мем-инцидент в городе, живая городская сцена",
        niche="Новостное медиа",
        aspect_ratio="1:1",
        brand_colors=grid_audit.get("brand_hex_palette")
    )
    
    print(f" POSITIVE PROMPT:\n{generated_prompt['positive_prompt']}\n")
    print(f" NEGATIVE PROMPT:\n{generated_prompt['negative_prompt']}")
    
    print("\n" + "=" * 80)
    print(">> ВСЕ ЭТАПЫ (TELEGRAM SCRAPE -> VLM DOSSIER -> GRID DNA -> PROMPT DIRECTING) ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 80)


if __name__ == "__main__":
    run_telegram_grid_audit()
