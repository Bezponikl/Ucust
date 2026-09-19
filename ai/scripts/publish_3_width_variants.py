# -*- coding: utf-8 -*-
"""
Создание тестовых постов для оценки 3 вариантов выравнивания ширины в Telegram:
- Вариант 1: Единый монолитный пост (Стильный коллаж 2x2 из 4 фото + весь текст в caption с <blockquote expandable> и кнопками)
- Вариант 2: Второе сообщение целиком обернуто в стилизованный <blockquote> (акцентная полоса, компактная колонка)
- Вариант 3: Второе сообщение с узким стильным брендовым баннером-разделителем (чтобы Telegram зафиксировал ширину под медиа)

Старые посты НЕ УДАЛЯЮТСЯ.
"""

import os
import sys
import asyncio
import httpx
import json
from PIL import Image, ImageDraw, ImageFont

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

# 1. Создаем Коллаж 2x2 для Варианта 1
COLLAGE_PATH = r"C:\Users\Metal\Documents\Новая папка\Ucust\ai\output\ucust_collage_2x2.jpg"
BANNER_PATH = r"C:\Users\Metal\Documents\Новая папка\Ucust\ai\output\ucust_separator_banner.jpg"

os.makedirs(os.path.dirname(COLLAGE_PATH), exist_ok=True)

def create_media_assets():
    # Создание коллажа 2x2
    imgs = [Image.open(p).convert("RGB") for p in IMAGES]
    # Ресайзим к единому квадрату 600x600 каждый (итого коллаж 1200x1200)
    target_w, target_h = 600, 600
    resized = []
    for img in imgs:
        # Центрированный crop до соотношения 1:1
        min_dim = min(img.width, img.height)
        left = (img.width - min_dim) // 2
        top = (img.height - min_dim) // 2
        cropped = img.crop((left, top, left + min_dim, top + min_dim))
        resized.append(cropped.resize((target_w, target_h), Image.Resampling.LANCZOS))
    
    gap = 8
    collage_w = target_w * 2 + gap
    collage_h = target_h * 2 + gap
    collage = Image.new("RGB", (collage_w, collage_h), (24, 24, 27))
    
    collage.paste(resized[0], (0, 0))
    collage.paste(resized[1], (target_w + gap, 0))
    collage.paste(resized[2], (0, target_h + gap))
    collage.paste(resized[3], (target_w + gap, target_h + gap))
    
    collage.save(COLLAGE_PATH, "JPEG", quality=95)
    print(f"✅ Коллаж сохранен: {COLLAGE_PATH}")
    
    # Создание тонкого брендового баннера-разделителя (1200x300)
    banner = Image.new("RGB", (1200, 240), (18, 24, 38))
    draw = ImageDraw.Draw(banner)
    
    # Рисуем градиентную полосу и плашку
    draw.rectangle([(0, 0), (1200, 8)], fill=(99, 102, 241)) # Фиолетово-синий акцент
    draw.rectangle([(0, 232), (1200, 240)], fill=(99, 102, 241))
    
    # Декоративный текст
    draw.text((60, 80), "UCUST AI ENGINE • NEXT-GEN VISUAL REALISM", fill=(148, 163, 184))
    draw.text((60, 120), "Автономный генератор контента без ручной ретуши", fill=(255, 255, 255))
    
    banner.save(BANNER_PATH, "JPEG", quality=95)
    print(f"✅ Баннер-разделитель сохранен: {BANNER_PATH}")

create_media_assets()


# Тексты
CAPTION_V1 = """🚀 <b>Это один маленький шаг для UCust, но гигантский скачок для всего SMM-сообщества</b>

Пока индустрия привыкала к картинкам с шестью пальцами на руках и лицам из жидкого пластика, мы в <b>UCust</b> тихо готовили революцию.

<tg-spoiler>Спойлер: стоковые фотобанки уже нервно курят в сторонке.</tg-spoiler>

Все 4 кадра сгенерированы полностью с нуля — без фотошопа и ретуши.

<blockquote expandable>
🌟 <b>Вот на что способен агент:</b>
1. <b>Анатомия и микротекстуры:</b> 5 пальцев на маникюре, честная текстура кожи, аппетитный стейк medium-rare с кристаллами соли.
2. <b>Честный свет и пар:</b> живой пар над капучино, естественные блики и кинематографичная глубина 35mm.
3. <b>Эстетика и вирусные тренды:</b> создание креативов под любую нишу за секунды без кринжа.
4. <b>Атмосфера ниши:</b> от домашнего уюта корги до премиального ресторана.
</blockquote>

🔥 <b>Хотите протестировать UCust для своего бренда?</b>
Пишите нам в ЛС или на почту: <code>ucust@yandex.ru</code>"""


# Вариант 2 тексты
ALBUM_CAPTION_V2 = """🚀 <b>[ВАРИАНТ 2] Это один маленький шаг для UCust, но гигантский скачок для всего SMM-сообщества</b>

Пока индустрия привыкала к картинкам с шестью пальцами и пластиковым лицам, мы в <b>UCust</b> тихо готовили революцию.

<tg-spoiler>Спойлер: стоковые фотобанки уже нервно курят в сторонке.</tg-spoiler>"""

TEXT_V2 = """<blockquote>Все 4 кадра в карусели выше сгенерированы с нуля — без фотошопа и ручной ретуши.

🌟 <b>Вот на что способен агент:</b>
1. <b>Анатомия и текстуры:</b> ровно 5 пальцев на маникюре, сочный стейк medium-rare с кристаллами соли.
2. <b>Свет и пар:</b> живой пар над чашкой капучино, честные тени и кинематографичный фокус 35mm.
3. <b>Эстетика и мемы:</b> генерация идей под тренды без кринжа.
4. <b>Атмосфера ниши:</b> от уюта корги до строгого премиума.

🔥 <b>Хотите протестировать UCust для своего бренда?</b>
Пишите нам в ЛС или на почту: <code>ucust@yandex.ru</code></blockquote>"""


