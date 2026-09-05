# File: scripts/analyze_user_uploaded_images.py
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ai_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ai_dir not in sys.path:
    sys.path.insert(0, ai_dir)

from skills.moondream_vqa import MoondreamVQASkill
from skills.advanced_visual_director import AdvancedVisualDirector

image_paths = [
    r"C:\Users\Metal\.gemini\antigravity\brain\a1e5a069-d05d-4bc6-88a9-30a1e0cf21c2\.user_uploaded\media_1788546599076.png",
    r"C:\Users\Metal\.gemini\antigravity\brain\a1e5a069-d05d-4bc6-88a9-30a1e0cf21c2\.user_uploaded\media_1788546654594.png",
    r"C:\Users\Metal\.gemini\antigravity\brain\a1e5a069-d05d-4bc6-88a9-30a1e0cf21c2\.user_uploaded\media_1788546682702.jpg",
    r"C:\Users\Metal\.gemini\antigravity\brain\a1e5a069-d05d-4bc6-88a9-30a1e0cf21c2\.user_uploaded\media_1788546688225.png",
    r"C:\Users\Metal\.gemini\antigravity\brain\a1e5a069-d05d-4bc6-88a9-30a1e0cf21c2\.user_uploaded\media_1788546695419.png"
]

vqa = MoondreamVQASkill()
batch = vqa.analyze_attachments_batch(image_paths, topic="Анализ постов канала", company_name="Двач")

director = AdvancedVisualDirector()
grid = director.analyze_visual_grid(image_paths, niche="Новостное медиа / Вирусный контент")

print("\n" + "=" * 60)
print("VQA DOSSIER PER IMAGE:")
print("=" * 60)
for idx, it in enumerate(batch.get("items", []), 1):
    print(f"Кадр #{idx}:")
    print(f"  - Размеры / Пропорции: {it.get('dimensions')} ({it.get('aspect_ratio')})")
    print(f"  - Освещение / Контраст: {it.get('lighting')} | {it.get('contrast')}")
    print(f"  - Доминирующие цвета (Hex): {it.get('dominant_colors')}")
    print(f"  - Описание: {it.get('description')}")
    print(f"  - Prompt Keywords: {it.get('prompt_enhancement')}")

print("\n" + "=" * 60)
print("GRID DNA SUMMARY:")
print("=" * 60)
print(f"Brand Hex Palette: {grid.get('brand_hex_palette')}")
print(f"Dominant Color: {grid.get('dominant_color')}")
print(f"Accent Color: {grid.get('accent_color')}")
print(f"Next Slot Recommendation: {grid.get('next_post_recommendation')}")
