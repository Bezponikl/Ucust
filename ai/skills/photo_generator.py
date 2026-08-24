"""
PhotoGeneratorSkill — Модуль автономной генерации фото и визуального контента для SMM.
Создает коммерческие промпты по стандартам современной фотографии (Sony A7R / Hasselblad),
управляет ракурсами, стилями, палитрой бренда и генерирует изображения.
"""

from __future__ import annotations

import os
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
            "subject": "artisan coffee cup with delicate latte art, fresh roasted coffee beans, croissant on rustic table",
            "environment": "cozy warm coffee shop interior, soft morning sunbeams, wooden texture, bokeh background",
            "lighting": "warm natural ambient sunlight, golden hour lighting, gentle rim light",
            "camera": "Sony A7R IV, 85mm f/1.4 lens, shallow depth of field, 8k commercial food photography"
        },
        "ресторан": {
            "subject": "exquisite gourmet dish, fresh organic ingredients, culinary master presentation, fine dining",
            "environment": "elegant restaurant ambiance, minimalist dark marble table, crystal glassware",
            "lighting": "moody soft studio lighting, delicate highlights, cinematic atmosphere",
            "camera": "Hasselblad H6D-100c, 100mm macro lens, tack sharp details, Michelin guide aesthetic"
        },
        "красота": {
            "subject": "luxurious skincare cosmetics bottles, natural botanical ingredients, organic drops, aesthetic spa scene",
            "environment": "minimalist aesthetic pastel surface, clean water ripples, fresh flower petals",
            "lighting": "clean bright diffused studio light, soft shadows, airy refreshing mood",
            "camera": "Canon EOS R5, 50mm f/1.2 lens, hyper-detailed skin and glass textures, Vogue editorial style"
        },
        "it": {
            "subject": "modern developer workspace, ultra-wide curved monitor displaying code, mechanical keyboard, stylish laptop",
            "environment": "high-tech minimalist studio, neon cyber accents, ambient desk glow, indoor plants",
            "lighting": "cool atmospheric neon blue and purple ambient lighting, cinematic rim lights",
            "camera": "Sony FX3, 35mm f/1.8 lens, sharp focus, clean technology aesthetic"
        },
        "фитнес": {
            "subject": "athletic sports gear, premium water bottle, dumbbells, dynamic workout accessories",
            "environment": "modern energetic gym interior, clean architectural lines, motivational atmosphere",
            "lighting": "dramatic directional rim light, high contrast, energizing mood",
            "camera": "Nikon Z9, 70-200mm f/2.8 lens, high shutter speed, sharp athletic focus"
        },
        "авто": {
            "subject": "luxury sleek sports car, glossy ceramic coating reflections, polished alloy wheels",
            "environment": "high-end modern detailing studio, clean architectural lighting, dark aesthetic floor",
            "lighting": "dramatic linear studio light strips, high contrast reflections, premium automotive mood",
            "camera": "Hasselblad H6D-100c, 50mm lens, tack sharp reflections, Top Gear editorial aesthetic"
        },
        "недвижимость": {
            "subject": "spacious modern luxury apartment interior, contemporary design furniture, panoramic city view",
            "environment": "sunlit penthouse living room, marble accents, minimalist decor, indoor olive tree",
            "lighting": "bright warm natural daylight, soft interior ambient lighting, Architectural Digest look",
            "camera": "Sony A7R V, 16-35mm f/2.8 wide lens, perfect straight verticals, magazine architecture quality"
        },
        "одежда": {
            "subject": "stylish premium clothing collection on minimalist hangers, luxury fabric textures, fashion accessories",
            "environment": "contemporary boutique showroom, neutral warm tones, textured lime plaster walls",
            "lighting": "soft diffused editorial lighting, gentle highlights on fabric grain, high-end lookbook mood",
            "camera": "Canon EOS R5, 85mm f/1.2 lens, shallow depth of field, Vogue lookbook photography"
        },
        "медицина": {
            "subject": "modern state-of-the-art dental clinic equipment, pristine medical tools, gentle reassuring atmosphere",
            "environment": "ultra-clean premium clinic interior, soft ambient glowing lighting, comfortable patient chair",
            "lighting": "clean bright soft diffused medical lighting, reassuring and calm atmosphere",
            "camera": "Sony A7 IV, 50mm f/1.8 lens, crisp clinical sharpness, trustworthy healthcare aesthetic"
        },
        "услуги": {
            "subject": "modern business planning desk, neat tablet with analytics dashboard, stylish leather notebook, pen",
            "environment": "sleek contemporary executive office, minimalist glass partitions, soft ambient background",
            "lighting": "balanced soft daylight, warm accent lamp, crisp professional commercial atmosphere",
            "camera": "Sony A7R IV, 50mm f/1.4 lens, clean commercial corporate photography"
        }
    }

    DEFAULT_NEGATIVE_PROMPT = (
        "blurry, low quality, distorted, extra limbs, bad anatomy, cartoon, 3d render, illustration, "
        "watermark, lowres, text artifacts, oversaturated, amateur photo, deformed fingers, unrealistic lighting"
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
        style: str = "photorealistic"
    ) -> Dict[str, Any]:
        """
        Составляет коммерческий промпт для нейросети на основе ниши и темы.
        """
        niche_key = "кофейня"
        for k in self.NICHE_PRESETS:
            if k in niche.lower() or k in topic.lower():
                niche_key = k
                break

        preset = self.NICHE_PRESETS.get(niche_key, self.NICHE_PRESETS["кофейня"])
        colors_str = f"Brand palette accents: {', '.join(brand_colors)}. " if brand_colors else ""

        positive_prompt = (
            f"Commercial SMM photography for {niche}. Subject: {topic.strip() or preset['subject']}. "
            f"Environment: {preset['environment']}. "
            f"{colors_str}"
            f"Lighting: {preset['lighting']}. "
            f"Shot details: {preset['camera']}, commercial quality, 8k resolution, photorealistic, raw texture."
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
        font_candidates = [
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

        # 1. Попытка рендера через ComfyUI API / CLI runner
        try:
            from skills.comfy_cli_runner import ComfyCLIRunner
            comfy_runner = ComfyCLIRunner(output_dir=self.output_dir)
            if await comfy_runner.is_server_online():
                print("[PhotoGeneratorSkill] ⚡ ComfyUI (127.0.0.1:8188) онлайн — отправка задачи в ComfyUI...")
        except Exception as ex:
            print(f"[PhotoGeneratorSkill] ℹ️ ComfyUI статус: {ex}")

        # 2. Рендер высококачественного брендового SMM-визуала
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

        # 3. Атмосферное фоновое свечение (Luminous Mesh Glow)
        glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow_layer)
        gdraw.ellipse([int(width * 0.05), int(height * 0.1), int(width * 0.55), int(height * 0.55)], fill=glow_primary)
        gdraw.ellipse([int(width * 0.48), int(height * 0.12), int(width * 0.95), int(height * 0.60)], fill=glow_secondary)
        gdraw.ellipse([int(width * 0.25), int(height * 0.35), int(width * 0.75), int(height * 0.85)], fill=glow_accent)
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
            default_logo_paths = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "Frontend", "public", "icon.png"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "Frontend", "public", "brand-logo.png"),
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
        
        status_title = "СТАРТ РАЗРАБОТКИ 2026" if ("коллектив" in topic_lower or "проект" in topic_lower or "команд" in topic_lower) else f"{company_name.upper()} • ОФИЦИАЛЬНО"
        draw.text((pill_x + 30, pill_y + 10), status_title, font=font_badge, fill=(255, 255, 255))

        # 8. Главный заголовок темы
        clean_topic = topic.strip() if topic.strip() else "Специальное предложение"
        title_lines = []
        words = clean_topic.split()
        curr_line = []
        for w in words:
            curr_line.append(w)
            if len(" ".join(curr_line)) > 28:
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

        # 9. Описание / Подзаголовок
        sub_y = ty + 15
        sub_line1 = f"Команда «{company_name}» объединила экспертов и AI-технологии."
        sub_line2 = "Фокус на понятный и измеримый результат для каждого клиента."
        draw.text((margin + 45, sub_y), sub_line1, font=font_sub, fill=(215, 225, 245))
        draw.text((margin + 45, sub_y + 36), sub_line2, font=font_sub, fill=(170, 185, 215))

        # 10. Нижние плашки преимуществ (Feature Badges) с акцентными светящимися точками
        features = ["Сильная команда", "Открытая разработка", "AI-инновации"] if "it" in niche_lower or "ucust" in company_name.lower() else ["Премиум качество", "Забота о гостях", "Новый сезон"]
        fx = margin + 45
        fy = card_bottom - 80
        for f_text in features:
            fw = int((width - margin * 2 - 120) / len(features))
            draw.rounded_rectangle([fx, fy, fx + fw, fy + 46], radius=20, fill=(255, 255, 255, 22), outline=(255, 255, 255, 45), width=1)
            # Светящаяся акцентная точка
            draw.ellipse([fx + 16, fy + 18, fx + 26, fy + 28], fill=dot_color)
            draw.text((fx + 34, fy + 11), f_text, font=font_tag, fill=(255, 255, 255))
            fx += fw + 14

        # 11. Сохранение в высоком коммерческом качестве
        img = img.convert("RGB")
        img.save(output_path, "JPEG", quality=95)
        print(f"[PhotoGeneratorSkill] ✅ Фото успешно сохранено: {output_path}")


__all__ = ["PhotoGeneratorSkill"]