# Вариант 3 тексты
ALBUM_CAPTION_V3 = """🚀 <b>[ВАРИАНТ 3] Это один маленький шаг для UCust, но гигантский скачок для всего SMM-сообщества</b>

Пока индустрия привыкала к картинкам с шестью пальцами и пластиковым лицам, мы в <b>UCust</b> тихо готовили революцию.

<tg-spoiler>Спойлер: стоковые фотобанки уже нервно курят в сторонке.</tg-spoiler>"""

BANNER_CAPTION_V3 = """Все 4 кадра в карусели выше сгенерированы с нуля — без фотошопа и ручной ретуши.

<blockquote expandable>
🌟 <b>Возможности автономного визуального агента:</b>
1. <b>Анатомия и микротекстуры:</b> 5 пальцев на маникюре, естественная кутикула, честный срез стейка medium-rare.
2. <b>Свет и объем:</b> живой пар в лучах утреннего солнца, мягкий боке и честные тени.
3. <b>Эстетика и вирусность:</b> генерация трендов и мемных креативов за секунды.
4. <b>Атмосфера:</b> моментальная передача вайба целевой аудитории.
</blockquote>

🔥 <b>Хотите в закрытый бета-тест UCust?</b>
Пишите в ЛС или на почту: <code>ucust@yandex.ru</code>"""


async def main():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # -------------------------------------------------------------
        # 1. ВАРИАНТ 1: Монолитный пост (Коллаж 2x2 + единый caption)
        # -------------------------------------------------------------
        print("\n--- Отправка ВАРИАНТА 1 (Монолитный Коллаж 2x2) ---")
        with open(COLLAGE_PATH, "rb") as f:
            data = {
                "chat_id": TARGET_CHANNEL,
                "caption": "💎 <b>[ВАРИАНТ 1: Единый монолитный пост-коллаж]</b>\n\n" + CAPTION_V1,
                "parse_mode": "HTML",
                "reply_markup": json.dumps(BUTTONS)
            }
            resp1 = await client.post(f"{url}/sendPhoto", data=data, files={"photo": f})
            print(f"Вариант 1: {resp1.status_code}")
            
        await asyncio.sleep(2)

        # -------------------------------------------------------------
        # 2. ВАРИАНТ 2: Альбом 4 фото + Текст обернут в красивый <blockquote>
        # -------------------------------------------------------------
        print("\n--- Отправка ВАРИАНТА 2 (Альбом + Второе сообщение в blockquote) ---")
        media_items_v2 = []
        files_v2 = {}
        for idx, img_path in enumerate(IMAGES):
            attach_name = f"photo_v2_{idx}"
            item = {"type": "photo", "media": f"attach://{attach_name}"}
            if idx == 0:
                item["caption"] = ALBUM_CAPTION_V2
                item["parse_mode"] = "HTML"
            media_items_v2.append(item)
            files_v2[attach_name] = open(img_path, "rb")
            
        try:
            data_v2 = {"chat_id": TARGET_CHANNEL, "media": json.dumps(media_items_v2)}
            resp_alb2 = await client.post(f"{url}/sendMediaGroup", data=data_v2, files=files_v2)
            print(f"Вариант 2 (Альбом): {resp_alb2.status_code}")
        finally:
            for f in files_v2.values():
                f.close()

        # Второе сообщение в blockquote
        resp_txt2 = await client.post(f"{url}/sendMessage", json={
            "chat_id": TARGET_CHANNEL,
            "text": TEXT_V2,
            "parse_mode": "HTML",
            "reply_markup": BUTTONS
        })
        print(f"Вариант 2 (Текст): {resp_txt2.status_code}")
        
        await asyncio.sleep(2)

        # -------------------------------------------------------------
        # 3. ВАРИАНТ 3: Альбом 4 фото + Второе сообщение с баннером-разделителем
        # -------------------------------------------------------------
        print("\n--- Отправка ВАРИАНТА 3 (Альбом + Второе сообщение с медиа-баннером) ---")
        media_items_v3 = []
        files_v3 = {}
        for idx, img_path in enumerate(IMAGES):
            attach_name = f"photo_v3_{idx}"
            item = {"type": "photo", "media": f"attach://{attach_name}"}
            if idx == 0:
                item["caption"] = ALBUM_CAPTION_V3
                item["parse_mode"] = "HTML"
            media_items_v3.append(item)
            files_v3[attach_name] = open(img_path, "rb")
            
        try:
            data_v3 = {"chat_id": TARGET_CHANNEL, "media": json.dumps(media_items_v3)}
            resp_alb3 = await client.post(f"{url}/sendMediaGroup", data=data_v3, files=files_v3)
            print(f"Вариант 3 (Альбом): {resp_alb3.status_code}")
        finally:
            for f in files_v3.values():
                f.close()

        # Второе сообщение с баннером
        with open(BANNER_PATH, "rb") as bf:
            data_b3 = {
                "chat_id": TARGET_CHANNEL,
                "caption": BANNER_CAPTION_V3,
                "parse_mode": "HTML",
                "reply_markup": json.dumps(BUTTONS)
            }
            resp_b3 = await client.post(f"{url}/sendPhoto", data=data_b3, files={"photo": bf})
            print(f"Вариант 3 (Баннер+Текст): {resp_b3.status_code}")

    print("\n🎉 Все 3 варианта успешно отправлены в канал https://t.me/testaipublisher!")


if __name__ == "__main__":
    asyncio.run(main())
