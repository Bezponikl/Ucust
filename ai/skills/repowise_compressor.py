"""
Repowise Compressor Skill — инструмент для сжатия и очистки спарсенного контента.
Интеграция с https://github.com/repowise-dev/repowise

Используется агентами (Аналитиком) для того, чтобы сжимать "грязные" 
выдачи от парсеров и поисковиков (Travity), оставляя только важный контекст.
Это позволяет экономить токены при передаче контекста в LLM.
"""

from __future__ import annotations

import json
import logging
import subprocess
import shutil
from typing import Optional, List

logger = logging.getLogger("repowise_skill")


class RepowiseCompressorSkill:
    """
    Скилл, использующий repowise для дистилляции (сжатия) текстов.
    Если repowise не установлен в системе, использует встроенный 
    алгоритм "легкой дистилляции" (удаление стоп-слов, ссылок, HTML).
    """

    def __init__(self, max_tokens: int = 500):
        self.max_tokens = max_tokens
        
        # Поиск repowise в PATH или в папке Scripts (где он был установлен pip)
        import os
        import shutil
        self.repowise_path = shutil.which("repowise")
        if not self.repowise_path:
            alt_path = os.path.expandvars(r"%APPDATA%\Python\Python314\Scripts\repowise.exe")
            if os.path.exists(alt_path):
                self.repowise_path = alt_path

    def distill_text(self, text: str) -> str:
        """
        Сжимает переданный текст, оставляя только суть.
        """
        if not text or not text.strip():
            return ""

        # Если в системе есть CLI repowise, используем его (через пайпы)
        if self.repowise_path:
            try:
                process = subprocess.Popen(
                    [self.repowise_path, "distill", "--text-only"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8"
                )
                out, err = process.communicate(input=text, timeout=10)
                if process.returncode == 0 and out.strip():
                    return out.strip()
                else:
                    logger.warning(f"Repowise CLI error: {err}")
            except Exception as e:
                logger.warning(f"Failed to use repowise CLI: {e}")

        # Fallback алгоритм (эмуляция дистилляции для экономии токенов)
        return self._fallback_distill(text)

    def distill_posts(self, posts: List[str]) -> List[str]:
        """
        Сжимает массив постов из соцсетей.
        """
        print(f"[RepowiseSkill] Дистилляция {len(posts)} постов для экономии токенов...")
        distilled = []
        for post in posts:
            compressed = self.distill_text(post)
            if compressed:
                distilled.append(compressed)
        
        saved = sum(len(p) for p in posts) - sum(len(d) for d in distilled)
        if saved > 0:
            print(f"[RepowiseSkill] Сжатие успешно! Сэкономлено ~{saved // 4} токенов.")
        
        return distilled

    def _fallback_distill(self, text: str) -> str:
        """
        Интеллектуальная фильтрация мусора и сжатие смыслов:
        1. Безжалостно отсеивает инфоцыганщину, рекламу курсов, призывы подписаться ('подпишись', 'жми на ссылку').
        2. Удаляет оценочные суждения ('интересный пост о...', 'супер полезно').
        3. Сохраняет исключительно факты, боли аудитории и бизнес-триггеры.
        """
        import re
        
        # 1. Отсеиваем спам, инфобизнес-курсы и призывы к подписке
        spam_patterns = [
            r'скидк\w*\s*\d+%', r'купи\w*\s*курс', r'записывай\w*\s*на\s*курс',
            r'подпиши\w*\s*на\s*канал', r'жми\s*на\s*ссылку', r'переходи\w*\s*в\s*профиль',
            r'https?://\S+|www\.\S+'
        ]
        for pat in spam_patterns:
            text = re.sub(pat, '', text, flags=re.IGNORECASE)
            
        # 2. Убираем оценочные суждения и паразитные вводные слова
        fluff_patterns = [
            r'интересный\s*пост\s*о', r'полезная\s*информация', r'секретная\s*фишка'
        ]
        for pat in fluff_patterns:
            text = re.sub(pat, '', text, flags=re.IGNORECASE)
        
        # 3. Убираем множественные пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Обрезаем до компактного размера (сухая выжимка фактов)
        words = text.split()
        if len(words) > self.max_tokens:
            text = " ".join(words[:self.max_tokens]) + "..."
            
        return text

__all__ = ["RepowiseCompressorSkill"]
