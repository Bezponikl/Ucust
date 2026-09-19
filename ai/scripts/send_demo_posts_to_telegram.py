# -*- coding: utf-8 -*-
"""
Скрипт отправки демонстрационных постов с интерактивным форматированием Telegram 7.2+
в канал @testaipublisher.
"""

import os
import sys
import asyncio
import httpx
import json

# Ensure UTF-8 stdout
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from skills.telegram_rich_formatter import TelegramRichPostFormatter

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8840988455:AAFsUPjrOSvQdMpuK5c-MkQdPcVB092tPzw")
TARGET_CHANNEL = "@testaipublisher"


async def send_telegram_message(html_text: str, reply_markup: dict = None, link_preview_options: dict = None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TARGET_CHANNEL,
        "text": html_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    if link_preview_options:
        payload["link_preview_options"] = link_preview_options

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(url, json=payload)
        res_data = resp.json()
        if resp.status_code == 200 and res_data.get("ok"):
            msg_id = res_data.get("result", {}).get("message_id")
            print(f"✅ Пост успешно опубликован в {TARGET_CHANNEL}! (Message ID: {msg_id})")
            return True
        else:
            print(f"❌ Ошибка отправки ({resp.status_code}): {res_data}")
            return False


async def main():
    print(f"🚀 Запуск отправки демонстрационных постов в {TARGET_CHANNEL}...\n")

    # -------------------------------------------------------------
    # ПОСТ 1: Гастрономия / Кофейня (Меню, 1-click промокод, скидка, кнопки)
    # -------------------------------------------------------------
    post_coffee = """☕ <b>Утро начинается с правильного вкуса в «Maison Coffee»</b>

Осень — не повод грустить, а повод попробовать наше обновлённое сезонное спешелти-меню. Мы отобрали зёрна свежей обжарки из Эфиопии и Колумбии с яркими нотами карамели и бергамота.

<blockquote expandable>
📋 <b>Сезонное меню напитков и десертов:</b>
• Черничный Латте на кокосовом — 320 ₽
• Фисташковый Раф с морской солью — 350 ₽
• Флэт Уайт на овсяном — 290 ₽
• Круассан с миндальным кремом — 260 ₽
• Тартин со слабосолёным лососем — 420 ₽
</blockquote>

🔥 Только до конца недели: авторский комбо-сет <s>770 ₽</s> <b>490 ₽</b> по промокоду <code>COFFEE2026</code>! Просто нажмите на промокод, чтобы скопировать.

<blockquote expandable>
Правила действия акции:
1. Предложение действует с 08:00 до 12:00 в будние дни.
2. Скидка не суммируется с другими специальными предложениями.
3. Доступно при заказе навынос или в зале.
</blockquote>

🎁 Секретный подарок к заказу: <tg-spoiler>фирменный имбирный пряник при заказе от 500 ₽</tg-spoiler>"""

    buttons_coffee = {
        "inline_keyboard": [
            [
                {"text": "🛍️ Оформить предзаказ", "url": "https://t.me/testaipublisher"}
            ],
            [
                {"text": "📍 Как добраться (2GIS)", "url": "https://2gis.ru/moscow"},
                {"text": "💬 Связь с бариста", "url": "https://t.me/testaipublisher"}
            ]
        ]
    }

    print("--- Отправка Поста 1: Спешелти-кофейня ---")
    await send_telegram_message(post_coffee, reply_markup=buttons_coffee)
    await asyncio.sleep(2)

    # -------------------------------------------------------------
    # ПОСТ 2: Бьюти-сфера / Барбершоп & Салон (Прайс, спойлер, онлайн-запись)
    # -------------------------------------------------------------
    post_barber = """💈 <b>Идеальный стиль и уверенность в «OldBoy Studio»</b>

Качественная стрижка — это не просто длина волос, это ваша визитная карточка перед важной встречей или свиданием. Наши топ-барберы подберут форму под геометрию лица.

<blockquote expandable>
✂️ <b>Полный прайс-лист на услуги барбершопа:</b>
• Мужская модельная стрижка + мытье — 1 800 ₽
• Моделирование и стрижка бороды — 1 200 ₽
• Комплекс «Стрижка + Борода» — 2 600 ₽
• Премиальное королевское бритье — 1 500 ₽
• Уход за кожей лица и SPA — 1 100 ₽
</blockquote>

⚡ Для новых клиентов действует спеццена: комплекс <s>2600 ₽</s> <b>1890 ₽</b> при записи по номеру <code>+7 (999) 777-22-33</code> или по коду <code>FIRSTLOOK</code>.

Интрига месяца: <tg-spoiler>каждый 5-й гость на этой неделе получает премиум-масло для бороды в подарок!</tg-spoiler>"""

    buttons_barber = {
        "inline_keyboard": [
            [
                {"text": "📅 Записаться онлайн", "url": "https://t.me/testaipublisher"}
            ],
            [
                {"text": "📍 Открыть на Яндекс Картах", "url": "https://yandex.ru/maps"},
                {"text": "📞 Позвонить в салон", "url": "https://t.me/testaipublisher"}
            ]
        ]
    }

    print("\n--- Отправка Поста 2: Премиум-Барбершоп ---")
    await send_telegram_message(post_barber, reply_markup=buttons_barber)
    await asyncio.sleep(2)

    # -------------------------------------------------------------
    # ПОСТ 3: Фитнес / Премиум-клуб (Абонементы, условия, карта)
    # -------------------------------------------------------------
    post_fitness = """🏋️ <b>Перезагрузи свое тело: старт нового фитнес-сезона в «Pulse Gym»</b>

Хватит откладывать здоровье на понедельник. 1200 м² премиальных тренажеров Hammer Strength, зона кроссфита, сауна и персональный контроль тренера.

<blockquote expandable>
💳 <b>Клубные карты и тарифы:</b>
• Безлимит 1 месяц (зал + сауна + вводная тренировка) — 3 900 ₽
• Дневной абонемент (до 17:00) — 2 700 ₽
• Абонемент на 6 месяцев (все зоны без ограничений) — 16 900 ₽
• Годовая VIP-карта с заморозкой до 60 дней — 27 500 ₽
• Пакет из 10 персональных тренировок — 14 000 ₽
</blockquote>

🎯 Специальное предложение: первый месяц безлимита <s>3900 ₽</s> <b>2490 ₽</b> по промокоду <code>FITPULSE</code>!

<blockquote expandable>
Что входит в каждую клубную карту:
- Неограниченный доступ в кардио- и силовую зону
- Финская сауна после тренировки
- Бесплатный фитнес-тест и анализ состава тела
- Сейф для ценных вещей и полотенца
</blockquote>

Узнайте свой персональный бонус: <tg-spoiler>+2 недели к любому абонементу при покупке сегодня!</tg-spoiler>"""

    buttons_fitness = {
        "inline_keyboard": [
            [
                {"text": "🔥 Забронировать карту по акции", "url": "https://t.me/testaipublisher"}
            ],
            [
                {"text": "📍 Маршрут в клуб", "url": "https://2gis.ru"},
                {"text": "💬 Задать вопрос менеджеру", "url": "https://t.me/testaipublisher"}
            ]
        ]
    }

    print("\n--- Отправка Поста 3: Фитнес-клуб ---")
    await send_telegram_message(post_fitness, reply_markup=buttons_fitness)

    print("\n✨ Все 3 демонстрационных поста успешно отправлены в канал https://t.me/testaipublisher!")


if __name__ == "__main__":
    asyncio.run(main())
