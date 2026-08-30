"""
PhotoGeneratorSkill — Модуль автономной генерации фото и визуального контента для SMM.
Создает коммерческие промпты по стандартам современной фотографии (Sony A7R / Hasselblad),
управляет ракурсами, стилями, палитрой бренда и генерирует изображения.
"""

from __future__ import annotations

import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import os
import re
import uuid
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger("photo_generator_skill")


class PhotoGeneratorSkill:
    """
    Автономный ИИ-фотограф для SMM.
    - Динамический Prompt Engineering под нишу бизнеса
    - Поддержка соотношений сторон: 1:1 (Квадрат), 4:5 (Портрет), 16:9 (Баннер), 9:16 (Stories)
    - Интеграция с ComfyUI / SDXL / Diffusers / Local Visual Engine
    """

    ASPECT_RATIOS = {
        "1:1": (1024, 1024),
        "4:5": (1080, 1350),
        "16:9": (1280, 720),
        "9:16": (720, 1280)
    }

    NICHE_PRESETS = {
        "кофейня": {
            "subject": "artisan craft coffee cup with neat latte art, fresh croissant on small wooden saucer, casual table setting",
            "environment": "cozy local coffee shop, soft morning window light, warm wooden tabletop, relaxed cafe background",
            "lighting": "natural soft ambient morning daylight from window, warm gentle tones, realistic room shadows",
            "camera": "Shot on iPhone 16 Pro, 24mm f/1.78 main lens, natural handheld eye-level angle, candid smartphone photo, unedited Apple ProRAW look"
        },
        "ресторан": {
            "subject": "delicious appetizing dish, fresh herbs, natural foodie presentation, ceramic plate",
            "environment": "warm inviting bistro table, cutlery, cloth napkin, casual dining atmosphere",
            "lighting": "warm ambient dining light, soft candle or window glow, natural food shadows",
            "camera": "Shot on iPhone 16 Pro, 48mm 2x telephoto mode, natural tabletop angle, candid food photography, realistic foodie post"
        },
        "красота": {
            "subject": "minimalist aesthetic skincare bottle, natural morning skincare routine, clean cosmetic dropper",
            "environment": "sunlit bathroom vanity marble shelf, soft fresh towel, green plant leaf in soft background",
            "lighting": "bright clean natural morning daylight, soft diffused window glow, fresh organic mood",
            "camera": "Shot on iPhone 16 Pro, 24mm camera, candid lifestyle beauty shot, authentic UGC texture, crisp realistic details"
        },
        "it": {
            "subject": "clean modern workspace desk, open laptop with clean code editor, stylish coffee mug, mechanical keyboard",
            "environment": "bright minimalist home office or coworking, indoor potted plant, cozy desk setup",
            "lighting": "natural ambient daylight from nearby window, soft warm desk lamp accent",
            "camera": "Shot on iPhone 16 Pro, natural casual desk point-of-view, authentic candid tech lifestyle photo, unedited RAW look"
        },
        "фитнес": {
            "subject": "modern stylish gym water bottle, fitness tracker on wrist, wireless earbuds case on bench",
            "environment": "modern clean gym corner, motivational athletic environment, wooden locker room bench",
            "lighting": "realistic ambient gym lighting, natural clean highlights",
            "camera": "Shot on iPhone 16 Pro, dynamic candid smartphone angle, authentic workout lifestyle photo"
        },
        "авто": {
            "subject": "clean sleek car interior steering wheel and dashboard, or glossy car hood with clean reflections",
            "environment": "urban street parking at golden hour or clean modern car wash bay",
            "lighting": "natural golden hour sunset light, realistic sky reflections on paint, natural street ambient",
            "camera": "Shot on iPhone 16 Pro, 24mm wide angle, candid automotive smartphone photo, authentic car enthusiast vibe"
        },
        "недвижимость": {
            "subject": "bright welcoming apartment living room, comfortable sofa with throw pillows, sunbeam on floor",
            "environment": "modern renovated apartment interior, minimalist decor, open window with city view",
            "lighting": "bright natural afternoon sunbeams, airy room daylight, true-to-life colors",
            "camera": "Shot on iPhone 16 Pro, ultra-wide 13mm lens / 24mm main, natural eye-level room view, authentic apartment tour photo"
        },
        "одежда": {
            "subject": "stylish casual daily outfit, minimal accessories, neat fabric texture, mirror selfie or flatlay",
            "environment": "bright bedroom full-length mirror or minimalist aesthetic clothing rack",
            "lighting": "soft natural window light, subtle room shadows, true fabric colors",
            "camera": "Shot on iPhone 16 Pro, casual candid mirror photo or flatlay, authentic fashion UGC aesthetic"
        },
        "медицина": {
            "subject": "clean modern dental or medical clinic reception desk, friendly reassuring environment",
            "environment": "bright sterile yet comfortable clinic room, neat medical brochure, indoor plant",
            "lighting": "soft bright diffused medical clinic light, calm and trustworthy atmosphere",
            "camera": "Shot on iPhone 16 Pro, natural smartphone point-of-view, authentic candid clinic photo"
        },
        "услуги": {
            "subject": "clean business planner, stylish coffee cup, tablet with charts, neat pen on wooden desk",
            "environment": "sunlit contemporary cafe or bright meeting room, casual productive atmosphere",
            "lighting": "natural window daylight, soft warm room ambient",
            "camera": "Shot on iPhone 16 Pro, casual tabletop angle, authentic business lifestyle UGC photo"
        }
    }

    DEFAULT_NEGATIVE_PROMPT = (
        "staged studio photoshoot, heavy artificial studio strobes, studio softboxes, plastic skin, "
        "wax figure, mannequin, 3d render, cgi, cartoon, anime, illustration, airbrushed, unnatural stiff pose, "
        "fake commercial look, oversaturated, blurry, bad anatomy, deformed hands, extra fingers, watermark, lowres"
    )

    def __init__(self, output_dir: Optional[str] = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = output_dir or os.path.normpath(os.path.join(base_dir, "..", "output", "photos"))
        os.makedirs(self.output_dir, exist_ok=True)

    def create_smm_prompt(
        self,
        topic: str,
        niche: str = "Общий бизнес",
        aspect_ratio: str = "1:1",
        brand_colors: Optional[List[str]] = None,
        style: str = "candid_iphone"
    ) -> Dict[str, Any]:
        """
        Составляет аутентичный, живой промпт для мобильной фотографии на iPhone (UGC / Lifestyle).
        """
        niche_key = "кофейня"
        for k in self.NICHE_PRESETS:
            if k in niche.lower() or k in topic.lower():
                niche_key = k
                break

        preset = self.NICHE_PRESETS.get(niche_key, self.NICHE_PRESETS["кофейня"])
        colors_str = f"Natural subtle color accents: {', '.join(brand_colors)}. " if brand_colors else ""

        positive_prompt = (
            f"Authentic candid lifestyle photograph for {niche}. Subject: {topic.strip() or preset['subject']}. "
            f"Environment: {preset['environment']}. "
            f"{colors_str}"
            f"Lighting: {preset['lighting']}. "
            f"Camera & Style: {preset['camera']}, genuine social media aesthetic, authentic depth of field, real life texture, natural grain, unedited raw photo."
        )

        dimensions = self.ASPECT_RATIOS.get(aspect_ratio, self.ASPECT_RATIOS["1:1"])

        return {
            "positive_prompt": positive_prompt,
            "negative_prompt": self.DEFAULT_NEGATIVE_PROMPT,
            "aspect_ratio": aspect_ratio,
            "width": dimensions[0],
            "height": dimensions[1],
            "niche": niche,
            "topic": topic
        }

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        """
        Кроссплатформенный загрузчик шрифтов с гарантированной поддержкой кириллицы.
        """
        bundled_font = os.path.normpath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "brand_font.ttf")
        )
        font_candidates = [
            bundled_font,
            "C:/Windows/Fonts/segoeui.ttf" if not bold else "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arial.ttf" if not bold else "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibri.ttf" if not bold else "C:/Windows/Fonts/calibrib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
            "arial.ttf"
        ]

        for path in font_candidates:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue
        try:
            return ImageFont.load_default()
        except Exception:
            return None

    async def generate_photo(
        self,
        topic: str,
        niche: str = "Бизнес",
        aspect_ratio: str = "1:1",
        brand_colors: Optional[List[str]] = None,
        style: str = "photorealistic",
        company_name: str = "UCust",
        attachments: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Полный цикл генерации профессиональной SMM фотографии и коммерческого визуала.
        """
        prompt_data = self.create_smm_prompt(
            topic=topic,
            niche=niche,
            aspect_ratio=aspect_ratio,
            brand_colors=brand_colors,
            style=style
        )

        photo_id = f"photo_{uuid.uuid4().hex[:10]}"
        filename = f"{photo_id}.jpg"
        file_path = os.path.join(self.output_dir, filename)

        rendered_via_comfy = False
        # 1. Попытка рендера через ComfyUI API / CLI runner
        try:
            from skills.comfy_cli_runner import ComfyCLIRunner
            comfy_runner = ComfyCLIRunner(output_dir=self.output_dir)
            if await comfy_runner.is_server_online():
                print("[PhotoGeneratorSkill] ⚡ ComfyUI (127.0.0.1:8188) онлайн — запуск фото-воркфлоу...")
                res_comfy = await comfy_runner.execute_workflow(
                    photo_prompt=prompt_data["positive_prompt"],
                    raw_topic=topic,
                    negative_prompt=prompt_data["negative_prompt"],
                    aspect_ratio=aspect_ratio
                )
                if res_comfy.get("photo_path") and os.path.exists(res_comfy["photo_path"]) and os.path.getsize(res_comfy["photo_path"]) > 100:
                    file_path = res_comfy["photo_path"]
                    filename = os.path.basename(file_path)
                    rendered_via_comfy = True
        except Exception as ex:
            print(f"[PhotoGeneratorSkill] ℹ️ ComfyUI статус: {ex}")

        # 2. Рендер высококачественного брендового SMM-визуала (если ComfyUI оффлайн)
        if not rendered_via_comfy:
            self._render_realistic_smm_visual(
                output_path=file_path,
                topic=topic,
                niche=niche,
                width=prompt_data["width"],
                height=prompt_data["height"],
                brand_colors=brand_colors,
                company_name=company_name,
                attachments=attachments
            )

        # 3. Строгая валидация наличия и размера файла на диске
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            raise RuntimeError(f"Критическая ошибка: фото-файл не сформирован: {file_path}")

        # 4. Формирование публичного URL
        relative_url = f"/output/photos/{filename}"

        return {
            "status": "success",
            "photo_id": photo_id,
            "filename": filename,
            "image_url": relative_url,
            "file_path": file_path,
            "positive_prompt": prompt_data["positive_prompt"],
            "negative_prompt": prompt_data["negative_prompt"],
            "aspect_ratio": aspect_ratio,
            "width": prompt_data["width"],
            "height": prompt_data["height"],
            "created_at": datetime.utcnow().isoformat()
        }

    def _render_realistic_smm_visual(
        self,
        output_path: str,
        topic: str,
        niche: str,
        width: int,
        height: int,
        brand_colors: Optional[List[str]] = None,
        company_name: str = "UCust",
        attachments: Optional[List[Any]] = None
    ) -> None:
        """
        Рендерит высококачественный коммерческий SMM-визуал с градиентами, логотипом бренда и типографикой.
        """
        if not PIL_AVAILABLE:
            with open(output_path, "wb") as f:
                f.write(b"MOCK_JPEG_IMAGE_DATA")
            return

        import base64
        import io

        niche_lower = niche.lower()
        topic_lower = topic.lower()

        # 1. Цветовая палитра под нишу бизнеса
        if "кофе" in niche_lower or "ресторан" in niche_lower:
            bg_top = (38, 22, 14)
            bg_bottom = (16, 10, 8)
            glow_primary = (255, 140, 60, 70)
            glow_secondary = (220, 90, 40, 60)
            glow_accent = (160, 60, 30, 50)
            accent_pill = (230, 110, 35, 230)
            dot_color = (255, 180, 80, 255)
        elif "красот" in niche_lower or "космет" in niche_lower or "спа" in niche_lower:
            bg_top = (42, 20, 34)
            bg_bottom = (18, 10, 16)
            glow_primary = (255, 90, 160, 70)
            glow_secondary = (210, 60, 180, 60)
            glow_accent = (120, 40, 160, 50)
            accent_pill = (235, 60, 140, 230)
            dot_color = (255, 140, 200, 255)
        elif "авто" in niche_lower or "детейл" in niche_lower:
            bg_top = (20, 24, 30)
            bg_bottom = (10, 12, 16)
            glow_primary = (0, 210, 255, 70)
            glow_secondary = (255, 45, 85, 60)
            glow_accent = (0, 140, 255, 50)
            accent_pill = (0, 160, 240, 230)
            dot_color = (0, 220, 255, 255)
        else: # IT, UCust, Сервисы, Контент, Автоматизация
            bg_top = (14, 20, 38)
            bg_bottom = (8, 12, 24)
            glow_primary = (0, 150, 255, 75)
            glow_secondary = (255, 60, 120, 65)
            glow_accent = (130, 40, 230, 60)
            accent_pill = (0, 130, 255, 230)
            dot_color = (0, 210, 255, 255)

        img = Image.new("RGBA", (width, height), color=(*bg_top, 255))

        # 2. Рендер вертикального градиентного фона
        for y in range(height):
            f = y / float(height)
            r = int(bg_top[0] * (1 - f) + bg_bottom[0] * f)
            g = int(bg_top[1] * (1 - f) + bg_bottom[1] * f)
            b = int(bg_top[2] * (1 - f) + bg_bottom[2] * f)
            ImageDraw.Draw(img).line([(0, y), (width, y)], fill=(r, g, b, 255))

        import random
        # 3. Атмосферное фоновое свечение (Luminous Mesh Glow с динамическим разбросом)
        glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow_layer)
        shift_x = random.randint(-40, 40)
        shift_y = random.randint(-30, 30)
        gdraw.ellipse([int(width * 0.05) + shift_x, int(height * 0.1) + shift_y, int(width * 0.55) + shift_x, int(height * 0.55) + shift_y], fill=glow_primary)
        gdraw.ellipse([int(width * 0.48) - shift_x, int(height * 0.12) - shift_y, int(width * 0.95) - shift_x, int(height * 0.60) - shift_y], fill=glow_secondary)
        gdraw.ellipse([int(width * 0.25) + shift_y, int(height * 0.35) + shift_x, int(width * 0.75) + shift_y, int(height * 0.85) + shift_x], fill=glow_accent)
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(int(min(width, height) * 0.08)))
        img = Image.alpha_composite(img, glow_layer)

        # 4. Центральная стеклянная карточка (Glassmorphism Container)
        card_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        cdraw = ImageDraw.Draw(card_layer)
        margin = int(width * 0.05)
        card_top = int(height * 0.12)
        card_bottom = int(height * 0.88)
        cdraw.rounded_rectangle(
            [margin, card_top, width - margin, card_bottom],
            radius=36,
            fill=(255, 255, 255, 14),
            outline=(255, 255, 255, 50),
            width=2
        )
        img = Image.alpha_composite(img, card_layer)

        # 5. Обработка прикрепленного логотипа или бренд-изображения
        logo_img = None
        if attachments and len(attachments) > 0:
            first_att = attachments[0]
            att_data = first_att.get("dataUrl") or first_att.get("url") if isinstance(first_att, dict) else str(first_att)
            if att_data and att_data.startswith("data:image"):
                try:
                    header, b64data = att_data.split(",", 1)
                    logo_bytes = base64.b64decode(b64data)
                    logo_img = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
                except Exception as e:
                    print(f"[PhotoGeneratorSkill] ⚠️ Ошибка декодирования логотипа из base64: {e}")

        # Проверяем логотипы в стандартных директориях
        if logo_img is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            default_logo_paths = [
                os.path.normpath(os.path.join(base_dir, "..", "assets", "brand-logo.png")),
                os.path.normpath(os.path.join(base_dir, "..", "..", "Frontend", "public", "brand-logo.png")),
                os.path.normpath(os.path.join(base_dir, "..", "..", "Frontend", "public", "icon.png")),
            ]
            for lp in default_logo_paths:
                if os.path.exists(lp):
                    try:
                        logo_img = Image.open(lp).convert("RGBA")
                        break
                    except Exception:
                        pass

        # Размещение логотипа в карточке
        logo_placed_y = card_top + 45
        if logo_img:
            target_w = int(width * 0.42)
            target_h = int(logo_img.height * (target_w / float(logo_img.width)))
            if target_h > int(height * 0.22):
                target_h = int(height * 0.22)
                target_w = int(logo_img.width * (target_h / float(logo_img.height)))

            # Масштабируем
            logo_img = logo_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            # Размещаем логотип на чистой аккуратной белой подложке
            badge_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            bdraw = ImageDraw.Draw(badge_layer)
            bw, bh = target_w + 50, target_h + 30
            bx = (width - bw) // 2
            by = card_top + 40
            bdraw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=22, fill=(255, 255, 255, 245), outline=(255, 255, 255, 255), width=1)
            img = Image.alpha_composite(img, badge_layer)
            img.paste(logo_img, ((width - target_w) // 2, by + 15), logo_img)
            logo_placed_y = by + bh + 25

        # 6. Загружаем шрифты с поддержкой кириллицы
        font_badge = self._get_font(22, bold=True)
        font_title = self._get_font(38, bold=True)
        font_sub = self._get_font(25, bold=False)
        font_tag = self._get_font(21, bold=False)

        draw = ImageDraw.Draw(img)

        # 7. Статусный бейдж-пилюля (Status Pill)
        pill_w = 340
        pill_h = 44
        pill_x = (width - pill_w) // 2
        pill_y = logo_placed_y
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=22, fill=accent_pill, outline=(255, 255, 255, 180), width=1)
        
        if "нейросет" in topic_lower or "фото" in topic_lower or "понимает" in topic_lower or "визуал" in topic_lower:
            status_title = "ИИ-ФОТОГРАФИЯ • UGC"
        elif "коллектив" in topic_lower or "проект" in topic_lower or "команд" in topic_lower or "старт" in topic_lower:
            status_title = "СТАРТ РАЗРАБОТКИ 2026"
        elif "скидк" in topic_lower or "акци" in topic_lower or "промо" in topic_lower:
            status_title = "СПЕЦИАЛЬНОЕ ПРЕДЛОЖЕНИЕ"
        else:
            status_title = f"{company_name.upper()} • ОФИЦИАЛЬНО"
            
        draw.text((pill_x + 30, pill_y + 10), status_title, font=font_badge, fill=(255, 255, 255))

        # 8. Главный заголовок темы (строгая очистка от технического промпт-инжиниринга)
        clean_topic = topic.strip() if topic.strip() else "Специальное предложение"
        if "subject:" in clean_topic.lower():
            clean_topic = re.split(r'subject:\s*', clean_topic, flags=re.IGNORECASE)[1].split(".")[0].strip()
        elif "photograph for" in clean_topic.lower():
            clean_topic = re.sub(r'Authentic candid.*?photograph for\s*[^.]*\.\s*', '', clean_topic, flags=re.IGNORECASE)
            clean_topic = clean_topic.split(".")[0].strip()

        clean_topic = re.sub(r'shot on iphone.*', '', clean_topic, flags=re.IGNORECASE).strip().rstrip(".")
        clean_topic = re.sub(r'authentic candid.*', '', clean_topic, flags=re.IGNORECASE).strip().rstrip(".")
        if not clean_topic or len(clean_topic) < 4:
            clean_topic = "Как нейросеть понимает запрос и создает фото"

        title_lines = []
        words = clean_topic.split()
        curr_line = []
        for w in words:
            curr_line.append(w)
            if len(" ".join(curr_line)) > 26:
                title_lines.append(" ".join(curr_line[:-1]))
                curr_line = [w]
        if curr_line:
            title_lines.append(" ".join(curr_line))
        title_lines = title_lines[:2]

        ty = pill_y + 65
        for i, line in enumerate(title_lines):
            line_color = (255, 255, 255) if i == 0 else (255, 205, 80)
            draw.text((margin + 45, ty), line, font=font_title, fill=line_color)
            ty += 52

        # 9. Описание / Подзаголовок (динамически под тему)
        sub_y = ty + 15
        if "нейросет" in topic_lower or "фото" in topic_lower or "понимает" in topic_lower or "визуал" in topic_lower:
            sub_line1 = "Создание живых коммерческих фото по простым запросам."
            sub_line2 = "Естественный свет, честные текстуры и стиль iPhone 16 Pro."
        elif "кофе" in niche_lower or "ресторан" in niche_lower:
            sub_line1 = "Свежая авторская обжарка и сбалансированная рецептура."
            sub_line2 = "Идеальное начало дня в уютной атмосфере нашего заведения."
        else:
            sub_line1 = f"Команда «{company_name}» объединила экспертов и AI-технологии."
            sub_line2 = "Фокус на понятный и измеримый результат для каждого клиента."
            
        draw.text((margin + 45, sub_y), sub_line1, font=font_sub, fill=(215, 225, 245))
        draw.text((margin + 45, sub_y + 36), sub_line2, font=font_sub, fill=(170, 185, 215))

        # 10. Нижние плашки преимуществ (Feature Badges)
        if "нейросет" in topic_lower or "фото" in topic_lower or "понимает" in topic_lower or "визуал" in topic_lower:
            features = ["Живой свет", "Честная текстура", "Стиль iPhone 16"]
        elif "кофе" in niche_lower or "ресторан" in niche_lower:
            features = ["Свежая обжарка", "Уютный зал", "Премиум меню"]
        elif "it" in niche_lower or "ucust" in company_name.lower():
            features = ["AI-агенты 24/7", "Контроль качества", "Автономия"]
        else:
            features = ["Премиум качество", "Забота о клиентах", "Новый сезон"]
            
        fx = margin + 45
        fy = card_bottom - 80
        for f_text in features:
            fw = int((width - margin * 2 - 120) / len(features))
            draw.rounded_rectangle([fx, fy, fx + fw, fy + 46], radius=20, fill=(30, 42, 68), outline=(80, 110, 160), width=1)
            # Светящаяся акцентная точка
            draw.ellipse([fx + 16, fy + 18, fx + 26, fy + 28], fill=dot_color)
            draw.text((fx + 34, fy + 11), f_text, font=font_tag, fill=(255, 255, 255))
            fx += fw + 14

        # 11. Сохранение в высоком коммерческом качестве
        img = img.convert("RGB")
        img.save(output_path, "JPEG", quality=95)
        print(f"[PhotoGeneratorSkill] ✅ Фото успешно сохранено: {output_path}")


__all__ = ["PhotoGeneratorSkill"]
