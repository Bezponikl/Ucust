"""
test_media_retention_and_prompt_rag.py
======================================================================
Тестирование:
1. MediaRetentionManager (TTL 30 дней, удаление temp_cache, архивация в zip).
2. Автоматическое сохранение итоговых промптов генерации фото в RAG.
3. Семантический поиск по истории визуальных стилей и промптов через RAG.
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import time
import asyncio
from PIL import Image

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from storage.media_retention import MediaRetentionManager
from core.orchestrator import UnifiedOrchestrator


def setup_dummy_old_and_new_files():
    """Создает тестовые файлы с искусственно заниженным mtime (35 дней назад) и свежие файлы."""
    output_dir = os.path.join(AI_ROOT, "output")
    temp_dir = os.path.join(output_dir, "temp_cache")
    photos_dir = os.path.join(output_dir, "photos")
    
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(photos_dir, exist_ok=True)

    now = time.time()
    old_time = now - (35 * 86400) # 35 дней назад

    # 1. Устаревший файл в temp_cache (должен быть удален)
    old_temp_file = os.path.join(temp_dir, "old_test_temp_35d.jpg")
    img = Image.new("RGB", (50, 50), color=(100, 100, 100))
    img.save(old_temp_file)
    os.utime(old_temp_file, (old_time, old_time))

    # 2. Свежий файл в temp_cache (должен остаться)
    new_temp_file = os.path.join(temp_dir, "new_test_temp_fresh.jpg")
    img.save(new_temp_file)

    # 3. Устаревшее фото в photos (должно быть заархивировано)
    old_photo_file = os.path.join(photos_dir, "old_test_photo_35d.jpg")
    img_photo = Image.new("RGB", (60, 60), color=(200, 50, 50))
    img_photo.save(old_photo_file)
    os.utime(old_photo_file, (old_time, old_time))

    return old_temp_file, new_temp_file, old_photo_file


async def run_retention_and_prompt_rag_test():
    print("=" * 80)
    print("📦 ТЕСТ УПРАВЛЕНИЯ ХРАНЕНИЕМ МЕДИА (30 ДНЕЙ TTL) И RAG-ПАМЯТИ ПРОМПТОВ")
    print("=" * 80)

    # -------------------------------------------------------------
    # ТЕСТ 1: РОТАЦИЯ И ОЧИСТКА ФАЙЛОВ (> 30 ДНЕЙ)
    # -------------------------------------------------------------
    print("\n--- [ТЕСТ 1] Очистка и архивация файлов старше 30 дней ---")
    old_temp, new_temp, old_photo = setup_dummy_old_and_new_files()
    
    cleaner = MediaRetentionManager()
    cleanup_res = cleaner.cleanup_expired_files(retention_days=30, archive_generations=True)
    
    print(f"📊 Результат очистки: {cleanup_res}")
    
    # Проверки
    assert not os.path.exists(old_temp), "Ошибка: старый файл из temp_cache не удален!"
    assert os.path.exists(new_temp), "Ошибка: свежий файл из temp_cache был ошибочно удален!"
    assert not os.path.exists(old_photo), "Ошибка: старое фото не удалено после архивации!"
    
    # Проверяем наличие zip архива
    archive_dir = os.path.join(AI_ROOT, "output", "archive")
    zip_files = [f for f in os.listdir(archive_dir) if f.endswith(".zip")]
    print(f"📦 Найдены архивы в {archive_dir}: {zip_files}")
    assert len(zip_files) > 0, "Ошибка: zip-архив не создан!"

    # Очистка тестового свежего файла
    if os.path.exists(new_temp):
        os.remove(new_temp)

    # -------------------------------------------------------------
    # ТЕСТ 2: ГЕНЕРАЦИЯ ПОСТА С СОХРАНЕНИЕМ ПРОМПТА ФОТО В RAG
    # -------------------------------------------------------------
    print("\n--- [ТЕСТ 2] Генерация поста и авто-индексация промпта фото в RAG ---")
    orchestrator = UnifiedOrchestrator()
    
    company_name = "AutoLuxe Detailing"
    niche = "Премиальный детейлинг авто"
    test_prompt = "Керамическая полировка кузова и защита от сколов"

    gen_res = await orchestrator.execute_task(
        task_type="generate_post",
        user_data={
            "company_name": company_name,
            "niche": niche,
            "prompt": test_prompt,
            "generate_image": True,
            "brand_colors": ["#1A1A1A", "#E63946", "#F1FAEE"]
        },
        session_id="sess_prompt_rag_test"
    )

    assert gen_res.get("status") == "success"
    print(f"✅ Пост и фото сгенерированы! Image: {gen_res.get('photo_path')}")

    # -------------------------------------------------------------
    # ТЕСТ 3: ПОИСК В RAG ПО ИСТОРИИ ПРОМПТОВ
    # -------------------------------------------------------------
    print("\n--- [ТЕСТ 3] Семантический поиск по RAG-памяти промптов фото ---")
    rag_search = await orchestrator.rag.query_async(f"промпт фото стиль свет {company_name} полировка")
    print(f"📚 Найдено чанков: {len(rag_search.chunks)}, Score: {rag_search.top_score:.2f}")
    print(f"   Фрагмент сохраненного промпта:\n{rag_search.formatted_context[:250]}...")

    assert len(rag_search.chunks) > 0, "Ошибка: промпт фото не найден в RAG базе!"
    assert company_name in rag_search.formatted_context
    assert "ComfyUI" in rag_search.formatted_context or "промпт" in rag_search.formatted_context.lower()

    print("\n" + "=" * 80)
    print("🎉 ВСЕ ТЕСТЫ ХРАНЕНИЯ МЕДИА И RAG-ПАМЯТИ ПРОМПТОВ УСПЕШНО ПРОЙДЕНЫ!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_retention_and_prompt_rag_test())
