# -*- coding: utf-8 -*-
"""
Публикация ИДЕАЛЬНОГО ЕДИНОГО поста:
Альбом из 4 фото, где весь пост целиком (включая <blockquote expandable>, спойлер и почту <code>)
находится внутри единой подписи (978 символов < 1024 лимит Telegram).
Ширина текста и фото 100% совпадает пиксель в пиксель.
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

FULL_POST_CAPTION = """🚀 <b>Это один маленький шаг для UCust, но гигантский скачок для всего SMM-сообщества</b>

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


async def main():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("📸 Публикация идеального единого альбома с полным текстом в подписи...")
        media_items = []
        files_to_open = {}
        for idx, img_path in enumerate(IMAGES):
            attach_name = f"photo_all_in_one_{idx}"
            item = {
                "type": "photo",
                "media": f"attach://{attach_name}"
            }
            if idx == 0:
                item["caption"] = "🎯 <b>[ИДЕАЛЬНЫЙ ФОРМАТ: Единое сообщение]</b>\n\n" + FULL_POST_CAPTION
                item["parse_mode"] = "HTML"
            media_items.append(item)
            files_to_open[attach_name] = open(img_path, "rb")
            
        try:
            data = {
                "chat_id": TARGET_CHANNEL,
                "media": json.dumps(media_items)
            }
            resp_album = await client.post(f"{url}/sendMediaGroup", data=data, files=files_to_open)
            print(f"Статус публикации: {resp_album.status_code}")
            if resp_album.status_code == 200:
                print("🎉 Идеальный единый пост успешно опубликован!")
            else:
                print(f"Ошибка: {resp_album.text}")
        finally:
            for f in files_to_open.values():
                f.close()


if __name__ == "__main__":
    asyncio.run(main())
