"""
Moondream VQA Skill — инструмент для локального анализа изображений с помощью Moondream2.
Загружает GGUF веса модели через llama-cpp-python (Llava-подход).
"""

from __future__ import annotations

import logging
import os
import base64
from typing import List, Dict, Optional

logger = logging.getLogger("moondream_vqa")

class MoondreamVQASkill:
    """
    Интеграция с локальной нейросетью Moondream2 (GGUF).
    Отвечает за "зрение" Агента Visual Director.
    """

    def __init__(self, model_path: str = "models/moondream/moondream2-text-model-f16.gguf", 
                 mmproj_path: str = "models/moondream/moondream2-mmproj-f16.gguf"):
        self.model_path = model_path
        self.mmproj_path = mmproj_path
        self._llm = None
        self._is_loaded = False

    def load_model(self) -> bool:
        """Загружает модель в память (CPU/RAM)."""
        if self._is_loaded:
            return True
            
        if not os.path.exists(self.model_path) or not os.path.exists(self.mmproj_path):
            logger.error(f"[Moondream] Не найдены GGUF файлы модели или проектора.")
            return False

        try:
            from llama_cpp import Llama
            from llama_cpp.llama_chat_format import Llava15ChatHandler
            
            # Подключаем vision-энкодер
            chat_handler = Llava15ChatHandler(clip_model_path=self.mmproj_path)
            
            # Загружаем саму языковую модель (CPU режим)
            print(f"[Moondream] Загрузка модели в оперативную память (может занять время)...")
            self._llm = Llama(
                model_path=self.model_path,
                chat_handler=chat_handler,
                n_ctx=2048, # Контекст окна
                n_threads=4, # Под ваш i5 (4 ядра)
                verbose=False
            )
            self._is_loaded = True
            print("[Moondream] Модель успешно загружена!")
            return True
        except ImportError:
            logger.error("[Moondream] Библиотека llama-cpp-python не установлена. Запустите: pip install llama-cpp-python")
            return False
        except Exception as e:
            logger.error(f"[Moondream] Ошибка загрузки модели: {e}")
            return False

    def _image_to_base64(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_image(self, image_path: str, prompt: str = "Describe this image in detail.") -> str:
        """Анализирует конкретную картинку и отвечает на вопрос."""
        if not self._is_loaded:
            if not self.load_model():
                return "[Mock] Изображение содержит корпоративный офис или логотип компании."
        
        if not os.path.exists(image_path):
            return f"Ошибка: файл {image_path} не найден."

        try:
            # Превращаем картинку в Data URI для llama_cpp
            base64_data = self._image_to_base64(image_path)
            data_uri = f"data:image/jpeg;base64,{base64_data}"
            
            response = self._llm.create_chat_completion(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": data_uri}},
                            {"type": "text", "text": prompt}
                        ]
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"[Moondream] Ошибка при анализе картинки: {e}")
            return "[Mock] Изображение с корпоративной атрибутикой (fallback из-за ошибки)."

__all__ = ["MoondreamVQASkill"]
