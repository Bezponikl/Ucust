"""
1. Data Ingestion & Sanitization
Очистка сырого текста от спама, рекламы, избыточных ссылок и эмодзи.
Семантическое разбиение на чанки (300-400 токенов, overlap 50 токенов).
"""

import re
import uuid
from typing import List, Dict, Any, Optional
from rag.models import Document, Chunk

class TextSanitizer:
    """
    Модуль очистки входных текстов от спама, инфоцыганщины,
    рекламных хвостов, мусорных URL и избыточных эмодзи.
    """
    
    # Стоп-паттерны спама и рекламы
    SPAM_PATTERNS = [
        r'(?i)скидк\w*\s*(?:до\s*)?\d+%',
        r'(?i)купи\w*\s*(?:прямо\s*сейчас|курс|вебинар)',
        r'(?i)записывай\w*\s*(?:на\s*бесплатный\s*курс|на\s*вебинар)',
        r'(?i)подпиши\w*\s*на\s*(?:наш\s*)?(?:канал|паблик|группу)',
        r'(?i)переходи\w*\s*(?:по\s*ссылке|в\s*шапку\s*профиля|в\s*описание)',
        r'(?i)жми\s*на\s*ссылку',
        r'(?i)успей\s*(?:забрать|купить|оплатить)',
        r'(?i)только\s*сегодня\s*(?:цена|бонус)',
        r'(?i)http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        r'(?i)t\.me/\S+',
        r'(?i)vk\.com/\S+'
    ]
    
    # Регулярка для фильтрации повторяющихся эмодзи (более 2 подряд)
    EMOJI_FLOOD_REGEX = re.compile(
        r'([\U00010000-\U0010ffff\u2600-\u26FF\u2700-\u27BF])\s*\1{2,}',
        re.UNICODE
    )

    @classmethod
    def sanitize(cls, raw_text: str) -> str:
        """
        Полная очистка текста от шума с сохранением фактуры и смысла.
        """
        if not raw_text or not raw_text.strip():
            return ""
            
        text = raw_text
        
        # 1. Удаление спам-шаблонов и ссылок
        for pattern in cls.SPAM_PATTERNS:
            text = re.sub(pattern, ' ', text)
            
        # 2. Ограничение эмодзи-флуда (оставляем максимум 1 эмодзи подряд)
        text = cls.EMOJI_FLOOD_REGEX.sub(r'\1', text)
        
        # 3. Нормализация кавычек и длинных тире (типографика)
        text = text.replace("—", "-").replace("–", "-")
        text = text.replace("«", '"').replace("»", '"')
        
        # 4. Нормализация пробелов и переносов строк
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        return text.strip()


class SemanticChunker:
    """
    Семантическое деление текста на смысловые блоки.
    Разбивает по границам параграфов, списков и предложений,
    выдерживая целевой размер в 300–400 токенов и overlap в 50 токенов.
    """
    
    def __init__(self, target_chunk_tokens: int = 350, overlap_tokens: int = 50):
        self.target_chunk_tokens = target_chunk_tokens
        self.overlap_tokens = overlap_tokens
        
    @staticmethod
    def _approx_token_count(text: str) -> int:
        """
        Быстрая эвристическая оценка токенов для русского/английского языков:
        ~1 слово = ~1.3 токена для кириллицы BPE.
        """
        words = text.split()
        return int(len(words) * 1.3)

    def chunk_document(self, document: Document) -> List[Chunk]:
        """
        Делит документ на семантические чанки с метаданными.
        """
        cleaned_text = TextSanitizer.sanitize(document.text)
        if not cleaned_text:
            return []
            
        # 1. Деление на смысловые параграфы и блоки
        raw_paragraphs = [p.strip() for p in cleaned_text.split("\n\n") if p.strip()]
        
        # Если текст без двойных переносов, делим по точкам/вопросам
        if len(raw_paragraphs) <= 1:
            raw_paragraphs = [s.strip() for s in re.split(r'(?<=[.!?])\s+', cleaned_text) if s.strip()]

        chunks: List[Chunk] = []
        current_block: List[str] = []
        current_token_count = 0
        chunk_idx = 0
        
        for para in raw_paragraphs:
            para_tokens = self._approx_token_count(para)
            
            # Если добавление параграфа превышает лимит чанка
            if current_token_count + para_tokens > self.target_chunk_tokens and current_block:
                chunk_text = " ".join(current_block)
                chunks.append(
                    Chunk(
                        chunk_id=f"{document.doc_id}_chunk_{chunk_idx}",
                        doc_id=document.doc_id,
                        text=chunk_text,
                        token_count=current_token_count,
                        metadata={**document.metadata, "chunk_index": chunk_idx},
                        source=document.source,
                        created_at=document.created_at
                    )
                )
                chunk_idx += 1
                
                # Создаем overlap (перекрытие) из последних предложений текущего блока
                overlap_block = []
                overlap_count = 0
                for item in reversed(current_block):
                    item_tok = self._approx_token_count(item)
                    if overlap_count + item_tok <= self.overlap_tokens:
                        overlap_block.insert(0, item)
                        overlap_count += item_tok
                    else:
                        break
                        
                current_block = overlap_block
                current_token_count = overlap_count
                
            current_block.append(para)
            current_token_count += para_tokens
            
        # Добавляем финальный оставшийся чанк
        if current_block:
            chunk_text = " ".join(current_block)
            chunks.append(
                Chunk(
                    chunk_id=f"{document.doc_id}_chunk_{chunk_idx}",
                    doc_id=document.doc_id,
                    text=chunk_text,
                    token_count=current_token_count,
                    metadata={**document.metadata, "chunk_index": chunk_idx},
                    source=document.source,
                    created_at=document.created_at
                )
            )
            
        return chunks
