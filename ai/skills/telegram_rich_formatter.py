# -*- coding: utf-8 -*-
"""
модуль: telegram_rich_formatter.py
Комплексное обогащение и форматирование постов для Telegram (Bot API 7.2+):
1. <code>ПРОМОКОД</code> — копирование в 1 клик для промокодов и телефонов
2. <s>Старая цена</s> Новая цена — зачеркивание старой цены при скидках
3. <tg-spoiler>Секрет/Бонус</tg-spoiler> — спойлеры для интриги и викторин
4. <blockquote expandable>...</blockquote> — сворачиваемые прайсы и правила
5. Inline-кнопки (reply_markup) — сайт, карта (2GIS/Яндекс), запись, менеджер
6. Link preview options — управление положением и размером превью ссылок
"""

from __future__ import annotations
import re
from typing import Dict, Any, List, Optional, Tuple, Union
from skills.expandable_blockquote import ExpandableBlockquoteFormatter


class TelegramRichPostFormatter:
    """
    Продвинутый процессор обогащения постов под возможности Telegram:
    преобразует текст в интерактивный маркетинговый креатив с кнопками,
    кликабельными промокодами, спойлерами и сворачиваемыми блоками.
    """

    @classmethod
    def format_clickable_promocodes(cls, text: str, promo_code: Optional[str] = None) -> str:
        """
        Оборачивает промокоды и телефонные номера в <code>,
        чтобы в Telegram пользователь мог скопировать их в буфер обмена одним кликом.
        """
        if not text:
            return ""

        result = text

        # 1. Если явно передан промокод — оборачиваем его точное вхождение
        if promo_code and promo_code.strip():
            code_clean = promo_code.strip()
            # Если еще не обернут в <code>
            if f"<code>{code_clean}</code>" not in result and f"`{code_clean}`" not in result:
                pattern = re.compile(rf"(?<!<code>)(?<!`)\b({re.escape(code_clean)})\b(?!</code>)(?!`)", re.IGNORECASE)
                result = pattern.sub(r"<code>\1</code>", result)

        # 2. Авто-поиск промокодов по ключевым словам: «промокод: CODE», «промокоду CODE»
        promo_keyword_pattern = re.compile(
            r"(промокод[уа]?\s*[:\-—]?\s*)(?:«|\"|\b)([A-Z0-9А-Я_]{4,20})(?:»|\"|\b)",
            re.IGNORECASE
        )
        def _wrap_promo(match):
            prefix = match.group(1)
            code = match.group(2)
            return f"{prefix}<code>{code}</code>"

        result = promo_keyword_pattern.sub(_wrap_promo, result)

        # 3. Авто-поиск телефонных номеров: +7 (XXX) XXX-XX-XX или 8 (XXX) XXX-XX-XX
        phone_pattern = re.compile(
            r"(?<!<code>)(?<!`)(?:(?:\+7|8)[\s\-\(]*\d{3}[\s\-\)]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2})(?!</code>)(?!`)"
        )
        result = phone_pattern.sub(r"<code>\g<0></code>", result)

        return result

    @classmethod
    def format_strikethrough_prices(cls, text: str) -> str:
        """
        Находит паттерны старых и новых цен (скидок) и форматирует:
        «вместо 3500 ₽ всего 2490 ₽» -> «<s>3 500 ₽</s> <b>2 490 ₽</b>»
        «было 2000 руб, стало 1500 руб» -> «<s>2 000 руб</s> <b>1 500 руб</b>»
        """
        if not text:
            return ""

        patterns = [
            # «вместо 3500 ₽ всего 2490 ₽»
            (
                r"(?:вместо|старая цена:?)\s*(\d[\d\s]*(?:₽|руб|rub|\$|€))\s*(?:всего|новая цена:?|теперь)?\s*(\d[\d\s]*(?:₽|руб|rub|\$|€))",
                r"<s>\1</s> <b>\2</b>"
            ),
            # «было 3500 ₽ — стало 2490 ₽»
            (
                r"(?:было:?)\s*(\d[\d\s]*(?:₽|руб|rub|\$|€))\s*(?:[—\-,]\s*(?:стало:?))?\s*(\d[\d\s]*(?:₽|руб|rub|\$|€))",
                r"<s>\1</s> <b>\2</b>"
            ),
            # «3500 ₽ -> 2490 ₽»
            (
                r"(\d[\d\s]*(?:₽|руб|rub|\$|€))\s*(?:->|→|=>)\s*(\d[\d\s]*(?:₽|руб|rub|\$|€))",
                r"<s>\1</s> <b>\2</b>"
            )
        ]

        result = text
        for pat, repl in patterns:
            result = re.sub(pat, repl, result, flags=re.IGNORECASE)

        return result

    @classmethod
    def format_spoilers(cls, text: str, spoiler_keywords: Optional[List[str]] = None) -> str:
        """
        Оборачивает секретные ответы, интриги или скрытые бонусы в <tg-spoiler>.
        Синтаксис: <tg-spoiler>текст</tg-spoiler>
        """
        if not text:
            return ""

        result = text
        # 1. Если пользователь ввел ||текст|| (стандартный маркдаун-спойлер) -> превращаем в <tg-spoiler>
        result = re.sub(r"\|\|(.*?)\|\|", r"<tg-spoiler>\1</tg-spoiler>", result)

        # 2. Авто-поиск фраз: «секретный бонус: ...», «правильный ответ: ...»
        spoiler_triggers = [
            r"(секретный\s+бонус\s*[:\-—]?\s*)([^\n\.]+)",
            r"(правильный\s+ответ\s*[:\-—]?\s*)([^\n\.]+)",
            r"(сюрприз\s+внутри\s*[:\-—]?\s*)([^\n\.]+)"
        ]
        for trig in spoiler_triggers:
            result = re.sub(trig, r"\1<tg-spoiler>\2</tg-spoiler>", result, flags=re.IGNORECASE)

        return result

    @classmethod
    def generate_inline_keyboard(
        cls,
        company_name: str = "",
        website_url: Optional[str] = None,
        contacts: Optional[Dict[str, Any]] = None,
        social_links: Optional[Dict[str, Any]] = None,
        cta_type: str = "general",
        promo_code: Optional[str] = None,
        custom_buttons: Optional[List[List[Dict[str, str]]]] = None
    ) -> Dict[str, Any]:
        """
        Генерирует умную сетку интерактивных Inline-кнопок (reply_markup) для Telegram:
        - Кнопка 1: Главный CTA (Записаться онлайн / Меню / Заказать)
        - Кнопка 2: Наш сайт / Telegram-канал
        - Кнопка 3: Маршрут на карте (2GIS / Яндекс Карты)
        - Кнопка 4: Связаться с менеджером
        """
        if custom_buttons:
            return {"inline_keyboard": custom_buttons}

        keyboard: List[List[Dict[str, str]]] = []
        contacts = contacts or {}
        social_links = social_links or {}

        # 1. Основной сайт или витрина
        web = website_url or social_links.get("website") or contacts.get("website")
        
        # 2. Ссылки на карты (2GIS / Яндекс)
        map_url = social_links.get("2gis") or social_links.get("yandex_maps") or contacts.get("map_url")
        if not map_url and contacts.get("address"):
            clean_addr = contacts['address'].replace(" ", "+")
            map_url = f"https://yandex.ru/maps/?text={clean_addr}"

        # 3. Телефон или связь в Telegram
        tg_contact = social_links.get("telegram") or social_links.get("tg_manager") or contacts.get("telegram")
        phone = contacts.get("phone")

        row1: List[Dict[str, str]] = []
        if web and str(web).startswith("http"):
            label = "🛍️ Оформить заказ" if cta_type in ["ecommerce", "delivery"] else "🌐 Перейти на сайт"
            row1.append({"text": label, "url": str(web)})
        elif tg_contact and str(tg_contact).startswith("http"):
            row1.append({"text": "💬 Написать нам", "url": str(tg_contact)})

        if row1:
            keyboard.append(row1)

        row2: List[Dict[str, str]] = []
        if map_url and str(map_url).startswith("http"):
            row2.append({"text": "📍 Как добраться (Карта)", "url": str(map_url)})

        if tg_contact and str(tg_contact).startswith("http") and not any(b.get("url") == tg_contact for b in row1):
            row2.append({"text": "📲 Записаться", "url": str(tg_contact)})
        elif phone:
            clean_phone = re.sub(r"[^\d+]", "", str(phone))
            if clean_phone.startswith("+") or clean_phone.isdigit():
                row2.append({"text": f"📞 Позвонить", "url": f"tel:{clean_phone}"})

        if row2:
            keyboard.append(row2)

        # Если кнопок не набралось — даем базовую кнопку бренда
        if not keyboard and company_name:
            keyboard.append([{"text": f"✨ Узнать больше о {company_name}", "url": "https://t.me/UcustAi"}])

        return {"inline_keyboard": keyboard}

    @classmethod
    def build_rich_telegram_post(
        cls,
        text: str,
        company_name: str = "",
        niche: str = "",
        promo_code: Optional[str] = None,
        website_url: Optional[str] = None,
        contacts: Optional[Dict[str, Any]] = None,
        social_links: Optional[Dict[str, Any]] = None,
        enable_expandable_blockquote: bool = True,
        enable_clickable_promo: bool = True,
        enable_strikethrough: bool = True,
        enable_spoilers: bool = True,
        enable_buttons: bool = True,
        cta_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Полный сквозной пайплайн форматирования поста для Telegram:
        Возвращает:
        - clean_text: чистый текст
        - html_text: Telegram HTML (<code>, <s>, <tg-spoiler>, <blockquote expandable>)
        - markdown_v2_text: Telegram MarkdownV2 (`, ~, ||, **>)
        - reply_markup: Telegram Inline Keyboard
        - link_preview_options: настройки превью
        - expandable_blocks: список свернутых секций
        """
        if not text:
            return {
                "clean_text": "",
                "html_text": "",
                "markdown_v2_text": "",
                "reply_markup": None,
                "expandable_blocks": []
            }

        # 1. Чистый текст без служебных мета-тегов
        clean_text = ExpandableBlockquoteFormatter.strip_expandable_blockquote(text)

        # 2. Форматирование HTML
        html_text = clean_text

        # 2.1 Сворачиваемые цитаты (Expandable Blockquotes)
        expandable_blocks = []
        if enable_expandable_blockquote:
            html_text, _ = ExpandableBlockquoteFormatter.auto_wrap_sections(html_text, mode="html")
            expandable_blocks = ExpandableBlockquoteFormatter.extract_blocks(html_text)

        # 2.2 Промокоды и телефоны в <code> (копирование в 1 клик)
        if enable_clickable_promo:
            html_text = cls.format_clickable_promocodes(html_text, promo_code=promo_code)

        # 2.3 Зачеркнутые старые цены <s>
        if enable_strikethrough:
            html_text = cls.format_strikethrough_prices(html_text)

        # 2.4 Спойлеры <tg-spoiler>
        if enable_spoilers:
            html_text = cls.format_spoilers(html_text)

        # 3. Форматирование MarkdownV2
        md_text = clean_text
        if enable_expandable_blockquote:
            md_text, _ = ExpandableBlockquoteFormatter.auto_wrap_sections(md_text, mode="markdown_v2")

        # 4. Генерация Inline-кнопок
        reply_markup = None
        if enable_buttons:
            reply_markup = cls.generate_inline_keyboard(
                company_name=company_name,
                website_url=website_url,
                contacts=contacts,
                social_links=social_links,
                cta_type=cta_type,
                promo_code=promo_code
            )

        # 5. Link Preview Options
        link_preview_options = {
            "is_disabled": False,
            "prefer_small_media": True,
            "show_above_text": False
        }

        return {
            "clean_text": clean_text,
            "html_text": html_text,
            "markdown_v2_text": md_text,
            "reply_markup": reply_markup,
            "link_preview_options": link_preview_options,
            "expandable_blocks": expandable_blocks,
            "features_applied": {
                "clickable_promo": enable_clickable_promo and "<code>" in html_text,
                "strikethrough_prices": enable_strikethrough and "<s>" in html_text,
                "spoilers": enable_spoilers and "<tg-spoiler>" in html_text,
                "expandable_blockquote": bool(expandable_blocks),
                "inline_buttons": bool(reply_markup and reply_markup.get("inline_keyboard"))
            }
        }
