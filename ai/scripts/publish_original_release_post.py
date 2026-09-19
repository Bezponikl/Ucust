# -*- coding: utf-8 -*-
"""
Публикация поста с оригинальным заголовком:
"Это один маленький шаг для UCust, но гигантский скачок для всего SMM-сообщества 🚀"
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

IMAGES = [
    r"C:\Users\Metal\.gemini\antigravity\brain\a1e5a069-d05d-4bc6-88a9-30a1e0cf21c2\.user_uploaded\media_1788868298172.png",
    r"C:\Users\Metal\.gemini\antigravity\brain\a1e5a069-d05d-4bc6-88a9-30a1e0cf21c2\.user_uploaded\media_1788868302025.png",
    r"C:\Users\Metal\.gemini\antigravity\brain\a1e5a069-d05d-4bc6-88a9-30a1e0cf21c2\.user_uploaded\media_1788868305638.png",
    r"C:\Users\Metal\.gemini\antigravity\brain\a1e5a069-d05d-4bc6-88a9-30a1e0cf21c2\.user_uploaded\media_1788868309267.png",
]

ALBUM_CAPTION = """🚀 <b>Это один маленький шаг для UCust, но гигантский скачок для всего SMM-сообщества</b>

Пока индустрия привыкала к картинкам с шестью пальцами на руках и лицам из жидкого пластика, мы в <b>UCust</b> тихо готовили революцию. Мы активно приближаемся к релизу и сегодня хотим показать, чему научили нашего автономного агента-визуализатора.

<tg-spoiler>Спойлер: стоковые фотобанки уже нервно курят в сторонке.</tg-spoiler>"""

POST_TEXT = """Все 4 кадра в карусели выше сгенерированы полностью с нуля — без фотошопа, магии вне Хогвартса и ручной ретуши.

<blockquote expandable>
🌟 <b>Вот на что способен агент:</b>

1. <b>Анатомия и микротекстуры здорового человека</b>
Да, на фото с маникюром ровно 5 пальцев, аккуратная кутикула и естественная кожа. На стейке — честные кристаллы соли и аппетитный срез medium-rare, а не коричневый 3D-полигон из старой видеоигры.

2. <b>Настоящий свет и глубина (без эффекта «вырезали в Paint и наклеили»)</b>
Взгляните на чашку капучино и стейк: живой пар в лучах утреннего солнца, мягкий фокус на фоне и честные глубокие тени вместо плоской пластмассовой заливки.

3. <b>От эстетики до вирусных мемов за секунды</b>
Агент не просто делает красивую картинку — он понимает интернет-культуру и ситуативный маркетинг. Нужен строгий премиальный визуал для ресторана? Легко. Нужно обыграть свежий тренд, запустить мемный креатив под ваш продукт или сделать вирусный кадр без кринжа? Агент моментально генерирует идею и визуал под контекст бренда.

4. <b>Атмосфера ниши с полуслова</b>
Корги на вязаном пледе излучает домашний уют, кофейня манит утренним спокойствием, а салон красоты подчеркивает эстетику. Агент сам понимает, какой вайб нужен вашей аудитории.
</blockquote>

Мы продолжаем разгонять эту технологию и повышать планку реализма каждый день.

🔥 <b>Хотите в числе первых протестировать UCust для своего бренда или залететь в закрытый бета-тест?</b>

Пишите нам в личные сообщения или на почту: <code>ucust@yandex.ru</code> — покажем, как система генерирует и эстетику, и мемы под вашу нишу!"""

BUTTONS = {
    "inline_keyboard": [
        [
            {"text": "🚀 Подать заявку на бета-тест", "url": "https://t.me/testaipublisher"}
        ],
        [
            {"text": "💬 Написать в Telegram", "url": "https://t.me/testaipublisher"},
            {"text": "🌐 Наш канал UCust AI", "url": "https://t.me/testaipublisher"}
        ]
    ]
}


async def main():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🧹 Очистка старых сообщений...")
        for m_id in range(275, 310):
            try:
                await client.post(f"{url}/deleteMessage", json={"chat_id": TARGET_CHANNEL, "message_id": m_id})
            except Exception:
                pass
                
        print("📸 Публикация альбома с оригинальным заголовком...")
        media_items = []
        files_to_open = {}
        for idx, img_path in enumerate(IMAGES):
            attach_name = f"photo_{idx}"
            item = {
                "type": "photo",
                "media": f"attach://{attach_name}"
            }
            if idx == 0:
                item["caption"] = ALBUM_CAPTION
                item["parse_mode"] = "HTML"
            media_items.append(item)
            files_to_open[attach_name] = open(img_path, "rb")
            
        try:
            data = {
                "chat_id": TARGET_CHANNEL,
                "media": json.dumps(media_items)
            }
            resp_album = await client.post(f"{url}/sendMediaGroup", data=data, files=files_to_open)
            print(f"Альбом: {resp_album.status_code}")
        finally:
            for f in files_to_open.values():
                f.close()
                
        print("📝 Публикация текста...")
        msg_payload = {
            "chat_id": TARGET_CHANNEL,
            "text": POST_TEXT,
            "parse_mode": "HTML",
            "reply_markup": BUTTONS
        }
        resp_text = await client.post(f"{url}/sendMessage", json=msg_payload)
        res_j = resp_text.json()
        print(f"Текст: {resp_text.status_code}, id: {res_j.get('result', {}).get('message_id')}")
        print("🎉 Публикация с оригинальным заголовком успешно завершена!")


if __name__ == "__main__":
    asyncio.run(main())
