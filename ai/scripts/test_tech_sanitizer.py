"""
test_tech_sanitizer.py
======================================================================
Тестирование фильтра TechSanitizer (Anti-Model-Leak Filter):
1. Строгий запрет на упоминание названий моделей: Saiga, Сайга, Moondream, FLUX, LTX, ComfyUI, RAG.
2. Автоматическая замена на продуктовые возможности (ИИ-копирайтер, компьютерное зрение, генератор студийных фото).
3. Проверка чистоты текстов для официальных каналов UCust.AI.
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from skills.tech_sanitizer import TechSanitizer


def test_tech_sanitizer_suite():
    print("=" * 80)
    print("🛡️ ТЕСТИРОВАНИЕ ФИЛЬТРА ЗАЩИТЫ ОТ УТЕЧЕК НАЗВАНИЙ МОДЕЛЕЙ (TECH SANITIZER)")
    print("=" * 80)

    raw_text = (
        "Наш мультиагентный контур объединяет локальную нейросеть Сайга, "
        "зрительный анализ Moondream, фотогенерацию FLUX и видеомодуль LTX через ComfyUI и RAG."
    )

    cleaned = TechSanitizer.sanitize_text(raw_text)
    print(f"📥 Исходный текст с техническими названиями:\n   {raw_text}\n")
    print(f"📤 Очищенный текст с продуктовыми возможностями:\n   {cleaned}\n")

    forbidden_names = ["сайга", "saiga", "moondream", "flux", "ltx", "comfyui", "rag", "llama"]
    for word in forbidden_names:
        assert word not in cleaned.lower(), f"Обнаружена утечка названия технологии: {word}"

    print("✅ Все названия внутренних моделей и библиотек успешно заблокированы и заменены на продуктовые термины!")


if __name__ == "__main__":
    test_tech_sanitizer_suite()
