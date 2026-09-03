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

class CinematographyDirector:
    """
    Интеллектуальный режиссер-постановщик и арт-директор:
    Применяет профессиональные законы кинокомпозиции, световых схем,
    колористики и психологии восприятия кадра.
    """

    LIGHTING_SCHEMES = {
        "low_key": "Low-Key lighting with deep velvet shadows and high emotional drama",
        "high_key": "High-Key lighting with abundant soft luminous tones, airy and pristine",
        "chiaroscuro": "Chiaroscuro lighting, intense Renaissance contrast between glowing highlights and deep shadow",
        "silhouette": "Graceful dark silhouette against a radiant glowing background",
        "gobo_shadows": "Gobo light casting soft atmospheric window blind and botanical shadow patterns",
        "rim_backlight": "Golden hour Rim lighting / backlighting creating a glowing ethereal contour",
        "rembrandt": "Rembrandt lighting with subtle luminous triangle highlight on cheekbone",
        "paramount": "Paramount butterfly lighting defining facial cheekbones with elegant luxury",
        "spotlight": "Atmospheric warm golden spotlight isolating the subject against dark ambient room",
        "lens_flare": "Subtle warm lens flares and sunbeams, nostalgic indie film aesthetic",
        "soft_diffused": "Soft diffused morning window daylight with gentle natural gradients"
    }

    COLOR_HARMONIES = {
        "teal_orange": "Teal and Orange cinematic color harmony, warm golden subject tones separated from cool background",
        "warm_analogous": "Warm analogous palette of honey, amber, terracotta and roasted gold",
        "complementary": "Dynamic complementary color contrast creating vibrant visual energy",
        "muted_editorial": "Refined desaturated muted color palette with timeless editorial sophistication",
        "monochrome": "Timeless monochromatic tones emphasizing raw texture, geometry and emotion"
    }

    COMPOSITION_GEOMETRIES = {
        "rule_of_thirds": "Rule of Thirds composition with key visual weight on dynamic power intersection points",
        "symmetry": "Cinematic centered symmetrical framing with Wes Anderson precision and balance",
        "leading_lines": "Dynamic leading lines guiding the viewer's eye seamlessly into the focal subject",
        "framing": "Natural architectural framing through doorway, window arch or soft foliage",
        "negative_space": "Expansive negative space creating a high-end minimalist, breathable composition",
        "triangles": "Stable triangular geometry balancing masses and creating visual permanence",
        "golden_spiral": "Golden ratio Fibonacci spiral naturally drawing focus into the scene center"
    }

    PERSPECTIVES = {
        "bokeh_shallow": "Shallow depth of field (f/1.4), creamy bokeh background isolation",
        "low_angle_heroic": "Low-angle heroic perspective conveying confidence, scale and mastery",
        "tabletop_commercial": "Top-down / 45-degree angled tabletop commercial perspective with rich tactile textures",
        "candid_eye_level": "Natural eye-level 35mm perspective, clean editorial commercial photography"
    }

    NICHE_EN_MAP = {
        "электроник": "electronics and embedded IoT hardware",
        "it": "modern IT software and digital technology",
        "кофейн": "craft specialty coffee shop",
        "кофе": "specialty coffee and espresso bar",
        "ресторан": "fine dining gourmet restaurant",
        "пекарн": "artisan bakery and pastry shop",
        "кондитерск": "pastry confectionery and dessert boutique",
        "авто": "luxury automotive detailing and workshop",
        "мебел": "high-end designer handcrafted furniture",
        "стоматолог": "modern pristine dental clinic",
        "медицин": "modern healthcare and wellness clinic",
        "фитнес": "state-of-the-art loft fitness gym",
        "спорт": "athletic sports and workout lifestyle",
        "ремонт": "architectural interior renovation and design",
        "недвижим": "luxury contemporary real estate",
        "юриспруд": "prestigious corporate law firm",
        "бьюти": "modern sunlit beauty and aesthetics salon",
        "зоо": "cozy pet boutique and veterinary care",
        "животн": "warm cozy pet lifestyle setting with beloved animals",
        "кот": "warm cozy sunlit living room with charming playful domestic cats",
        "собак": "vibrant outdoor park with joyful well-trained dogs",
        "религи": "historic sacred cultural architecture with stained glass and candle glow",
        "церков": "peaceful historic cathedral with serene architectural beauty",
        "бизнес": "contemporary creative professional studio",
        "услуг": "modern professional service workspace"
    }

    @classmethod
    def compose_cinematic_prompt(
        cls,
        topic: str,
        niche: str = "бизнес",
        brand_colors: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Генерирует высокохудожественный промпт для ComfyUI Realism 2.0
        с учетом психологии света, композиции и цвета.
        """
        topic_lower = topic.lower()
        niche_lower = (niche or "").lower()

        # Определение англоязычного контекста ниши
        niche_en = "professional commercial environment"
        for k, v in cls.NICHE_EN_MAP.items():
            if k in niche_lower or k in topic_lower:
                niche_en = v
                break

        # 1. Анализ сюжета и определение световой схемы
        if "закат" in topic_lower or "пляж" in topic_lower or "вечер" in topic_lower:
            light_key = "rim_backlight"
            color_key = "teal_orange"
            comp_key = "rule_of_thirds"
            persp_key = "bokeh_shallow"
        elif "неон" in topic_lower or "приват" in topic_lower or "клуб" in topic_lower or "бар" in topic_lower:
            light_key = "low_key"
            color_key = "complementary"
            comp_key = "negative_space"
            persp_key = "candid_eye_level"
        elif "массаж" in topic_lower or "spa" in topic_lower or "спа" in topic_lower or "камн" in topic_lower:
            light_key = "soft_diffused"
            color_key = "warm_analogous"
            comp_key = "framing"
            persp_key = "bokeh_shallow"
        elif "десерт" in topic_lower or "ролл" in topic_lower or "выпечк" in topic_lower or "кофе" in topic_lower or "еда" in topic_lower or "кулич" in topic_lower or "огурец" in topic_lower or "плата" in topic_lower or "esp" in topic_lower or "электроник" in topic_lower or "микроконтроллер" in topic_lower or "турбин" in topic_lower or "инструмент" in topic_lower or "ювелир" in topic_lower or "кольц" in topic_lower or "косметик" in topic_lower or "крем" in topic_lower:
            light_key = "high_key"
            color_key = "warm_analogous"
            comp_key = "golden_spiral"
            persp_key = "tabletop_commercial"
        elif "флаг" in topic_lower or "архитектур" in topic_lower or "спорт" in topic_lower or "фитнес" in topic_lower:
            light_key = "rim_backlight"
            color_key = "teal_orange"
            comp_key = "triangles"
            persp_key = "low_angle_heroic"
        else:
            light_key = "soft_diffused"
            color_key = "muted_editorial"
            comp_key = "rule_of_thirds"
            persp_key = "candid_eye_level"

        # 2. Интеллектуальный поиск точной спецификации одежды / объекта через VisualKnowledgeResearcher
        from skills.visual_knowledge_researcher import VisualKnowledgeResearcher
        visual_spec = VisualKnowledgeResearcher.research_visual_spec_sync(topic)

        # Динамическая сборка объекта с переводом сущностей на чистый английский
        if "массаж" in topic_lower or "камн" in topic_lower:
            subject = visual_spec.get("visual_description", "serene relaxing hot stone back massage SPA treatment, smooth black basalt stones placed along spine, aromatic botanical oils glistening")
            environment = "peaceful luxury wellness SPA room, marble surface, soft warm candlelight and towels in soft focus"
        elif "бикини" in topic_lower or "стринги" in topic_lower or "купальник" in topic_lower or "модел" in topic_lower:
            garment_desc = visual_spec.get("visual_description", "elegant stylish minimalist swimwear")
            if "пляж" in topic_lower or "закат" in topic_lower:
                subject = f"athletic graceful young female model posing naturally, wearing {garment_desc}"
                environment = "breathtaking golden hour ocean shoreline, gentle turquoise waves in soft background bokeh, warm sea breeze"
            else:
                subject = f"captivating charismatic female model posing with poise and elegance, wearing {garment_desc}"
                environment = "moody luxury penthouse lounge with soft neon ambient reflections, subtle velvet textures, cinematic depth"
        elif "плата" in topic_lower or "esp32" in topic_lower or "esp-32" in topic_lower or "ардуино" in topic_lower or "arduino" in topic_lower or "микроконтроллер" in topic_lower or "чип" in topic_lower:
            subject = visual_spec.get("visual_description", f"extreme macro product photography of compact ESP-32 microcontroller board")
            environment = "clean high-tech electronics engineering workbench, blue anti-static silicone soldering mat, precision tweezers and fine copper wires in soft background bokeh, tabletop macro focus"
        elif "кот" in topic_lower or "кошк" in topic_lower or "котик" in topic_lower:
            subject = "charming fluffy domestic tabby cat with expressive amber eyes resting peacefully on a warm wooden surface"
            environment = "cozy sunlit living room with natural house plants, soft warm window sunlight in background bokeh"
        elif "собак" in topic_lower or "щен" in topic_lower:
            subject = "healthy energetic loyal dog with shining fur looking curiously at the camera"
            environment = "bright sunlit green park with gentle golden hour sunbeams and lush grass"
        elif "кулич" in topic_lower or "пасх" in topic_lower:
            subject = "traditional artisanal glazed Easter brioche cake with delicate sugar icing, pastel sugar sprinkles and spring floral garnish"
            environment = "rustic wooden table with natural linen napkin, warm soft window daylight"
        elif "кофе" in topic_lower or "эфиопи" in topic_lower or "капучин" in topic_lower:
            subject = "artisanal ceramic cup of creamy cappuccino with intricate latte art, fresh ripe peach slice and delicate white jasmine flowers on saucer"
            environment = "cozy sunlit craft specialty coffee shop, warm rustic oak table"
        elif "крем" in topic_lower or "сыворотк" in topic_lower or "помад" in topic_lower or "блеск для губ" in topic_lower or "косметик" in topic_lower:
            subject = visual_spec.get("visual_description", f"luxury commercial cosmetic product display")
            environment = "minimalist luxury travertine marble stone podium, delicate fresh water droplets, soft botanical accents in blurred background, clean studio aesthetic"
        elif "турбин" in topic_lower or "gt2871" in topic_lower or "койловер" in topic_lower or "перфоратор" in topic_lower or "шуруповерт" in topic_lower or "инструмент" in topic_lower:
            subject = visual_spec.get("visual_description", f"precision tabletop commercial photograph of professional engineering component")
            environment = "clean professional workshop table, cedar wood shavings and blueprint schematics in soft background bokeh, authentic craftsmanship"
        else:
            raw_vis = visual_spec.get("visual_description")
            subject = f"authentic candid commercial scene: {raw_vis}" if raw_vis and raw_vis != topic else f"authentic commercial scene representing {niche_en}"
            environment = f"aesthetic contemporary {niche_en} setting, natural room depth"

        lighting = cls.LIGHTING_SCHEMES[light_key]
        color_scheme = cls.COLOR_HARMONIES[color_key]
        composition = cls.COMPOSITION_GEOMETRIES[comp_key]
        perspective = cls.PERSPECTIVES[persp_key]

        colors_str = f"Brand palette accents: {', '.join(brand_colors)}. " if brand_colors else ""

        # Дифференцируем текстурные дескрипторы: кожа для людей, фактура материала для предметов/еды/плат/животных
        is_human_scene = any(w in topic_lower or w in subject.lower() for w in ["человек", "девушк", "модел", "парень", "мужчин", "женщин", "лицо", "портрет", "мастер", "доктор", "врач", "тренер", "студент", "бариста", "юрист", "model", "woman", "man", "person", "barista", "doctor"]) and not any(w in topic_lower for w in ["плата", "esp32", "esp-32", "arduino", "чип", "десерт", "стейк", "турбин", "перфоратор", "кот", "кошк", "собак"])
        
        texture_desc = "natural skin texture, authentic pores, genuine human expression" if is_human_scene else "tactile surface texture, crisp micro-details, pristine material finish, macro lens clarity"

        full_prompt = (
            f"Authentic commercial photograph for {niche_en}. "
            f"Subject: {subject}. "
            f"Environment: {environment}. "
            f"{colors_str}"
            f"Lighting & Atmosphere: {lighting}. "
            f"Color Harmony: {color_scheme}. "
            f"Composition & Framing: {composition}. "
            f"Perspective & Optics: {perspective}, 35mm film masterpiece, fine tactile detail, Hasselblad color science, uncompressed raw photo, {texture_desc}, tactile realism, natural grain, photorealistic."
        )

        return {
            "prompt": full_prompt,
            "lighting_scheme": light_key,
            "color_harmony": color_key,
            "composition": comp_key,
            "perspective": persp_key
        }


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
            "subject": "smiling friendly barista leaning over rustic wooden counter, gently handing a steaming artisanal ceramic cup of cappuccino with delicate latte art directly toward viewer",
            "environment": "cozy local craft coffee shop, large sunlit window with soft floating dust motes, relaxed warm background",
            "lighting": "natural soft ambient morning daylight from window, warm gentle golden tones, realistic room shadows",
            "camera": "Cinematic 35mm film look, natural handheld eye-level angle, candid smartphone photo, unedited Apple ProRAW look, emotional warmth"
        },
        "ресторан": {
            "subject": "passionate focused chef in dark apron using precision tweezers to place delicate garnish onto gourmet signature dish in warm open kitchen",
            "environment": "warm inviting bistro with ambient dining room in soft bokeh, polished glassware, fine dining atmosphere",
            "lighting": "warm golden spotlight on culinary masterpiece, soft candle and ambient dining glow",
            "camera": "Cinematic 35mm photography, natural tabletop angle, candid culinary passion, realistic foodie storytelling"
        },
        "красота": {
            "subject": "radiant client with a genuine glowing smile looking into sunlit salon mirror admiring fresh stylish hair and makeup, caring stylist smiling proudly behind her",
            "environment": "sunlit modern beauty salon, marble vanity shelf, delicate green eucalyptus in soft background",
            "lighting": "bright clean natural morning daylight, soft diffused window glow, fresh organic radiance",
            "camera": "Cinematic lifestyle beauty shot, authentic UGC texture, genuine emotion of confidence and self-love"
        },
        "it": {
            "subject": "focused passionate developer or founder leaning back with a relieved happy smile after successful project milestone, laptop on desk with clean editor",
            "environment": "bright minimalist home office or loft coworking, indoor potted plant, cozy ambient desk setup",
            "lighting": "natural ambient daylight from nearby window, soft warm desk lamp accent",
            "camera": "Cinematic desk point-of-view, authentic candid tech lifestyle photo, unedited RAW look, genuine human accomplishment"
        },
        "фитнес": {
            "subject": "dedicated athlete taking a deep breath of triumph after an intense workout in modern loft gym, holding water bottle with sunlight highlighting determination",
            "environment": "modern spacious gym, motivational athletic loft environment, wooden bench",
            "lighting": "warm golden morning sunbeams piercing through high gym windows, dramatic authentic highlights",
            "camera": "Dynamic candid smartphone angle, authentic workout lifestyle photo, raw emotion of self-overcoming"
        },
        "авто": {
            "subject": "skilled detailing specialist in black gloves gently running fingertips across mirror-like glossy hood of sports car, admiring flawless reflection",
            "environment": "clean modern workshop with soft LED strip lighting, reflections on glossy paint",
            "lighting": "natural golden hour light, realistic reflections on paint, dramatic workshop contrasts",
            "camera": "Cinematic automotive photography, candid automotive enthusiast passion, authentic craftsmanship"
        },
        "недвижимость": {
            "subject": "happy young homeowner sitting comfortably on warm hardwood floor of airy sunlit living room with coffee mug, gazing out panoramic window at city sunset",
            "environment": "modern newly finished apartment interior, floor-to-ceiling panoramic windows, potted plant nearby",
            "lighting": "bright warm afternoon sunbeams, airy room daylight, golden sunset glow",
            "camera": "Cinematic wide architectural photography, authentic new home celebration, pure happiness and safety"
        },
        "одежда": {
            "subject": "stylish woman in front of warm boutique mirror playfully adjusting collar of chic elegant coat with confident joyful smile",
            "environment": "bright aesthetic boutique dressing area, minimalist aesthetic clothing rack in soft background",
            "lighting": "soft natural window light, subtle room shadows, true fabric colors",
            "camera": "Casual candid mirror photo, authentic fashion UGC aesthetic, delight in personal style"
        },
        "медицина": {
            "subject": "caring friendly doctor in clean white coat having warm empathetic conversation with smiling relieved patient, genuine trust and safety",
            "environment": "bright modern consultation room with wood and green plant accents, welcoming atmosphere",
            "lighting": "soft bright diffused natural light, calm trustworthy and reassuring atmosphere",
            "camera": "Natural eye-level perspective, authentic candid healthcare photo, relief and care"
        },
        "ремонт": {
            "subject": "architect and proud homeowner standing together in finished open-plan room looking at blueprints with genuine satisfaction and pride",
            "environment": "spacious newly renovated living room, warm hardwood flooring, designer lighting",
            "lighting": "bright warm natural window daylight, gentle realistic interior shadows",
            "camera": "Wide angle lens, authentic interior design storytelling photo, crisp architectural details"
        },
        "образование": {
            "subject": "focused inspired student in headphones experiencing breakthrough moment of excitement while taking notes next to laptop by sunny window",
            "environment": "bright modern library or student coworking corner, organized learning space",
            "lighting": "natural sunny window light, soft warm ambiance, inspiring study mood",
            "camera": "Tabletop angle, authentic study lifestyle photo, intellectual growth and ambition"
        },
        "туризм": {
            "subject": "traveler wrapped in cozy blanket holding steaming mug of tea sitting on edge of wooden glamping deck watching golden sunrise over misty mountains",
            "environment": "scenic mountain or lake view at golden hour, breathtaking tranquil nature background",
            "lighting": "warm golden sunrise glow, soft mountain atmosphere, peaceful awe and tranquility",
            "camera": "Wide scenic view, authentic travel photography, natural rich colors, deep emotional peace"
        },
        "юриспруденция": {
            "subject": "two business partners firmly shaking hands across modern conference table at sunset after signing crucial contract, mutual respect and relief",
            "environment": "bright contemporary law firm or consulting office, large panoramic window with city view",
            "lighting": "crisp natural office daylight, warm golden hour accents, trustworthy and authoritative",
            "camera": "Professional desk perspective, authentic corporate lifestyle storytelling photo, confidence and success"
        },
        "праздник": {
            "subject": "cheerful professional team or person raising a warm toast or smiling genuinely in celebration by sunlit window with festive seasonal accent",
            "environment": "warm sunlit modern office, cheerful inspiring celebratory atmosphere",
            "lighting": "warm golden daylight, soft festive background bokeh",
            "camera": "Authentic candid commercial photo, shallow depth of field, genuine celebration and connection"
        },
        "флаг": {
            "subject": "focused professional in elegant silhouette standing at lower right looking up in awe, colossal majestic Russian tricolor flag fluttering grandly and powerfully on towering flagpole dominating upper sky",
            "environment": "modern high-rise glass office by panoramic window, dramatic glowing golden sunset sky and clouds",
            "lighting": "warm golden sunbeams through clouds, brilliant golden rim lighting on silhouette, soft window reflections",
            "camera": "Heroic dramatic low-angle upward perspective (shot from below looking up), cinematic 35mm film masterpiece, monumental scale and grandeur"
        },
        "услуги": {
            "subject": "passionate dedicated professional deeply engaged in their craft at modern sunlit workstation, genuine focus, pride and mastery",
            "environment": "sunlit contemporary creative workspace or bright meeting room, productive human atmosphere",
            "lighting": "natural window daylight, soft warm room ambient, golden highlights",
            "camera": "Casual tabletop angle, authentic business lifestyle storytelling photo"
        },
        "рынок": {
            "subject": "rustic weathered wooden market crate overflowing with vibrant ripe red tomatoes and crisp fresh herbs, dewdrops glistening in morning sun",
            "environment": "authentic bustling organic farmers market with natural canvas awnings, warm rustic atmosphere",
            "lighting": "golden morning sunshine streaming through market stalls, rich natural warmth",
            "camera": "Top-down / angled tabletop commercial food photography, crisp appetizing textures, shallow depth of field"
        },
        "приват": {
            "subject": "captivating charismatic creator in subtle ambient neon and candlelight, striking aesthetic silhouette, confident playful gaze",
            "environment": "stylish moody modern penthouse lounge or aesthetic cozy studio room with velvet textures",
            "lighting": "moody cinematic rim lighting, warm candle glow, subtle deep shadows and atmospheric highlights",
            "camera": "Cinematic 35mm portrait, intimate artistic depth of field"
        }
    }

    DEFAULT_NEGATIVE_PROMPT = (
        "smartphone, phone screen, holding smartphone, camera UI, viewfinder, bezel, device mockup, "
        "staged studio photoshoot, heavy artificial studio strobes, studio softboxes, plastic skin, "
        "nsfw, nude, naked, explicit, bad anatomy, deformed fingers, extra limbs, blurry face, bad eyes, "
        "low quality, oversaturated, plastic 3d render, watermark, text, signature"
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
        style: str = "candid_iphone",
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Составляет высокохудожественный промпт для ComfyUI через CinematographyDirector.
        """
        if custom_prompt and len(custom_prompt.strip()) > 30 and not custom_prompt.startswith("Authentic candid photo of a small tech") and not custom_prompt.startswith("Cinematic emotional culinary"):
            positive_prompt = custom_prompt
        else:
            cinematic_res = CinematographyDirector.compose_cinematic_prompt(
                topic=topic,
                niche=niche,
                brand_colors=brand_colors
            )
            positive_prompt = cinematic_res["prompt"]

        dimensions = self.ASPECT_RATIOS.get(aspect_ratio, self.ASPECT_RATIOS["1:1"])

        print(f"\n[PhotoGeneratorSkill] 📸 Сформирован промпт для ComfyUI (Ниша: {niche}):\n  👉 {positive_prompt}\n")

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
        attachments: Optional[List[Any]] = None,
        custom_prompt: Optional[str] = None
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
        if custom_prompt:
            prompt_data["positive_prompt"] = custom_prompt
            print(f"[PhotoGeneratorSkill] 🎯 Использован контекстный промпт от Копирайтера:\n  👉 {custom_prompt}\n")

        photo_id = f"photo_{uuid.uuid4().hex[:10]}"
        filename = f"{photo_id}.jpg"
        file_path = os.path.join(self.output_dir, filename)

        rendered_via_comfy = False
        # 1. Попытка рендера через ComfyUI API / CLI runner (Realism 2.0)
        try:
            from skills.comfy_cli_runner import ComfyCLIRunner
            comfy_runner = ComfyCLIRunner(output_dir=self.output_dir)
            if await comfy_runner.is_server_online():
                has_images = bool(attachments and len(attachments) > 0)
                mode_str = "Edit Mode (True) с апскейлом референсов" if has_images else "Generation Mode (False) с нуля из шума"
                print(f"[PhotoGeneratorSkill] ⚡ ComfyUI (127.0.0.1:8188) онлайн — запуск Realism 2.0 воркфлоу ({mode_str})...")
                res_comfy = await comfy_runner.execute_workflow(
                    photo_prompt=prompt_data["positive_prompt"],
                    raw_topic=topic,
                    negative_prompt=prompt_data["negative_prompt"],
                    aspect_ratio=aspect_ratio,
                    attachments=attachments,
                    edit_mode=has_images
                )
                if res_comfy.get("photo_path") and os.path.exists(res_comfy["photo_path"]) and os.path.getsize(res_comfy["photo_path"]) > 100:
                    file_path = res_comfy["photo_path"]
                    filename = os.path.basename(file_path)
                    rendered_via_comfy = True
            else:
                print("[PhotoGeneratorSkill] ⚠️ Сервер ComfyUI оффлайн (127.0.0.1:8188 недоступен). Используется встроенный брендовый баннер...")
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
