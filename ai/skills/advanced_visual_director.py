import os
import asyncio
import time
from typing import List
from skills.media_utils import MediaUtils
from core.resource_manager import ResourceManager

class AdvancedVisualDirector:
    """
    Автономный ИИ-режиссер.
    - Динамический Prompt Engineering
    - Рендеринг микро-сценами (защита от OOM)
    - Self-Healing QA через Moondream
    """
    
    def __init__(self, brand_images: List[str]):
        self.brand_images = brand_images
        self.brand_colors = []
        
        # 1. Извлекаем цвета для Брендбука (Control Brandbook)
        if self.brand_images:
            colors = MediaUtils.extract_dominant_colors(self.brand_images[0])
            self.brand_colors = colors
            print(f"[AdvancedVisualDirector] 🎨 ИИ-Брендбук загружен. Фирменные цвета: {self.brand_colors}")

    def create_cinematic_prompts(self, saiga_tone: dict, saiga_storyboard: list) -> List[dict]:
        """
        Собирает финальные комплексные промпты (Positive, Negative, Audio) 
        строго по официальному стандарту LTX-2: единый связный нарративный абзац 
        с описанием масштаба кадра, движения камеры, освещения, действия и русской речи в кавычках.
        """
        print(f"[AdvancedVisualDirector] 🎬 Сборка промптов по стандарту LTX-2 для {len(saiga_storyboard)} сцен...")
        
        script_chunks = []
        brand_colors_str = " ".join(self.brand_colors) if self.brand_colors else "neutral modern tones"
        
        for i, scene in enumerate(saiga_storyboard):
            shot_type = scene.get("shot_type", "Cinematic medium shot")
            scene_desc = scene.get("scene_description", "")
            style = scene.get("style_markers", "Cinematic realism")
            neg = scene.get("negative_prompt", "low quality, distorted anatomy, blur, artifacts")
            audio = scene.get("audio", {})
            
            # --- POSITIVE PROMPT (Единый кинематографичный абзац LTX-2) ---
            video_prompt = (
                f"{shot_type}. {scene_desc} "
                f"Natural facial micro-expressions, subtle relaxed movement. "
                f"Style: {style}. Brand color palette accents: {brand_colors_str}. "
                f"Cinematic quality, 4k resolution, photorealistic textures."
            )
            
            # --- NEGATIVE PROMPT ---
            negative_prompt = (
                f"{neg}, wooden talking head, stiff facial expressions, robotic lifeless stare, "
                f"frozen eyes, unmoving neck, wrong colors, avoid colors not matching {brand_colors_str}, "
                f"ugly, malformed, extra limbs, bad proportions, flicker, glitch"
            )
            
            # --- AUDIO PROMPT (Ambient + Русская речь) ---
            ambient_sound = audio.get("ambient", "")
            dialogue_line = audio.get("dialogue", "")
            audio_prompt = f"Ambient: {ambient_sound}. Dialogue: {dialogue_line}"
            
            script_chunks.append({
                "video_prompt": video_prompt,
                "negative_prompt": negative_prompt,
                "audio_prompt": audio_prompt
            })
                
        print(f"[AdvancedVisualDirector] 🎬 Готово! Сформировано {len(script_chunks)} профессиональных LTX-2 промптов.")
        return script_chunks

    async def _mock_ltx_video_generate(self, video_prompt: str, negative_prompt: str, audio_prompt: str, chunk_index: int, output_path: str):
        """Мок рендера LTX-Video."""
        print(f"[LTX-Video] ⏳ Рендеринг сцены {chunk_index+1} (2 сек) на GPU...")
        print(f"  > 🟢 Positive: {video_prompt[:80]}...")
        print(f"  > 🔴 Negative: {negative_prompt[:80]}...")
        print(f"  > 🔊 Audio:    {audio_prompt[:80]}...")
        await asyncio.sleep(2)
        with open(output_path, "w") as f:
            f.write("mock video content")
        print(f"[LTX-Video] ✅ Сцена {chunk_index+1} готова: {output_path}")

    async def generate_and_qa_video(self, prompts: List[dict], final_output: str):
        """
        Основной цикл генерации с защитой OOM и QA-проверками.
        """
        ResourceManager.enforce_gpu_priority_for_ai()
        
        chunk_paths = []
        os.makedirs("temp_media", exist_ok=True)
        
        for i, scene_data in enumerate(prompts):
            success = False
            attempts = 0
            chunk_path = f"temp_media/chunk_{i}.mp4"
            qa_frame_path = f"temp_media/qa_frame_{i}.jpg"
            
            while not success and attempts < 2:
                attempts += 1
                print(f"\n[AdvancedVisualDirector] 🎥 Съемка дубля {attempts} для сцены {i+1}...")
                
                # 1. Генерация
                await self._mock_ltx_video_generate(
                    scene_data["video_prompt"], 
                    scene_data["negative_prompt"], 
                    scene_data["audio_prompt"], 
                    i, 
                    chunk_path
                )
                
                # 2. Очистка видеопамяти (Только если мы на слабом локальном ПК)
                is_server_mode = os.getenv("SERVER_MODE", "false").lower() == "true"
                if not is_server_mode:
                    try:
                        import torch
                        torch.cuda.empty_cache()
                        import gc
                        gc.collect()
                        print("[AdvancedVisualDirector] 🧹 VRAM агрессивно очищена (Локальный режим).")
                    except ImportError:
                        print("[AdvancedVisualDirector] 🧹 (torch не установлен, пропускаем очистку)")
                else:
                    print("[AdvancedVisualDirector] 🚀 Server Mode: Модель остается в VRAM для максимальной скорости.")
                
                # 3. Извлечение кадра для QA
                # В моковом варианте ffmpeg упадет на текстовом файле, 
                # поэтому мы симулируем извлечение кадра.
                print(f"[AdvancedVisualDirector] 🔍 Извлечение кадра из {chunk_path} для QA...")
                with open(qa_frame_path, "w") as f:
                    f.write("mock image")
                
                # 4. Self-Healing QA (Moondream Check)
                print(f"[Moondream2] 🤖 Строгий QA контроль кадра {qa_frame_path}: руки, физика, вывески...")
                await asyncio.sleep(1)
                
                # Эмуляция обнаружения бага на первом дубле второй сцены
                if i == 1 and attempts == 1:
                    penalty_tag = "severe penalty: unnatural physics, warped hands, distorted signage text"
                    scene_data["negative_prompt"] += f", {penalty_tag}"
                    print(f"[Moondream2] ❌ ОБНАРУЖЕН ДЕФЕКТ: Аномалия анатомии и неестественная физика движения.")
                    print(f"[Moondream2] 🏷️ Добавлен штрафной тег в Negative Prompt: '{penalty_tag}'")
                    print(f"[AdvancedVisualDirector] 🔄 Перезапуск генерации дубля 2 для сцены {i+1} с обновленным негативом...")
                else:
                    print(f"[Moondream2] ✅ Кадр чистый. Артефактов рук и физики не обнаружено.")
                    success = True
                    chunk_paths.append(chunk_path)
                    
        # 5. Склейка всех чанков на CPU
        print("\n[AdvancedVisualDirector] 🎞️ Склейка микро-сцен в итоговый ролик...")
        ResourceManager.enforce_cpu_for_parsers()
        
        # Симулируем успешную работу ffmpeg для невалидных видео-файлов (переписывая просто текст)
        with open(final_output, "w") as f:
            f.write("final combined video")
        print(f"[AdvancedVisualDirector] 🎉 Финальное видео успешно собрано: {final_output}")
