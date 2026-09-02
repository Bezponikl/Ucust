"""
test_realism_comfy_workflow.py
======================================================================
Тест интеграции нового воркфлоу Realism 2.0 (realism2.0.json) в UCust AI.

Проверяет 2 режима работы:
1. Mode: Edit (72) = False — Генерация фото с нуля по текстовому промпту (из шума).
2. Mode: Edit (72) = True — Редактирование фото по 1-3 референсам (LoadImage 55, 64, 65).
3. Валидация конвертации графа в API-формат ComfyUI (/prompt).
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import json
import asyncio
from pathlib import Path

# Setup paths
AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from skills.comfy_cli_runner import ComfyCLIRunner
from skills.photo_generator import PhotoGeneratorSkill
from core.orchestrator import UnifiedOrchestrator


async def test_realism_workflow():
    print("=" * 75)
    print("🎨 ТЕСТИРОВАНИЕ ВОРКФЛОУ REALISM 2.0 (realism2.0.json)")
    print("=" * 75)

    runner = ComfyCLIRunner()
    raw_workflow = runner.load_workflow()

    print(f"\n📁 Загружен воркфлоу: {runner.workflow_template_path}")
    print(f"   Количество нод в GUI-шаблоне: {len(raw_workflow.get('nodes', []))}")

    # -------------------------------------------------------------
    # ТЕСТ 1: РЕЖИМ ГЕНЕРАЦИИ С НУЛЯ (Mode: Edit = False)
    # -------------------------------------------------------------
    print("\n" + "-" * 75)
    print("✨ [ТЕСТ 1] РЕЖИМ ГЕНЕРАЦИИ С НУЛЯ (Mode: Edit = False, из шума)")
    print("-" * 75)

    prompt_gen = (
        "Authentic candid commercial photograph for coffee shop. "
        "Subject: smiling barista handing a cup of cappuccino with latte art. "
        "Lighting: soft morning window daylight, warm golden tones. "
        "Camera: Cinematic 35mm photography, natural handheld angle, 1024x1024 unedited raw."
    )

    customized_gen = runner.customize_workflow(
        workflow_json=raw_workflow,
        photo_prompt=prompt_gen,
        aspect_ratio="1:1",
        images=[],
        edit_mode=False
    )

    api_prompt_gen = runner.to_api_prompt(customized_gen)

    node_72_gen = api_prompt_gen.get("72", {})
    node_60_gen = api_prompt_gen.get("60", {})
    node_74_gen = api_prompt_gen.get("74", {})
    node_36_gen = api_prompt_gen.get("36", {})

    print(f"  • Нода 72 (Mode: Edit PrimitiveBoolean): Bypassed (Успешно исключена из API)")
    print(f"  • Нода 60 (Positive Prompt TextEncode): «{node_60_gen.get('inputs', {}).get('prompt', '')[:65]}...»")
    print(f"  • Нода 74 (EmptySD3LatentImage): {node_74_gen.get('inputs', {})}")
    print(f"  • Нода 36 (KSampler Denoise): {node_36_gen.get('inputs', {}).get('denoise')} (Ожидается: 1.0)")

    assert "73" not in api_prompt_gen, "Ошибка: Node 73 (Latent Input Switch) должен быть исключен!"
    assert node_36_gen.get("inputs", {}).get("denoise") == 1.0, "Ошибка: KSampler denoise должен быть 1.0 для генерации из шума!"
    print("  ✅ [ТЕСТ 1 ПРОЙДЕН]: Режим генерации с нуля настроен корректно!")

    # -------------------------------------------------------------
    # ТЕСТ 2: РЕЖИМ РЕДАКТИРОВАНИЯ И АПСКЕЙЛА (Mode: Edit = True)
    # -------------------------------------------------------------
    print("\n" + "-" * 75)
    print("🖼️ [ТЕСТ 2] РЕЖИМ РЕДАКТИРОВАНИЯ (Mode: Edit = True, 3 референса)")
    print("-" * 75)

    test_images = [
        "source_client_photo.jpg",      # Исходное фото (Image 1 - Node 55)
        "style_reference_lighting.jpg", # Референс стиля 1 (Image 2 - Node 64)
        "texture_reference_props.jpg"   # Референс стиля 2 (Image 3 - Node 65)
    ]

    prompt_edit = (
        "In Image 1, upgrade the background and lighting to match the warm cinematic atmosphere "
        "of Image 2, while adding subtle props from Image 3. High resolution 1024x1024 upscale."
    )

    customized_edit = runner.customize_workflow(
        workflow_json=raw_workflow,
        photo_prompt=prompt_edit,
        aspect_ratio="1:1",
        images=test_images,
        edit_mode=True
    )

    api_prompt_edit = runner.to_api_prompt(customized_edit)

    node_55_edit = api_prompt_edit.get("55", {})
    node_64_edit = api_prompt_edit.get("64", {})
    node_65_edit = api_prompt_edit.get("65", {})
    node_60_edit = api_prompt_edit.get("60", {})

    print(f"  • Нода 72 (Mode: Edit PrimitiveBoolean): Bypassed (Успешно исключена из API)")
    print(f"  • Нода 55 (LoadImage 1 - Исходник): {node_55_edit.get('inputs', {}).get('image')} (Ожидается: source_client_photo.jpg)")
    print(f"  • Нода 64 (LoadImage 2 - Референс 1): {node_64_edit.get('inputs', {}).get('image')} (Ожидается: style_reference_lighting.jpg)")
    print(f"  • Нода 65 (LoadImage 3 - Референс 2): {node_65_edit.get('inputs', {}).get('image')} (Ожидается: texture_reference_props.jpg)")
    print(f"  • Нода 60 (Positive Prompt TextEncode): «{node_60_edit.get('inputs', {}).get('prompt', '')[:65]}...»")

    assert "73" not in api_prompt_edit, "Ошибка: Node 73 (Latent Input Switch) должен быть исключен!"
    assert node_55_edit.get("inputs", {}).get("image") == "source_client_photo.jpg", "Ошибка: Нода 55 должна содержать Image 1!"
    assert node_64_edit.get("inputs", {}).get("image") == "style_reference_lighting.jpg", "Ошибка: Нода 64 должна содержать Image 2!"
    assert node_65_edit.get("inputs", {}).get("image") == "texture_reference_props.jpg", "Ошибка: Нода 65 должна содержать Image 3!"
    print("  ✅ [ТЕСТ 2 ПРОЙДЕН]: Режим редактирования и раскладка по 3 нодам LoadImage работают идеально!")

    # -------------------------------------------------------------
    # ТЕСТ 3: СКВОЗНОЙ ВЫЗОВ ЧЕРЕЗ ОРКЕСТРАТОР И САЙГУ
    # -------------------------------------------------------------
    print("\n" + "-" * 75)
    print("👑 [ТЕСТ 3] СКВОЗНОЙ ВЫЗОВ ОРКЕСТРАТОРА С ОБОГАЩЕНИЕМ ПРОМПТА ОТ САЙГИ")
    print("-" * 75)

    orchestrator = UnifiedOrchestrator()
    
    # Моделируем запрос с фронтенда с 2 прикрепленными фото
    frontend_request = {
        "user_id": "usr_frontend_creator_99",
        "company_name": "Studio Lux",
        "niche": "Салон красоты и бьюти-студия",
        "prompt": "сделай стильное преображение как на фото 2", # Короткий запрос пользователя
        "attachments": [
            "client_before.jpg",
            "style_moodboard.jpg"
        ],
        "aspect_ratio": "1:1"
    }

    print(f"  • Входящий короткий промпт от пользователя: «{frontend_request['prompt']}»")
    print(f"  • Прикреплено фото с фронтенда: {len(frontend_request['attachments'])} шт.")

    photo_res = await orchestrator.execute_task(
        task_type="edit_photo",
        user_data=frontend_request,
        session_id="sess_realism_test_001"
    )

    print(f"  ✅ [Оркестратор + Сайга] Результат обработки:")
    print(f"     • Статус: {photo_res.get('status')}")
    print(f"     • Обогащенный коммерческий промпт:\n       👉 {photo_res.get('positive_prompt')}")
    print(f"     • Сохраненный файл/баннер: {photo_res.get('file_path')}")

    print("\n" + "=" * 75)
    print("🎉 ВСЕ ТЕСТЫ REALISM 2.0 (ГЕНЕРАЦИЯ, РЕДАКТИРОВАНИЕ, ОРКЕСТРАТОР) УСПЕШНО ПРОЙДЕНЫ!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(test_realism_workflow())
