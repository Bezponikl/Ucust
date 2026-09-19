# -*- coding: utf-8 -*-
"""
Публикация единого поста с коллажем 4 фото, полным текстом и Inline Reply кнопками.
Демонстрация возможности обновления кнопок на лету (editMessageReplyMarkup).
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

BOT_TOKEN = "8840988455:AAFsUPjrOSvQdMpuK5c-MkQdPcVB092tPzw"
TARGET_CHANNEL = "@testaipublisher"
COLLAGE_PATH = r"C:\Users\Metal\Documents\Новая папка\Ucust\ai\output\ucust_collage_2x2.jpg"

POST_CAPTION = """🚀 <b>Это один маленький шаг для UCust, но гигантский скачок для всего SMM-сообщества</b>

Пока индустрия привыкала к картинкам с шестью пальцами на руках и лицам из жидкого пластика, мы в <b>UCust</b> тихо готовили революцию.

<tg-spoiler>Спойлер: стоковые фотобанки уже нервно курят в сторонке.</tg-spoiler>

Все 4 кадра сгенерированы полностью с нуля — без фотошопа и ретуши.

<blockquote expandable>
🌟 <b>Вот на что способен наш визуальный агент:</b>
1. <b>Анатомия и микротекстуры:</b> 5 пальцев на маникюре, естественная кутикула, сочный стейк medium-rare с кристаллами соли.
2. <b>Честный свет и пар:</b> живой пар над капучино, мягкий фокус 35mm и глубокие тени вместо плоской заливки.
3. <b>Эстетика и вирусность:</b> создание ситуативных креативов под тренды без кринжа.
4. <b>Атмосфера ниши:</b> от домашнего уюта корги до строгого ресторанного премиума.
</blockquote>

🔥 <b>Хотите протестировать UCust для своего бренда?</b>
Пишите нам в ЛС @testaipublisher или на почту: <code>ucust@yandex.ru</code>"""

BUTTONS = {
    "inline_keyboard": [
        [
            {"text": "🚀 Подать заявку на бета-тест", "url": "https://t.me/testaipublisher"}
        ],
        [
            {"text": "💬 Написать в Telegram", "url": "https://t.me/testaipublisher"},
            {"text": "🌐 Канал UCust AI", "url": "https://t.me/testaipublisher"}
        ]
    ]
}


async def main():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("📸 Публикация единого поста с 4 фото в коллаже, текстом и Reply-кнопками...")
        with open(COLLAGE_PATH, "rb") as f:
            data = {
                "chat_id": TARGET_CHANNEL,
                "caption": POST_CAPTION,
                "parse_mode": "HTML",
                "reply_markup": json.dumps(BUTTONS)
            }
            resp = await client.post(f"{url}/sendPhoto", data=data, files={"photo": f})
            res_j = resp.json()
            if resp.status_code == 200 and res_j.get("ok"):
                msg_id = res_j["result"]["message_id"]
                print(f"🎉 Пост с кнопками успешно опубликован! Message ID: {msg_id}")
            else:
                print(f"❌ Ошибка отправки: {res_j}")


if __name__ == "__main__":
    asyncio.run(main())
