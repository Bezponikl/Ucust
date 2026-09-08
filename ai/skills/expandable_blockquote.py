# -*- coding: utf-8 -*-
"""
модуль: expandable_blockquote.py
Форматирование и управление сворачиваемыми цитатами (Expandable Blockquotes)
для Telegram (Bot API 7.2+), Web / Mobile UI, HTML и MarkdownV2.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List, Optional, Tuple, Union


class ExpandableBlockquoteFormatter:
    """
    Универсальный форматер раскрывающихся цитат (Expandable Blockquote) для постов и контента:
    - Telegram HTML: <blockquote expandable>...</blockquote>
    - Telegram MarkdownV2: **>первая строка\n**>вторая строка
    - Web / Markdown: <details><summary>Заголовок</summary>...</details>
    - React UI DTO: структурированные блоки с метаданными.
    """

    PRICE_MARKERS = [
        r"прайс[- ]?лист", r"цены?:", r"стоимость", r"меню:", r"наши услуги", r"тарификац",
        r"\b\d+\s*(?:₽|руб|rub|\$|€)\b"
    ]
    
    TERMS_MARKERS = [
        r"услови[яе]\b", r"программ[аы]\s+лояльности", r"правил[ао]\b",
        r"как\s+(?:принять\s+участие|получить|заказать|принять)",
        r"механик[аи]\b", r"что\s+нужно\s+сделать:", r"бонусн[аяую]\b", r"скидочн[аяую]\b"
    ]

    FAQ_MARKERS = [
        r"f\.?a\.?q\.?", r"часто\s+задаваемые\s+вопросы", r"ответы\s+на\s+вопросы", r"вопрос[- ]ответ"
    ]

    RECIPE_MARKERS = [
        r"состав:", r"ингредиенты:", r"пошаговый\s+рецепт", r"способ\s+приготовления"
    ]

    DISCLAIMER_MARKERS = [
        r"имеются\s+противопоказания", r"дисклеймер:", r"юридическая\s+информация",
        r"не\s+является\s+публичной\s+офертой", r"важное\s+примечание:"
    ]

    @classmethod
    def wrap_html(cls, content: str, title: Optional[str] = None) -> str:
        """Оборачивает текст в официальный Telegram HTML тег <blockquote expandable>."""
        clean = content.strip()
        if not clean:
            return ""
        if title:
            title_clean = title.strip()
            if not title_clean.startswith("<b>") and not title_clean.startswith("<strong>"):
                body = f"<b>{title_clean}</b>\n{clean}"
            else:
                body = f"{title_clean}\n{clean}"
        else:
            body = clean
            
        return f"<blockquote expandable>\n{body}\n</blockquote>"

    @classmethod
    def wrap_markdown_v2(cls, content: str, title: Optional[str] = None) -> str:
        """
        Оборачивает текст в синтаксис Telegram MarkdownV2 для expandable blockquote:
        **>строка 1
        **>строка 2
        """
        clean = content.strip()
        if not clean:
            return ""
        
        full_text = f"*{title}*\n{clean}" if title else clean
        lines = full_text.splitlines()
        formatted_lines = [f"**>{line}" for line in lines]
        return "\n".join(formatted_lines)

    @classmethod
    def wrap_details(cls, content: str, summary: str = "Показать подробнее ▾") -> str:
        """Оборачивает текст в стандартный HTML5 <details><summary> для веб-интерфейса/React."""
        clean = content.strip()
        if not clean:
            return ""
        return f"<details>\n<summary>{summary}</summary>\n{clean}\n</details>"

    @classmethod
    def extract_blocks(cls, text: str) -> List[Dict[str, Any]]:
        """
        Извлекает все существующие expandable_blockquote из текста
        и возвращает структурированный список для фронтенда / аналитики.
        """
        if not text:
            return []
            
        blocks = []
        # 1. Поиск <blockquote expandable>
        html_pattern = re.compile(r"<blockquote\s+expandable>(.*?)</blockquote>", re.DOTALL | re.IGNORECASE)
        for idx, match in enumerate(html_pattern.finditer(text)):
            raw_inner = match.group(1).strip()
            # Извлекаем возможный заголовок
            title_match = re.search(r"^(?:<b>|<strong>)(.*?)(?:</b>|</strong>)", raw_inner, re.IGNORECASE)
            if title_match:
                title = title_match.group(1)
            else:
                first_line = raw_inner.splitlines()[0].strip() if raw_inner else ""
                title = first_line.rstrip(":") if first_line else f"Блок {idx + 1}"
                
            blocks.append({
                "index": idx,
                "type": "expandable_blockquote",
                "format": "html",
                "title": title,
                "content": raw_inner,
                "char_length": len(raw_inner)
            })

        # 2. Поиск **> в MarkdownV2
        md_lines = []
        in_md_block = False
        md_block_idx = len(blocks)
        for line in text.splitlines():
            if line.startswith("**>"):
                in_md_block = True
                md_lines.append(line[3:])
            else:
                if in_md_block and md_lines:
                    inner_md = "\n".join(md_lines).strip()
                    blocks.append({
                        "index": md_block_idx,
                        "type": "expandable_blockquote",
                        "format": "markdown_v2",
                        "title": inner_md.splitlines()[0] if inner_md else f"Блок {md_block_idx + 1}",
                        "content": inner_md,
                        "char_length": len(inner_md)
                    })
                    md_block_idx += 1
                    md_lines = []
                in_md_block = False
                
        if in_md_block and md_lines:
            inner_md = "\n".join(md_lines).strip()
            blocks.append({
                "index": md_block_idx,
                "type": "expandable_blockquote",
                "format": "markdown_v2",
                "title": inner_md.splitlines()[0] if inner_md else f"Блок {md_block_idx + 1}",
                "content": inner_md,
                "char_length": len(inner_md)
            })

        return blocks

    @classmethod
    def auto_wrap_sections(
        cls, 
        text: str, 
        mode: str = "html",
        targets: Optional[List[str]] = None,
        min_list_items: int = 2
    ) -> Tuple[str, int]:
        """
        Автоматически находит в тексте поста смысловые секции:
        - Прайсы / Меню / Цены услуг
        - Условия акций / конкурсов
        - FAQ / Вопросы и ответы
        - Ингредиенты / Состав
        - Дисклеймеры и противопоказания
        и аккуратно сворачивает их в <blockquote expandable>.

        Возвращает: (преобразованный_текст, количество_свернутых_блоков)
        """
        if not text:
            return "", 0

        # Если уже содержит теги цитат — не дублируем
        if "<blockquote" in text.lower() or "**>" in text:
            return text, 0

        selected_targets = targets or ["prices", "terms", "faq", "recipe", "disclaimer"]
        paragraphs = text.split("\n\n")
        wrapped_count = 0
        new_paragraphs = []

        for p in paragraphs:
            p_clean = p.strip()
            if not p_clean:
                continue

            p_lower = p_clean.lower()
            lines = [line.strip() for line in p_clean.splitlines() if line.strip()]
            list_items = [l for l in lines if l.startswith(("•", "🔹", "▪️", "-", "*", "1.", "2.", "3.", "4.", "5.", "✅"))]
            
            should_wrap = False
            detected_category = None

            # Проверка условий на прайсы/списки
            if "prices" in selected_targets:
                has_price_keyword = any(re.search(pat, p_lower) for pat in cls.PRICE_MARKERS)
                currency_count = len(re.findall(r"(?:₽|руб|rub|\$|€)", p_lower))
                if (has_price_keyword and len(list_items) >= min_list_items) or currency_count >= 2:
                    should_wrap = True
                    detected_category = "Прайс-лист & Стоимость"

            if not should_wrap and "terms" in selected_targets:
                has_terms_keyword = any(re.search(pat, p_lower) for pat in cls.TERMS_MARKERS)
                if has_terms_keyword and len(list_items) >= min_list_items:
                    should_wrap = True
                    detected_category = "Условия & Правила"

            if not should_wrap and "faq" in selected_targets:
                has_faq_keyword = any(re.search(pat, p_lower) for pat in cls.FAQ_MARKERS)
                if has_faq_keyword:
                    should_wrap = True
                    detected_category = "Ответы на вопросы"

            if not should_wrap and "recipe" in selected_targets:
                has_recipe_keyword = any(re.search(pat, p_lower) for pat in cls.RECIPE_MARKERS)
                if has_recipe_keyword and len(list_items) >= min_list_items:
                    should_wrap = True
                    detected_category = "Состав & Ингредиенты"

            if not should_wrap and "disclaimer" in selected_targets:
                has_disclaimer = any(re.search(pat, p_lower) for pat in cls.DISCLAIMER_MARKERS)
                if has_disclaimer:
                    should_wrap = True
                    detected_category = "Важная информация"

            # Оборачиваем
            if should_wrap and len(lines) >= 2:
                wrapped_count += 1
                if mode == "html":
                    wrapped_p = cls.wrap_html(p_clean)
                elif mode == "markdown_v2":
                    wrapped_p = cls.wrap_markdown_v2(p_clean)
                elif mode == "details":
                    wrapped_p = cls.wrap_details(p_clean, summary=f"📋 {detected_category or 'Подробнее'} ▾")
                else:
                    wrapped_p = cls.wrap_html(p_clean)
                new_paragraphs.append(wrapped_p)
            else:
                new_paragraphs.append(p_clean)

        result_text = "\n\n".join(new_paragraphs)
        return result_text, wrapped_count

    @classmethod
    def strip_expandable_blockquote(cls, text: str) -> str:
        """
        Удаляет теги <blockquote expandable> / <details> и префиксы **>,
        возвращая чистый текст поста (для VK, OK, Instagram, Threads).
        """
        if not text:
            return ""
        
        # 1. Снимаем HTML <blockquote...> и </blockquote>
        clean = re.sub(r"<\s*blockquote[^>]*>", "", text, flags=re.IGNORECASE)
        clean = re.sub(r"<\s*/\s*blockquote\s*>", "", clean, flags=re.IGNORECASE)
        
        # 2. Снимаем <details> и <summary>
        clean = re.sub(r"<\s*details[^>]*>", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"<\s*/\s*details\s*>", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"<\s*summary[^>]*>.*?<\s*/\s*summary\s*>", "", clean, flags=re.IGNORECASE)

        # 3. Снимаем MarkdownV2 **>
        lines = []
        for line in clean.splitlines():
            if line.startswith("**>"):
                lines.append(line[3:])
            elif line.startswith(">"):
                lines.append(line[1:])
            else:
                lines.append(line)

        clean = "\n".join(lines)
        return clean.strip()
