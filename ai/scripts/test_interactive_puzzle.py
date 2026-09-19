"""
Тестовый скрипт для проверки InteractivePuzzleSlicer и генератора HTML-превью.
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from PIL import Image, ImageDraw, ImageFont

# Добавляем пути к модулям
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if AI_DIR not in sys.path:
    sys.path.insert(0, AI_DIR)

from skills.interactive_puzzle_generator import (
    InteractivePuzzleSlicer,
    CinematographyDirectorPuzzleExtension,
    PUZZLE_PRESETS
)


def create_mock_scene_image(scene_idx: int, width: int = 1024, height: int = 1024) -> Image.Image:
    """Генерирует тестовую цветовую картинку со слоями для проверки нарезки и совмещения."""
    img = Image.new("RGB", (width, height), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)

    colors = [
        [(40, 60, 90), (50, 80, 120), (30, 50, 80)],        # Слой 1 (Фон)
        [(30, 130, 70), (200, 160, 100), (160, 50, 40)],    # Слой 2 (Крышка/Арт)
        [(25, 95, 55), (180, 140, 90), (190, 190, 190)],    # Слой 3 (Стакан)
        [(110, 75, 45), (100, 70, 40), (120, 80, 50)]       # Слой 4 (Стол)
    ]

    # Слой 1: 0 - 22%
    y1 = int(height * 0.22)
    draw.rectangle([0, 0, width, y1], fill=colors[0][scene_idx % 3])
    draw.text((width // 2 - 100, y1 // 2), f"Слой 1: Фон (Вариант {scene_idx + 1})", fill=(255, 255, 255))

    # Слой 2: 22% - 44%
    y2 = int(height * 0.44)
    draw.rectangle([0, y1, width, y2], fill=colors[1][scene_idx % 3])
    draw.text((width // 2 - 120, (y1 + y2) // 2), f"Слой 2: Крышка/Арт (Вариант {scene_idx + 1})", fill=(255, 255, 255))

    # Слой 3: 44% - 76%
    y3 = int(height * 0.76)
    draw.rectangle([0, y2, width, y3], fill=colors[2][scene_idx % 3])
    draw.text((width // 2 - 110, (y2 + y3) // 2), f"Слой 3: Стакан (Вариант {scene_idx + 1})", fill=(255, 255, 255))

    # Слой 4: 76% - 100%
    draw.rectangle([0, y3, width, height], fill=colors[3][scene_idx % 3])
    draw.text((width // 2 - 100, (y3 + height) // 2), f"Слой 4: Стол (Вариант {scene_idx + 1})", fill=(255, 255, 255))

    # Центральный ориентир
    draw.line([width // 2, 0, width // 2, height], fill=(255, 255, 255, 128), width=2)

    return img


def main():
    print("🚀 [1/3] Проверка генератора промптов CinematographyDirectorPuzzleExtension для всех ниш...")
    for niche in ("coffee", "beauty", "legal", "banking"):
        preset = PUZZLE_PRESETS[niche]
        print(f"\n==================== НИША: {preset.niche} ({preset.title}) ====================")
        print(f"🎯 CTA Хук: {preset.cta_hook}")
        prompts = CinematographyDirectorPuzzleExtension.compose_puzzle_batch(niche, f"Alpha {niche.capitalize()} Group")
        for i, p in enumerate(prompts):
            print(f"   📸 Сцена #{i+1}: {p[:130]}...")

    print("\n✂️ [2/3] Создание тестовых сцен и нарезка слоев...")
    mock_images = [create_mock_scene_image(i) for i in range(3)]
    
    slicer = InteractivePuzzleSlicer()
    layer_pools = slicer.slice_batch(mock_images)

    print(f"✅ Нарезано слоев: {len(layer_pools)}")
    for i, pool in enumerate(layer_pools):
        print(f"   - Слой {i+1}: {len(pool)} вариаций, размер полосы: {pool[0].size}")

    print("\n📦 [3/3] Экспорт пакета и создание HTML-превью...")
    output_dir = os.path.join(AI_DIR, "output", "test_puzzle_carousel")
    manifest = slicer.export_puzzle_package(layer_pools, output_dir, prefix="universal_mix_match")

    print(f"🎉 Пакет успешно сохранен в: {output_dir}")
    print(f"🌐 HTML-превью доступно: {manifest['html_preview']}")


if __name__ == "__main__":
    main()
