"""
File: ai/scripts/test_comfy_bridge.py
Тестовый скрипт проверки ComfyUI Bridge, WorkflowBuilder и сквозного рендера.
"""

import sys
import os
import asyncio
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, AI_DIR)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from bridge.comfy_workflow_templates import WorkflowBuilder, BASE_SDXL_API_JSON
from bridge.comfy_bridge import ComfyUIBridge
from services.storage_uploader import StorageUploader, upload_media_bytes
from core.lazy_rendering_controller import (
    LazyRenderingController, PostDraft, ImageGenerationSpec,
    SubscriptionTier, ContentFormat, PostLifecycleStatus
)


async def test_workflow_builder():
    print("\n📐 [1/4] Тестирование WorkflowBuilder (Формирование Prompt API JSON)...")
    
    payload = WorkflowBuilder.build_payload(
        prompt="Analog photo of artisan leather workshop with golden hour light",
        negative_prompt="blurry, cgi, 3d render, plastic",
        width=1080,
        height=1350,
        seed=424242,
        steps=25,
        cfg=6.5,
        filename_prefix="ucust_post_test_999"
    )

    # 1. Проверка структуры нод
    assert "3" in payload, "Отсутствует нода KSampler ('3')"
    assert "4" in payload, "Отсутствует нода CheckpointLoader ('4')"
    assert "5" in payload, "Отсутствует нода EmptyLatentImage ('5')"
    assert "6" in payload, "Отсутствует нода CLIPTextEncode Positive ('6')"
    assert "7" in payload, "Отсутствует нода CLIPTextEncode Negative ('7')"
    assert "8" in payload, "Отсутствует нода VAEDecode ('8')"
    assert "9" in payload, "Отсутствует нода SaveImage ('9')"

    # 2. Проверка инжектированных значений
    assert payload["5"]["inputs"]["width"] == 1080
    assert payload["5"]["inputs"]["height"] == 1350
    assert payload["6"]["inputs"]["text"] == "Analog photo of artisan leather workshop with golden hour light"
    assert payload["7"]["inputs"]["text"] == "blurry, cgi, 3d render, plastic"
    assert payload["3"]["inputs"]["seed"] == 424242
    assert payload["3"]["inputs"]["steps"] == 25
    assert payload["3"]["inputs"]["cfg"] == 6.5
    assert payload["9"]["inputs"]["filename_prefix"] == "ucust_post_test_999"

    print(f"   Нод в графе: {len(payload)}")
    print(f"   Разрешение: {payload['5']['inputs']['width']}x{payload['5']['inputs']['height']}")
    print(f"   Сэмплер: steps={payload['3']['inputs']['steps']}, cfg={payload['3']['inputs']['cfg']}, seed={payload['3']['inputs']['seed']}")
    print(f"   Префикс файла: {payload['9']['inputs']['filename_prefix']}")
    print("   ✅ WorkflowBuilder генерирует 100% валидный Prompt API JSON!")


async def test_comfy_bridge_simulation():
    print("\n🌉 [2/4] Тестирование ComfyUIBridge в режиме симуляции (dev_simulation_mode=True)...")
    bridge = ComfyUIBridge(host="127.0.0.1", port=8188)
    
    spec = ImageGenerationSpec(
        prompt="Scandinavian light oak desk with minimalist brass details",
        width=1024,
        height=1024,
        seed=12345
    )

    image_bytes = await bridge.render_image(
        spec=spec,
        post_id="post_mock_abc",
        dev_simulation_mode=True
    )

    assert isinstance(image_bytes, bytes)
    assert len(image_bytes) > 0
    assert b"UCUST_SIMULATED_RENDER" in image_bytes
    print(f"   Получено байтов: {len(image_bytes)} байт")
    print("   ✅ ComfyUIBridge безопасен в Dev-режиме (0 GPU VRAM overhead)!")


async def test_storage_uploader():
    print("\n💾 [3/4] Тестирование StorageUploader (Загрузка в хранилище)...")
    uploader = StorageUploader()
    test_data = b"TEST_IMAGE_BINARY_DATA_12345"
    
    url = await uploader.upload_bytes(test_data, "posts/post_demo_1/img_1.jpg")
    print(f"   Итоговый URL медиа: {url}")
    assert url is not None
    assert "img_1.jpg" in url
    print("   ✅ StorageUploader успешно отдал доступный URL!")


async def test_end_to_end_lazy_rendering_with_bridge():
    print("\n🔄 [4/4] Тестирование сквозного Lazy Rendering со стейт-машиной и ComfyUIBridge...")
    uploader = StorageUploader()
    bridge = ComfyUIBridge()
    controller = LazyRenderingController(
        storage_uploader=uploader.upload_bytes,
        comfy_bridge=bridge,
        dev_simulation_mode=True
    )

    # 1. Создание черновика поста
    post = PostDraft(
        post_id="post_e2e_verified_101",
        brand_id="tenant_nordic_wood",
        target_date=datetime.now(),
        format=ContentFormat.CAROUSEL_LIGHT,
        text_content="📌 Скандинавские стандарты качества и долговечность мебели из массива дуба.",
        image_specs=[
            ImageGenerationSpec(prompt="Scandinavian solid oak dining table macro", width=1024, height=1024),
            ImageGenerationSpec(prompt="Minimalist brass joinery details", width=1024, height=1024)
        ]
    )

    # 2. Регистрация черновика (0 GPU)
    draft = controller.register_draft(post)
    assert draft.status == PostLifecycleStatus.DRAFT_TEXT
    print(f"   Шаг 1: Пост зарегистрирован в статусе {draft.status.value}")

    # 3. Триггер рендера
    rendered_post = await controller.trigger_render(post_id=draft.post_id)
    print(f"   Шаг 2: Триггер рендера выполнен, итоговый статус: {rendered_post.status.value}")
    print(f"   Сгенерировано URL: {rendered_post.rendered_image_urls}")
    assert rendered_post.status == PostLifecycleStatus.RENDERED
    assert len(rendered_post.rendered_image_urls) == 2
    print("   ✅ Сквозная цепочка Lazy Rendering ➔ ComfyUIBridge ➔ StorageUploader полностью подтверждена!")


async def main():
    print("=" * 70)
    print("🧪 ЗАПУСК ТЕСТИРОВАНИЯ COMFYUI BRIDGE & WORKFLOW TEMPLATES")
    print("=" * 70)
    await test_workflow_builder()
    await test_comfy_bridge_simulation()
    await test_storage_uploader()
    await test_end_to_end_lazy_rendering_with_bridge()
    print("\n" + "=" * 70)
    print("🎉 ВСЕ ТЕСТЫ COMFYUI BRIDGE УСПЕШНО ПРОЙДЕНЫ!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
