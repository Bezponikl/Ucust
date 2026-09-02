# File: skills/tech_sanitizer.py
"""
Tech Model & Internal Architecture Sanitizer for UCust.AI.
Строго запрещает упоминание названий внутренних моделей, фреймворков и библиотек
(Saiga, Сайга, Moondream, FLUX, LTX, ComfyUI, RAG, Llama, Ollama, RabbitMQ).
Автоматически заменяет их на продуктовые и маркетинговые термины (возможности, а не названия).
"""

from __future__ import annotations

import re
from typing import Dict, List, Pattern, Tuple


class TechSanitizer:
    """
    Фильтр защиты от утечек названий технологий и внутренних моделей.
    """

    # Словарь строгой замены названий моделей на продуктовые возможности
    REPLACEMENTS: List[Tuple[Pattern, str]] = [
        (re.compile(r'\b(сайг[а-яё]*|saiga)\b', re.IGNORECASE), "ИИ-копирайтер"),
        (re.compile(r'\b(moondream|мундрим)\b', re.IGNORECASE), "компьютерное зрение"),
        (re.compile(r'\b(flux(?:\.1)?(?:-dev|-schnell)?|флакс)\b', re.IGNORECASE), "генератор студийных фото"),
        (re.compile(r'\b(ltx(?:-video)?|лтх)\b', re.IGNORECASE), "генератор реалистичного видео"),
        (re.compile(r'\b(comfyui|комфи)\b', re.IGNORECASE), "AI-визуальная студия"),
        (re.compile(r'\b(llama|ллама)\b', re.IGNORECASE), "языковая нейромодель"),
        (re.compile(r'\b(rag|раг)\b', re.IGNORECASE), "база знаний бренда"),
        (re.compile(r'\b(gguf|ollama|оллама)\b', re.IGNORECASE), "нейросетевой движок"),
        (re.compile(r'\b(rabbitmq|amqp|amqps)\b', re.IGNORECASE), "очередь публикаций"),
        (re.compile(r'\b(telethon|vk_api)\b', re.IGNORECASE), "аналитический парсер"),
    ]

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """
        Очищает текст от любых прямых названий внутренних моделей и библиотек.
        """
        if not text:
            return ""
        
        sanitized = text
        for pattern, replacement in cls.REPLACEMENTS:
            sanitized = pattern.sub(replacement, sanitized)
            
        return sanitized
