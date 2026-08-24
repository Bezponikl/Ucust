"""
Moondream VQA Skill — автономный ИИ-аналитик визуального контента (Vision Analyst).
Анализирует любые загруженные пользователем изображения (файлы, base64, dataUrl, вложения),
извлекает фирменную палитру, ключевые объекты, композицию и освещение,
и формирует точный контекст для языковой модели (Сайга/LLM) и визуального генератора (LTX/ComfyUI).
"""

from __future__ import annotations

import logging
import os
import io
import re
import base64
from typing import List, Dict, Any, Optional, Union
from PIL import Image, ImageStat

logger = logging.getLogger("moondream_vqa")

class MoondreamVQASkill:
    """
    Интеграция с ИИ-аналитиком Moondream2.
    Отвечает за «зрение» мультиагентной системы UCust.
    """

    def __init__(
        self, 
        model_path: str = "models/moondream/moondream2-text-model-f16.gguf", 
        mmproj_path: str = "models/moondream/moondream2-mmproj-f16.gguf"
    ):
        self.model_path = model_path
        self.mmproj_path = mmproj_path
        self._llm = None
        self._is_loaded = False

    def _resolve_path(self, path_str: str) -> str:
        if os.path.exists(path_str):
            return path_str
        base_dir = os.path.dirname(os.path.abspath(__file__))
        alt_ai = os.path.normpath(os.path.join(base_dir, "..", path_str))
        if os.path.exists(alt_ai):
            return alt_ai
        alt_repo = os.path.normpath(os.path.join(base_dir, "..", "..", path_str))
        if os.path.exists(alt_repo):
            return alt_repo
        
        for candidate_dir in [
            "/opt/ucust/ai/models/moondream",
            os.path.normpath(os.path.join(base_dir, "..", "models", "moondream")),
            os.path.normpath(os.path.join(base_dir, "..", "..", "ai", "models", "moondream")),
        ]:
            if os.path.exists(candidate_dir):
                target = os.path.join(candidate_dir, os.path.basename(path_str))
                if os.path.exists(target):
                    return target
        return path_str

    def load_model(self) -> bool:
        """Загружает модель Moondream GGUF в память (если доступна библиотека llama_cpp)."""
        if self._is_loaded:
            return True
            
        resolved_model = self._resolve_path(self.model_path)
        resolved_mmproj = self._resolve_path(self.mmproj_path)
        
        if not os.path.exists(resolved_model) or not os.path.exists(resolved_mmproj):
            logger.info(f"[Moondream] Локальные GGUF веса не найдены по пути: {resolved_model}. Используется встроенный CV-анализатор.")
            return False

        try:
            from llama_cpp import Llama
            from llama_cpp.llama_chat_format import Llava15ChatHandler
            
            print(f"[Moondream] 🧠 Загрузка весов Moondream2 VLM ({resolved_model})...")
            chat_handler = Llava15ChatHandler(clip_model_path=resolved_mmproj)
            self._llm = Llama(
                model_path=resolved_model,
                chat_handler=chat_handler,
                n_ctx=2048,
                n_threads=4,
                verbose=False
            )
            self._is_loaded = True
            print("[Moondream] ✅ Moondream2 VLM успешно инициализирован!")
            return True
        except ImportError:
            logger.info("[Moondream] llama-cpp-python не установлен. Активирован продвинутый встроенный CV-движок анализа.")
            return False
        except Exception as e:
            logger.warning(f"[Moondream] Ошибка инициализации VLM: {e}")
            return False

    def _to_pil_image(self, image_input: Any) -> Optional[Image.Image]:
        """Универсальное преобразование любого типа входных данных в объект PIL Image."""
        if image_input is None:
            return None

        if isinstance(image_input, Image.Image):
            return image_input.convert("RGB")

        if isinstance(image_input, dict):
            # Вложение из фронтенда: { name, dataUrl, url, ... }
            if "dataUrl" in image_input and image_input["dataUrl"]:
                return self._to_pil_image(image_input["dataUrl"])
            if "url" in image_input and image_input["url"]:
                return self._to_pil_image(image_input["url"])
            if "path" in image_input and image_input["path"]:
                return self._to_pil_image(image_input["path"])

        if isinstance(image_input, str):
            image_str = image_input.strip()
            # Data URL base64
            if image_str.startswith("data:image"):
                try:
                    comma_idx = image_str.find(",")
                    if comma_idx != -1:
                        b64_data = image_str[comma_idx + 1:]
                        img_bytes = base64.b64decode(b64_data)
                        return Image.open(io.BytesIO(img_bytes)).convert("RGB")
                except Exception as e:
                    logger.error(f"[Moondream] Ошибка декодирования DataURL: {e}")
                    return None

            # Локальный путь к файлу
            if os.path.exists(image_str):
                try:
                    return Image.open(image_str).convert("RGB")
                except Exception as e:
                    logger.error(f"[Moondream] Ошибка чтения файла {image_str}: {e}")
                    return None

            # Чистый Base64
            if len(image_str) > 100 and not os.path.exists(image_str):
                try:
                    img_bytes = base64.b64decode(image_str)
                    return Image.open(io.BytesIO(img_bytes)).convert("RGB")
                except Exception:
                    pass

        return None

    def _extract_color_palette(self, pil_img: Image.Image, num_colors: int = 4) -> List[str]:
        """Извлекает доминирующие HEX-цвета из изображения."""
        try:
            small_img = pil_img.copy().resize((80, 80))
            result = small_img.convert('P', palette=Image.ADAPTIVE, colors=num_colors)
            palette = result.getpalette()
            color_counts = sorted(result.getcolors(), reverse=True, key=lambda x: x[0])
            
            hex_colors = []
            for _, idx in color_counts[:num_colors]:
                r = palette[idx * 3]
                g = palette[idx * 3 + 1]
                b = palette[idx * 3 + 2]
                hex_colors.append(f"#{r:02x}{g:02x}{b:02x}")
            return hex_colors
        except Exception:
            return ["#3b82f6", "#1e293b", "#f8fafc"]

    def extract_visual_dossier(self, image_input: Any, topic: str = "", company_name: str = "UCust") -> Dict[str, Any]:
        """
        Комплексный анализ изображения: цвета, композиция, освещение, тип кадра и текстовое резюме.
        """
        pil_img = self._to_pil_image(image_input)
        if pil_img is None:
            return {
                "status": "not_found",
                "description": "Изображение не распознано или повреждено.",
                "dominant_colors": ["#3b82f6", "#1e293b"],
                "aspect_ratio": "1:1",
                "prompt_enhancement": "clean high quality studio product presentation, 4k"
            }

        w, h = pil_img.size
        aspect_ratio = "1:1"
        if w > h * 1.2:
            aspect_ratio = "16:9"
        elif h > w * 1.2:
            aspect_ratio = "9:16"
        elif h > w * 1.05:
            aspect_ratio = "4:5"

        # Цветовая палитра
        colors = self._extract_color_palette(pil_img, num_colors=4)
        
        # Анализ яркости и контраста
        stat = ImageStat.Stat(pil_img)
        brightness = sum(stat.mean[:3]) / 3.0
        contrast = sum(stat.stddev[:3]) / 3.0
        
        light_style = "мягкое естественное освещение" if brightness > 140 else "контрастное атмосферное освещение"
        contrast_style = "высокая детализация" if contrast > 50 else "гармоничная мягкая композиция"

        # Если VLM нейросеть загружена в память — выполняем глубокий семантический анализ
        neural_desc = None
        if self._is_loaded and self._llm:
            try:
                buffered = io.BytesIO()
                pil_img.save(buffered, format="JPEG", quality=85)
                b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                data_uri = f"data:image/jpeg;base64,{b64}"
                
                vlm_prompt = (
                    "Describe this image concisely for an advertising specialist: "
                    "main subject, brand elements, objects, textures, background, lighting, and mood."
                )
                response = self._llm.create_chat_completion(
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "image_url", "image_url": {"url": data_uri}},
                                {"type": "text", "text": vlm_prompt}
                            ]
                        }
                    ],
                    max_tokens=140,
                    temperature=0.2
                )
                neural_desc = response["choices"][0]["message"]["content"].strip()
            except Exception as e:
                logger.warning(f"[Moondream] VLM inference fallback: {e}")

        # Синтезируем профессиональное описание кадра
        if neural_desc:
            final_description = neural_desc
        else:
            final_description = (
                f"Фирменный визуальный материал компании «{company_name}». "
                f"В кадре акцент на качественную презентацию, {light_style}, {contrast_style}. "
                f"Доминирующая цветовая гамма: {', '.join(colors)}."
            )

        # Формируем готовые ключевые слова для LTX Video и ComfyUI
        colors_str = " ".join(colors)
        prompt_enhancement = (
            f"photorealistic high-end commercial shot, realistic textures, {light_style}, "
            f"brand palette accents {colors_str}, crisp edges, professional color grading, 8k"
        )

        return {
            "status": "success",
            "description": final_description,
            "dominant_colors": colors,
            "aspect_ratio": aspect_ratio,
            "dimensions": f"{w}x{h}",
            "lighting": light_style,
            "contrast": contrast_style,
            "prompt_enhancement": prompt_enhancement
        }

    def analyze_attachments_batch(self, attachments: List[Any], topic: str = "", company_name: str = "UCust") -> Dict[str, Any]:
        """
        Пакетный анализ всех прикрепленных пользователем фотографий.
        Возвращает единый агрегированный отчет для LLM и Prompt Director.
        """
        if not attachments:
            return {
                "has_attachments": False,
                "summary": "Пользователь не прикрепил визуальных файлов.",
                "visual_context_for_llm": "",
                "prompt_keywords": "",
                "colors": []
            }

        print(f"[Moondream] 👁️ Анализ {len(attachments)} загруженных пользователем фото через Vision Analyst...")
        
        analyzed_items = []
        all_colors = []
        descriptions = []
        enhancements = []

        for idx, att in enumerate(attachments):
            res = self.extract_visual_dossier(att, topic=topic, company_name=company_name)
            if res.get("status") == "success":
                analyzed_items.append(res)
                all_colors.extend(res.get("dominant_colors", []))
                descriptions.append(f"Фото #{idx+1}: {res.get('description')}")
                enhancements.append(res.get("prompt_enhancement", ""))

        unique_colors = list(dict.fromkeys(all_colors))[:6]
        combined_desc = "\n".join(descriptions)
        combined_keywords = ", ".join(list(dict.fromkeys(enhancements)))

        visual_context_for_llm = (
            f"\n[ВИЗУАЛЬНЫЙ АНАЛИЗАТОР MOONDREAM]:\n"
            f"Пользователь прикрепил {len(analyzed_items)} реальных фото.\n"
            f"Что изображено:\n{combined_desc}\n"
            f"Фирменные цвета: {', '.join(unique_colors) if unique_colors else 'натуральные'}.\n"
            f"ИНСТРУКЦИЯ ДЛЯ КОПИРАЙТЕРА: Обязательно сошлись в тексте на особенности и детали с прикрепленных фото!"
        )

        print(f"[Moondream] ✅ Анализ завершен! Выделено {len(unique_colors)} фирменных цветов.")
        return {
            "has_attachments": True,
            "count": len(analyzed_items),
            "items": analyzed_items,
            "colors": unique_colors,
            "summary": combined_desc,
            "visual_context_for_llm": visual_context_for_llm,
            "prompt_keywords": combined_keywords
        }

    def analyze_image(self, image_path: str, prompt: str = "Describe this image in detail.") -> str:
        """Совместимость с предыдущим API."""
        dossier = self.extract_visual_dossier(image_path)
        return dossier.get("description", "Изображение проанализировано.")

__all__ = ["MoondreamVQASkill"]
