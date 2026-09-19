"""
File: ai/scripts/test_content_generation_engine.py
Интеграционный тест ContentGenerationEngine и Celery задачи generate_post_draft_task.
"""

import sys
import os
import asyncio

# Добавляем корневой путь ai в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from skills.content_generation_engine import ContentGenerationEngine
from celery_tasks import generate_post_draft_task


def test_content_generation_lifecycle():
    print("=" * 70, flush=True)
    print("🚀 ТЕСТИРОВАНИЕ ГЕНЕРАЦИИ КОНТЕНТА И RAG РЕТРИВЕРА (CORE VALUE LOOP)", flush=True)
    print("=" * 70, flush=True)

    project_id = "test_cafe_specialty_2026"
    profile = {
        "about": {
            "name": "Кофейня Аромат Зерен",
            "niche": "Спешелти кофейня и выпечка",
            "positioning": "Свежеобжаренное зерно Эфиопия и авторские напитки"
        },
        "goals": {
            "content_goals": ["Вовлечение гостей и рост чека"],
            "tone_of_voice": ["Теплый", "Гостеприимный", "Экспертный"]
        }
    }

    # -------------------------------------------------------------
    # ШАГ 1: Прямой вызов ContentGenerationEngine
    # -------------------------------------------------------------
    print("\n[ШАГ 1] Вызов ContentGenerationEngine.generate_post()...", flush=True)
    engine = ContentGenerationEngine(dev_mode=True)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        post_draft = loop.run_until_complete(engine.generate_post(
            project_id=project_id,
            topic="Сезонное авторское меню: хвойный латте с брусникой",
            profile=profile,
            aspect_ratio="1:1"
        ))
    finally:
        loop.close()

    print(f"  ✅ PostDraft успешно сформирован: post_id='{post_draft.post_id}', status='{post_draft.status}'", flush=True)
    print(f"  Текст поста (первые 150 символов):\n  {post_draft.text_content[:150]}...", flush=True)
    assert post_draft.status.value == "draft_text" or post_draft.status == "draft_text"
    assert len(post_draft.image_specs) > 0
    assert post_draft.image_specs[0].aspect_ratio == "1:1"
    print(f"  ✅ ImageGenerationSpec: '{post_draft.image_specs[0].prompt[:70]}...'", flush=True)

    # -------------------------------------------------------------
    # ШАГ 2: Вызов Celery таски generate_post_draft_task
    # -------------------------------------------------------------
    print("\n[ШАГ 2] Вызов Celery таски generate_post_draft_task...", flush=True)
    celery_res = generate_post_draft_task(
        project_id=project_id,
        topic="Почему спешелти кофе не горчит: секреты светлой обжарки",
        profile=profile,
        aspect_ratio="4:5"
    )

    print(f"  ✅ Celery таска вернула статус: {celery_res.get('status')}", flush=True)
    assert celery_res.get("status") == "success"
    assert "post_draft" in celery_res
    draft_dict = celery_res["post_draft"]
    assert draft_dict.get("project_id") == project_id or draft_dict.get("brand_id") == project_id

    print("\n" + "=" * 70, flush=True)
    print("🎉 КОНВЕЙЕР ГЕНЕРАЦИИ КОНТЕНТА И СВЯЗКА С CELERY ПОЛНОСТЬЮ РАБОТАЮТ!", flush=True)
    print("=" * 70, flush=True)


if __name__ == "__main__":
    test_content_generation_lifecycle()
