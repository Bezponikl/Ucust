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
        "low_key": "Low-key natural directional light with deep ambient shadows",
        "high_key": "Soft natural daylight illumination, airy ambient light",
        "chiaroscuro": "Strong directional side lighting with deep natural shadows",
        "silhouette": "Natural backlit contour against bright background",
        "gobo_shadows": "Natural window shadow patterns across the scene",
        "rim_backlight": "Natural backlighting contour and subtle rim glow",
        "rembrandt": "Dramatic directional side lighting, deep micro-shadows",
        "paramount": "Gentle overhead light defining facial planes",
        "spotlight": "Warm direct task light illuminating the subject",
        "lens_flare": "Subtle optical lens flare, organic light leak",
        "soft_diffused": "Soft diffused morning window daylight with gentle natural gradients"
    }

    COLOR_HARMONIES = {
        "teal_orange": "Natural daylight with subtle warm subject tones against cool ambient background",
        "warm_analogous": "Natural warm daylight and organic earthy materials",
        "complementary": "Natural color contrast between subject and background",
        "muted_editorial": "Natural authentic color reproduction, un-graded RAW tones",
        "monochrome": "Natural monochrome black and white analog film tones"
    }

    COMPOSITION_GEOMETRIES = {
        "rule_of_thirds": "Rule of thirds framing with subject placed on natural focal points",
        "symmetry": "Balanced centered framing",
        "leading_lines": "Natural leading lines through the environment",
        "framing": "Natural framing through environmental elements",
        "negative_space": "Uncluttered composition with natural negative space",
        "triangles": "Natural triangular arrangement of scene elements",
        "golden_spiral": "Natural flowing compositional curve guiding the eye"
    }

    PERSPECTIVES = {
        "bokeh_shallow": "Shallow depth of field (f/1.4), anamorphic background bokeh",
        "low_angle_heroic": "Slightly low-angle natural eye-level perspective",
        "tabletop_commercial": "45-degree angle tabletop view with tactile material focus",
        "candid_eye_level": "35mm lens, candid natural eye-level perspective",
        "culinary_macro_eyelevel": "35mm close-up macro lens perspective, f/2.8 shallow depth of field",
        "culinary_flatlay_topdown": "Direct top-down 90-degree overhead perspective",
        "culinary_45_slice": "45-degree angled perspective with crisp focal depth"
    }

    NICHE_EN_MAP = {
        "martech": "innovative AI MarTech software platform and digital marketing analytics",
        "маркетинг": "modern AI marketing automation and growth analytics platform",
        "saas": "cutting-edge cloud SaaS software and AI intelligence enterprise",
        "it": "modern high-tech IT software and artificial intelligence enterprise",
        "ии": "modern artificial intelligence and machine learning technology",
        "электроник": "electronics and embedded IoT hardware",
        "кофейн": "craft specialty coffee shop",
        "кофе": "specialty coffee and espresso bar",
        "ресторан": "fine dining gourmet restaurant",
        "пекарн": "artisan bakery and pastry shop",
        "кондитерск": "pastry confectionery and dessert boutique",
        "детейлинг": "luxury automotive detailing and ceramic studio",
        "автомобил": "modern automotive showroom and engineering workshop",
        "автосервис": "professional auto repair and diagnostic bay",
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
        "цвет": "charming Parisian floral boutique and botanical atelier",
        "флорист": "artisan floral design studio and botanical boutique",
        "букет": "luxury artisan flower atelier with fresh dewy blooms",
        "посуд": "high-end artisanal ceramic, fine porcelain and tableware boutique",
        "фарфор": "luxury fine porcelain, bone china and handcrafted ceramic salon",
        "керамик": "artisan pottery and handcrafted ceramic studio",
        "бизнес": "contemporary creative professional studio",
        "услуг": "modern professional service workspace"
    }

    @classmethod
    def compose_cinematic_prompt(
        cls,
        topic: str,
        niche: str = "бизнес",
        brand_colors: Optional[List[str]] = None,
        variation_index: int = 0,
        routing: Optional[Any] = None
    ) -> Dict[str, str]:
        """
        Генерирует высокохудожественный промпт для ComfyUI Realism 2.0
        с учетом психологии света, композиции, цвета и номера перегенерации (variation_index).
        """
        topic_lower = topic.lower()
        niche_lower = (niche or "").lower()
        var = variation_index % 4

        # Предотвращение Semantic Bleed: если в теме указана конкретная предметная область, она имеет наивысший приоритет
        domain_priority = ["цвет", "флорист", "букет", "пион", "посуд", "фарфор", "керамик", "глинян", "гончар", "кофе", "пекарн", "десерт", "электроник", "плата", "кот", "собак", "детейлинг", "стоматолог", "недвижим", "it", "saas", "martech"]
        effective_niche_key = None
        for k in domain_priority:
            if k in topic_lower:
                effective_niche_key = k
                break
        if not effective_niche_key:
            for k in domain_priority:
                if k in niche_lower:
                    effective_niche_key = k
                    break

        niche_en = cls.NICHE_EN_MAP.get(effective_niche_key, "professional commercial environment") if effective_niche_key else "professional commercial environment"

        # =========================================================================
        # ПИЛАР 1: АУТЕНТИЧНЫЙ МИР И СФЕРА ДЕЯТЕЛЬНОСТИ (Niche World-Building)
        # При перегенерации (var > 0) интерьер, окружение и реквизит циклически меняются!
        # =========================================================================
        niche_environments = {
            "martech": [
                {"setting": "sleek contemporary tech startup headquarters with glass partition walls and panoramic city skyline view", "props": "ultra-thin laptop with glowing analytics dashboard, minimal glass table, modern architectural daylight"},
                {"setting": "modern sunlit open-plan digital innovation lab with minimalist Scandinavian oak desks", "props": "sleek monitors displaying real-time AI conversion charts, potted indoor plants, bright productive ambiance"},
                {"setting": "futuristic executive tech boardroom at golden hour with floor-to-ceiling panoramic glass", "props": "clean aluminum tablet, modern data visualization, elite tech prestige and growth"},
                {"setting": "bright creative IT workspace with warm ambient pendant lighting and whiteboards", "props": "ergonomic workstation, high-tech SaaS dashboards, breakthrough clarity and success"}
            ],
            "it": [
                {"setting": "modern high-tech software engineering office with floor-to-ceiling glass windows and natural daylight", "props": "clean minimalist desk with ultra-thin laptop showing AI code and metrics, contemporary tech atmosphere"},
                {"setting": "innovative AI technology hub with sleek architectural design and soft ambient illumination", "props": "cutting-edge digital workstation, data analytics visualizations, focused creativity"},
                {"setting": "sunlit Scandinavian style tech coworking space with lush green indoor plants and wooden tables", "props": "sleek laptop, warm natural morning daylight, inspiring productivity"},
                {"setting": "panoramic rooftop tech terrace with view of modern city skyscrapers at golden hour", "props": "tablet showing cloud software growth, futuristic optimism and mastery"}
            ],
            "религия": [
                {"setting": "majestic historic cathedral interior with towering stone arches, golden gilded altar details, soft sunbeams filtering through ancient stained glass windows", "props": "glowing beeswax candles in soft chiaroscuro, natural linen cloth, delicate incense haze, tranquil sacred stillness"},
                {"setting": "bright sunlit artisan monastery kitchen courtyard with natural morning daylight, rustic carved wooden table", "props": "fresh spring pussy willow branches, hand-woven natural linen napkin, warm soft window illumination"},
                {"setting": "intimate atmospheric evening chapel with warm glowing candle bokeh and rich architectural textures", "props": "aged brass candlestick, delicate embroidered tablecloth, timeless serenity"},
                {"setting": "festive spring celebration table by an arched stone window overlooking morning sky", "props": "natural terracotta dishware, dried floral accents, peaceful reverent warmth"}
            ],
            "животные": [
                {"setting": "warm sunlit Scandinavian-style home living room, natural herringbone hardwood floor, soft textured woven throw blanket", "props": "healthy potted indoor monstera plant, delicate dust motes floating in golden afternoon window sunbeams, pure domestic peaceful haven"},
                {"setting": "cozy sun-drenched window bench nook with plush velvet cushions and natural linen curtains", "props": "soft natural morning breeze, indoor ficus tree in background bokeh, serene relaxation"},
                {"setting": "modern minimalist sunlit loft patio with warm wooden deck and terracotta planters", "props": "morning sunlight puddles, gentle peaceful garden view in soft focus"},
                {"setting": "rustic country cottage fireside rug with warm amber glow", "props": "textured knitted wool blanket, cozy crackling warmth, ultimate comfort and security"}
            ],
            "кофейня": [
                {"setting": "sunlit rustic specialty craft coffee shop, polished vintage oak counter, soft morning street view in background bokeh", "props": "artisan ceramic cup, delicate rising fragrant steam, roasted coffee bean jar, warm brass accents"},
                {"setting": "minimalist luxury travertine marble counter with clean porcelain ware and fresh botanical eucalyptus", "props": "crisp morning studio daylight, glossy espresso machine reflection, refined modern aesthetic"},
                {"setting": "charming Parisian outdoor cafe bistro table with dark wrought iron accents in golden morning sun", "props": "crumbled buttery croissant flakes, fresh daily newspaper, warm European morning atmosphere"},
                {"setting": "warm atmospheric coffee roastery studio with burlap coffee sacks and glowing pendant lights", "props": "vintage brass coffee scale, roasted beans scattering, rich tactile aroma"}
            ],
            "пекарня": [
                {"setting": "artisan French pastry boutique, warm marble countertop with scattered fine flour dust and toasted almond flakes", "props": "flaky golden crust, fresh spring berry garnish, vintage baker's wooden paddle in soft focus"},
                {"setting": "sun-drenched rustic bakery table with natural raw linen and woven wicker bread baskets", "props": "delicate rising warm oven steam, rustic wheat sheaves, wholesome golden crust texture"},
                {"setting": "modern high-end confectionery showcase counter with crystal-clear glass and soft warm backlighting", "props": "gourmet dessert pedestal, fresh mint leaves, edible gold leaf accents"},
                {"setting": "bright minimalist patisserie kitchen with pristine stainless steel and white marble surfaces", "props": "precision pastry tools, glistening mirror glaze drips, culinary perfection"}
            ],
            "электроника": [
                {"setting": "clean high-tech electronics engineering laboratory, professional blue anti-static silicone soldering mat", "props": "precision tweezers, fine copper circuit traces, gold-plated header pins, micro-components in crisp macro focus"},
                {"setting": "modern minimalist R&D wooden workbench with glowing digital oscilloscope and schematic blueprints in soft focus", "props": "braided USB cables, precision multimeter probes, crisp engineering lighting"},
                {"setting": "top-down architectural tech workspace with anodized aluminum plates and brass precision calipers", "props": "clean circuit board layout, microchip silicon reflections, high-precision layout"},
                {"setting": "atmospheric prototyping studio with soft ambient amber and cyan LED edge illumination", "props": "breadboards, neatly organized jumper wires, cutting-edge innovation atmosphere"}
            ],
            "детейлинг": [
                {"setting": "pristine modern luxury auto detailing studio, glowing linear ceiling LED strip lights reflecting on deep paintwork", "props": "mirror-like gloss, hydrophobic micro water beads, ultra-plush microfiber towel in soft background"},
                {"setting": "high-end showroom floor at golden hour, polished epoxy reflective floor", "props": "dramatic rim lighting on car curves, flawless metallic paint depth, pristine prestige"},
                {"setting": "clean engineering tuning bay with professional modular tool cabinets in blurred background", "props": "ceramic coating applicator block, crisp reflection of overhead studio softbox"},
                {"setting": "outdoor scenic mountain lookout at golden sunset, clean asphalt reflection", "props": "warm evening sun flare, glistening clean aerodynamic bodywork"}
            ],
            "стоматология": [
                {"setting": "ultramodern sunlit aesthetic dental clinic, calm reassuring atmosphere with warm travertine marble and glass accents", "props": "flawless hygiene, soft diffused glare-free illumination, pure comfort and relief"},
                {"setting": "luxury dental wellness studio with floor-to-ceiling panoramic window and indoor bamboo garden", "props": "warm natural daylight, comfortable ergonomical setting, genuine peace of mind"},
                {"setting": "bright minimalist consultation office with contemporary Scandinavian wood finishes", "props": "crystal clear smile models, calming natural aroma, high-end medical excellence"},
                {"setting": "spacious private aesthetic room with soft warm indirect architectural lighting", "props": "pristine comfort, soothing atmosphere, trust and care"}
            ],
            "недвижимость": [
                {"setting": "spacious sun-drenched newly renovated open-plan living room with floor-to-ceiling panoramic windows overlooking evening sky", "props": "designer minimalist furniture, warm architectural ambient lighting, the feeling of dream home security"},
                {"setting": "contemporary luxury kitchen and dining area with monolithic quartz island and designer pendant lights", "props": "fresh fruit bowl, sunbeams piercing the room, elite architectural lifestyle"},
                {"setting": "airy sunlit master bedroom with herringbone oak flooring and sheer linen curtains fluttering in breeze", "props": "crisp white bedding, warm morning sunlight, serene sanctuary"},
                {"setting": "panoramic sunset terrace lounge with comfortable designer armchairs overlooking vibrant city lights", "props": "warm twilight sky, ambient recessed deck lighting, prestige and triumph"}
            ],
            "цвет": [
                {"setting": "sunlit Parisian floral boutique with rustic wooden worktables and arched European windows", "props": "fresh dewy pink peonies, eucalyptus stems, galvanized metal flower buckets, garden shears and ribbon rolls in soft focus"},
                {"setting": "charming botanical flower shop with cascading lush green foliage and sunbeams streaming through glass", "props": "delicate ranunculus bouquet in kraft paper wrap, water droplets on petals, artisan terracotta pots"},
                {"setting": "modern minimalist floral atelier with concrete surfaces and clean glass vases", "props": "exquisite white hydrangeas and garden roses, soft natural window daylight, botanical elegance"},
                {"setting": "cozy warm flower boutique counter at morning golden hour", "props": "vibrant fresh-cut seasonal flowers, organic twine spools, rustic wooden counter with rich tactile grain"}
            ],
            "посуд": [
                {"setting": "elegant sunlit artisanal ceramic and tableware boutique with warm open oak display shelves", "props": "handcrafted matte ceramic bowls, delicate bone porcelain plates, organic textured earthenware in soft warm ambient light"},
                {"setting": "minimalist Scandinavian tableware showroom with travertine stone pedestals", "props": "fine porcelain tea set with subtle glaze cracks, linen tablecloth in soft bokeh, timeless craftsmanship"},
                {"setting": "warm luxury porcelain gallery with soft directional gallery spotlights", "props": "exquisite bone china teacups, glazed ceramic vases, elegant refined lifestyle aesthetic"},
                {"setting": "charming European artisan tableware boutique counter with natural morning daylight", "props": "stacked handcrafted ceramic dinnerware, wooden serving spoons, pure tactile authenticity"}
            ]
        }

        # Выбираем пул окружений по нише или дефолтный
        env_pool = None
        for k, pool in niche_environments.items():
            if k in niche_lower or k in topic_lower:
                env_pool = pool
                break

        if routing and hasattr(routing, "visual_anchor") and routing.visual_anchor:
            va = routing.visual_anchor
            niche_universe = {
                "setting": va.environment_preset.replace("_", " "),
                "props": va.crossover_props or "authentic natural details"
            }
        elif env_pool:
            niche_universe = env_pool[var]
        else:
            default_variations = [
                {"setting": f"aesthetic contemporary {niche_en} setting", "props": "tactile authentic materials and natural atmospheric depth"},
                {"setting": f"bright minimalist sunlit {niche_en} environment with marble and warm wood accents", "props": "clean architectural lines, fresh botanical touches, soft natural lighting"},
                {"setting": f"warm luxury {niche_en} studio with soft evening ambient glow and rich textures", "props": "subtle velvet and brass details, sophisticated modern depth"},
                {"setting": f"spacious Scandinavian loft {niche_en} with expansive windows and golden daylight", "props": "organic textures, breathable negative space, effortless elegance"}
            ]
            niche_universe = default_variations[var]

        # =========================================================================
        # 1. АНАЛИЗ СЮЖЕТА, ВЫБОР РАКУРСА И СВЕТОВОЙ СХЕМЫ (С динамической ротацией)
        # =========================================================================
        perspectives_culinary = ["culinary_macro_eyelevel", "culinary_flatlay_topdown", "culinary_45_slice", "bokeh_shallow"]
        lighting_rotation = ["high_key", "soft_diffused", "rim_backlight", "gobo_shadows"]
        color_rotation = ["warm_analogous", "muted_editorial", "teal_orange", "warm_analogous"]
        comp_rotation = ["golden_spiral", "symmetry", "rule_of_thirds", "leading_lines"]

        if any(w in topic_lower for w in ["вид сверху", "сверху", "flatlay", "флэтлей", "ракурс сверху"]):
            light_key = "soft_diffused"
            color_key = "warm_analogous"
            comp_key = "symmetry"
            persp_key = "culinary_flatlay_topdown"
        elif any(w in topic_lower for w in ["торт", "пирог", "кусочек", "срез", "разрез", "начинк", "слои", "трюфель", "чизкейк"]):
            light_key = lighting_rotation[var]
            color_key = color_rotation[var]
            comp_key = comp_rotation[var]
            persp_key = "culinary_45_slice" if var % 2 == 0 else "culinary_macro_eyelevel"
        elif any(w in topic_lower for w in ["кулич", "пасх", "куличи", "панеттоне", "кекс", "капкейк"]):
            # При перегенерации кулича чередуем ракурсы: макро 30° -> flatlay 90° -> 45° срез
            persp_key = perspectives_culinary[var]
            light_key = lighting_rotation[var]
            color_key = color_rotation[var]
            comp_key = comp_rotation[var]
        elif "закат" in topic_lower or "пляж" in topic_lower or "вечер" in topic_lower:
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
        elif any(w in niche_lower for w in ["martech", "маркетинг", "saas", "it", "ии"]) or any(w in topic_lower for w in ["martech", "маркетинг", "saas", "ии-платформ", "автоматизац", "генеративн", "нейросеть"]):
            light_key = lighting_rotation[var]
            color_key = "muted_editorial" if var % 2 == 0 else "teal_orange"
            comp_key = comp_rotation[var]
            persp_key = "candid_eye_level" if var % 2 == 0 else "bokeh_shallow"
        elif any(w in topic_lower for w in ["десерт", "ролл", "выпечк", "кофе", "еда", "огурец", "плата", "esp", "электроник", "микроконтроллер", "турбин", "инструмент", "ювелир", "кольц", "косметик", "крем"]):
            light_key = lighting_rotation[var]
            color_key = color_rotation[var]
            comp_key = comp_rotation[var]
            persp_key = "tabletop_commercial" if var % 2 == 0 else "culinary_macro_eyelevel"
        elif any(w in topic_lower for w in ["флаг", "архитектур", "спорт", "фитнес"]):
            light_key = "rim_backlight"
            color_key = "teal_orange"
            comp_key = "triangles"
            persp_key = "low_angle_heroic"
        else:
            light_key = lighting_rotation[var]
            color_key = color_rotation[var]
            comp_key = comp_rotation[var]
            persp_key = "candid_eye_level" if var % 2 == 0 else "bokeh_shallow"

        # =========================================================================
        # ПИЛАР 2: РОЛЬ ПРОДУКТА И АРКА ЗРИТЕЛЯ (Product as Hero / Catalyst)
        # Кадр фиксирует кульминацию арки: идеальный момент гармонии, радости или безопасности.
        # =========================================================================
        from skills.visual_knowledge_researcher import VisualKnowledgeResearcher
        visual_spec = VisualKnowledgeResearcher.research_visual_spec_sync(topic)

        # 1. Проверяем конкретные сущности из темы (Topic Subjects) ПЕРЕД общими нишами
        if "кот" in topic_lower or "кошк" in topic_lower or "котик" in topic_lower:
            subject = "macro eye-level commercial pet portrait of a gorgeous fluffy tabby cat with bright sharp amber eyes and crisp long white whiskers, resting comfortably on a wooden desk beside an open laptop displaying high-contrast blue analytics charts"
            environment = "sunlit contemporary wooden desk, soft warm morning window daylight, crisp foreground focus with soft background office bokeh"
        elif any(w in topic_lower for w in ["собак", "щенок", "щенк"]) or any(re.search(rf'\b{w}\b', topic_lower) for w in ["пес", "пёс", "dog", "puppy"]):
            subject = "healthy energetic loyal dog with sharp shining fur, clear expressive eyes and joyful expression, macro pet photography"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["флорист", "девушка-флорист", "букет", "пион", "эвкалипт", "цветочн"]):
            subject = "a young female florist wearing a casual modest cotton shirt under a natural linen apron, holding a bouquet of pink peonies"
            environment = "Sunlit floral boutique, rustic wooden worktables, galvanized metal buckets"
        elif any(w in topic_lower for w in ["разработчик", "программист", "инженер", "developer", "tech developer"]) and any(w in topic_lower for w in ["кофе", "кружк", "чашк", "mug", "coffee", "стол", "ноутбук", "laptop", "office", "офис"]):
            subject = "a focused male tech developer wearing a casual dark shirt in a contemporary office looking at a laptop, holding a matte ceramic coffee mug"
            environment = "Soft ambient office daylight"
        elif any(w in topic_lower for w in ["посуд", "фарфор", "керамик", "чаш", "блюд", "гончар", "глинян"]):
            subject = "an artisan wearing a casual long-sleeved shirt under an apron, holding a handcrafted bone porcelain cup in hands, distinct individual fingers, authentic tactile grip"
            environment = "Sunlit artisanal ceramic and tableware boutique, open oak display shelves"
        elif any(w in topic_lower for w in ["человек", "основател", "фаундер", "девушк", "парен", "мужчин", "женщин", "портрет", "лицо", "разработчик", "инженер"]):
            subject = "a confident young tech professional wearing modest casual clothes with genuine relaxed expression, looking into camera"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif "плата" in topic_lower or "esp32" in topic_lower or "esp-32" in topic_lower or "ардуино" in topic_lower or "arduino" in topic_lower or "микроконтроллер" in topic_lower or "чип" in topic_lower:
            subject = visual_spec.get("visual_description", "extreme macro tabletop product photography of genuine ESP-32 development board with straight rigid gold square male header pins, rectangular metal RF shield engraved with ESP-32 logo, matte black FR-4 PCB, copper circuit traces, USB Type-C port")
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif "массаж" in topic_lower or "камн" in topic_lower:
            subject = visual_spec.get("visual_description", "serene relaxing hot stone back massage SPA treatment, smooth black basalt stones placed along spine, aromatic botanical oils glistening")
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["купальник", "бикини", "стринги", "нижнее белье", "swimwear", "lingerie"]):
            garment_desc = visual_spec.get("visual_description", "elegant stylish minimalist swimwear")
            if "пляж" in topic_lower or "закат" in topic_lower:
                subject = f"athletic graceful young female model posing naturally, wearing {garment_desc}"
                environment = "breathtaking golden hour ocean shoreline, gentle turquoise waves in soft background bokeh, warm sea breeze"
            else:
                subject = f"captivating charismatic female model posing with poise and elegance, wearing {garment_desc}"
                environment = "moody luxury penthouse lounge with soft neon ambient reflections, subtle velvet textures, cinematic depth"
        elif any(w in topic_lower for w in ["пасочниц", "формы для выпечки", "бумажные формы", "формочки для кулич"]):
            subject = "set of premium pleated brown cellulose Panettone and Easter Kulich paper baking molds with gold filigree and traditional carved wooden paskha pyramid mold on baker table"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["вид сверху", "flatlay", "флэтлей"]):
            subject = "centered top-down flatlay of artisanal Easter Kulich on a minimalist warm ceramic plate, glossy pastel pink or snowy-white glaze dome garnished with freeze-dried strawberry crumbles and soft mini marshmallows"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["торт", "трюфель", "чизкейк", "кусочек", "разрез"]):
            subject = "luxurious gourmet artisanal cake on a minimalist white porcelain plate, with a cleanly cut appetizing single slice placed beside it revealing moist rich sponge layers and creamy filling, dusted with shaved chocolate flakes, commercial dessert showcase"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["кулич", "пасх", "куличи", "пасхальн", "освящен"]):
            subject = "tall cylindrical golden-brown artisanal Easter Kulich brioche cake baked in a pleated brown Panettone paper mold with floral print, crowned with a thick glossy white royal icing glaze, decorated with emerald green pistachio sponge moss crumble and pastel sugar candy eggs, eye-level macro depth with background pastries in creamy bokeh"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif "кофе" in topic_lower or "эфиопи" in topic_lower or "капучин" in topic_lower:
            subject = "artisanal ceramic cup of creamy cappuccino with intricate latte art, fresh ripe peach slice and delicate white jasmine flowers on saucer, gentle rising steam"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif "крем" in topic_lower or "сыворотк" in topic_lower or "помад" in topic_lower or "блеск для губ" in topic_lower or "косметик" in topic_lower:
            subject = visual_spec.get("visual_description", "luxury commercial cosmetic product display")
            environment = "minimalist luxury travertine marble stone podium, delicate fresh water droplets, soft botanical accents in blurred background, clean studio aesthetic"
        elif "турбин" in topic_lower or "gt2871" in topic_lower or "койловер" in topic_lower or "перфоратор" in topic_lower or "шуруповерт" in topic_lower or "инструмент" in topic_lower:
            subject = visual_spec.get("visual_description", "precision tabletop commercial photograph of professional engineering component")
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in niche_lower for w in ["martech", "маркетинг", "saas", "it", "ии"]) or any(w in topic_lower for w in ["martech", "маркетинг", "saas", "ии-платформ", "автоматизац", "генеративн", "нейросеть"]):
            subject = "sleek modern workspace with an open ultra-thin laptop displaying a glowing clean AI marketing automation dashboard with real-time conversion growth graphs, creative preview cards, and automated campaign metrics in sharp focus"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        else:
            raw_vis = visual_spec.get("visual_description")
            subject = f"{raw_vis}" if raw_vis and raw_vis != topic else f"authentic commercial scene representing {niche_en}"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"

        # =========================================================================
        # ПИЛАР 3: ВНУТРЕННЯЯ ИСТОРИЯ И РЕКВИЗИТ КАК ЭКСПОЗИЦИЯ (Implied Narrative)
        # =========================================================================
        lighting = cls.LIGHTING_SCHEMES[light_key]
        color_scheme = cls.COLOR_HARMONIES[color_key]
        composition = cls.COMPOSITION_GEOMETRIES[comp_key]
        perspective = cls.PERSPECTIVES[persp_key]

        colors_str = f"Brand palette accents: {', '.join(brand_colors)}. " if brand_colors else ""

        # Дифференцируем текстурные дескрипторы: кожа для людей, фактура материала для предметов/еды/плат/животных
        is_human_scene = any(w in topic_lower or w in subject.lower() for w in ["человек", "девушк", "модел", "парень", "мужчин", "женщин", "лицо", "портрет", "мастер", "доктор", "врач", "тренер", "студент", "бариста", "юрист", "основател", "фаундер", "разработчик", "программист", "инженер", "model", "woman", "man", "person", "barista", "doctor", "founder", "florist", "artisan", "developer", "engineer", "male", "female"]) and not any(w in topic_lower for w in ["плата", "esp32", "esp-32", "arduino", "чип", "десерт", "стейк", "турбин", "перфоратор", "кот", "кошк", "собак"])
        
        if is_human_scene:
            texture_desc = (
                "(subsurface scattering, raw texture:1.2), (visible skin pores:1.2), peach fuzz, subtle blemishes, "
                "uneven natural skin tone, (35mm film grain, ISO 800:1.15), fine individual hair strands, "
                "messy hair, slightly unkempt, subtle facial asymmetry, natural skin folds, everyday realism"
            )
            # Направленный свет с глубокими микротенями для проявления текстуры
            if light_key in {"high_key", "soft_diffused", "rembrandt"}:
                lighting_desc = "Dramatic directional side lighting, deep micro-shadows"
            else:
                lighting_desc = lighting

            is_full_body = any(w in topic_lower for w in ["полный рост", "во весь рост", "full body", "standing", "ростовой", "в полный рост"])
            is_action_hands = any(w in topic_lower for w in ["держит", "руки", "пайк", "осциллограф", "инструмент", "holding", "hands", "soldering", "workbench"])

            optics_extra = ""
            if is_action_hands:
                optics_extra = "distinct clean individual fingers, natural hand grip, "
            elif is_full_body:
                optics_extra = "sharp full-body frame, crisp clothing fabric texture, "

            full_prompt = (
                f"35mm analog photography, candid snapshot of {subject}. "
                f"{environment}, anamorphic background bokeh. "
                f"{lighting_desc}. {optics_extra}"
                f"{texture_desc}."
            )
        else:
            texture_desc = (
                "tactile material texture, physical surface imperfections, natural reflections, "
                "(35mm film grain, ISO 400:1.1), authentic analog depth"
            )
            full_prompt = (
                f"35mm analog photography, candid snapshot of {subject}. "
                f"{environment}, anamorphic background bokeh. "
                f"{lighting}. "
                f"{perspective}, {texture_desc}."
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
    - Динамический Prompt Engineering под нишу бизнеса (3-Pillar Narrative Engine)
    - Поддержка соотношений сторон: 1:1 (Квадрат), 4:5 (Портрет), 16:9 (Баннер), 9:16 (Stories)
    - Интеграция с ComfyUI / SDXL / Diffusers / Local Visual Engine
    """

    ASPECT_RATIOS = {
        "1:1": (1152, 1152),
        "4:5": (1024, 1280),
        "16:9": (1344, 768),
        "9:16": (768, 1344),
        "3:4": (960, 1280),
        "4:3": (1280, 960)
    }

    NICHE_PRESETS = {
        "религия": {
            "subject": "majestic historic cathedral sanctuary with towering carved stone arches, golden gilded altar details, glowing beeswax candles, soft ethereal sunbeams filtering through ancient stained glass windows",
            "environment": "sacred historic sanctuary, timeless spiritual tranquility, marble floor reflecting candle glow, authentic cultural heritage atmosphere",
            "lighting": "warm golden candle glow, ethereal sunbeams through stained glass, gentle chiaroscuro highlights",
            "camera": "Cinematic 35mm architectural perspective, peaceful reverence and awe, Hasselblad color science, photorealistic"
        },
        "животные": {
            "subject": "adorable healthy domestic tabby cat resting peacefully on a warm wooden floor in a sunny spot next to a soft woven blanket, calm content expression",
            "environment": "cozy warm sunlit Scandinavian-style home living room, potted green plants, peaceful domestic haven",
            "lighting": "soft diffused morning window sunlight, gentle golden room ambient, natural warmth",
            "camera": "Eye-level macro pet photography, shallow depth of field, sharp tactile fur details, authentic UGC warmth"
        },
        "электроника": {
            "subject": "compact ESP-32 microcontroller board with dual-in-line gold header pins, CP2102 chip and USB Type-C port, extreme macro product shot",
            "environment": "clean high-tech electronics engineering workbench, blue anti-static silicone soldering mat, precision tweezers in soft background bokeh",
            "lighting": "high-key precision studio lighting, crisp metallic highlights on solder pads",
            "camera": "Macro tabletop lens, crisp copper circuit traces, tactile electronic engineering photography"
        },
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
        "bare shoulders, cleavage, exposed skin, bare chest, shirtless, half-naked, unclothed, revealing clothing, deep neckline, bare midriff, lingerie, swimsuit, bikini, underwear, suggestive, erotic, "
        "100-megapixel Hasselblad, Hasselblad H6D, 8k resolution, 4k, photorealistic, clean editorial, commercial retouching, "
        "crisp specular highlights, artificial global color filter, golden ratio overlay, diagram overlay, "
        "fused fingers, extra digits, missing fingers, malformed hands, fingers melting into objects, blurred hands, phantom fingers, mutated hands, "
        "computational photography blur, fake depth of field, synthetic bokeh, flat background, "
        "thick plastic hair, helmet hair, perfect grooming, CGI hair, hair clumps, stylized clay hair, "
        "Unreal Engine 5, octane render, digital painting, video game protagonist, hero shot, flawless, 3D render, "
        "airbrushed, plastic, smooth skin, overly retouched, wax, porcelain skin, perfect skin, "
        "smartphone, phone screen, holding smartphone, camera UI, viewfinder, bezel, device mockup, "
        "spiral lines, golden spiral overlay, graphic circle lines, diagram, geometric curves, grid overlay, "
        "staged studio photoshoot, heavy artificial studio strobes, studio softboxes, "
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
        custom_prompt: Optional[str] = None,
        variation_index: int = 0
    ) -> Dict[str, Any]:
        """
        Составляет высокохудожественный промпт для ComfyUI через CinematographyDirector с учетом номера перегенерации.
        """
        if custom_prompt and len(custom_prompt.strip()) > 30 and not custom_prompt.startswith("Authentic candid photo of a small tech") and not custom_prompt.startswith("Cinematic emotional culinary"):
            positive_prompt = custom_prompt
        else:
            cinematic_res = CinematographyDirector.compose_cinematic_prompt(
                topic=topic,
                niche=niche,
                brand_colors=brand_colors,
                variation_index=variation_index
            )
            positive_prompt = cinematic_res["prompt"]

        dimensions = self.ASPECT_RATIOS.get(aspect_ratio, self.ASPECT_RATIOS["1:1"])

        print(f"\n[PhotoGeneratorSkill] 📸 Сформирован промпт для ComfyUI (Ниша: {niche}, Вариация: {variation_index}):\n  👉 {positive_prompt}\n")

        return {
            "positive_prompt": positive_prompt,
            "negative_prompt": self.DEFAULT_NEGATIVE_PROMPT,
            "aspect_ratio": aspect_ratio,
            "width": dimensions[0],
            "height": dimensions[1],
            "niche": niche,
            "topic": topic,
            "variation_index": variation_index
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
        custom_prompt: Optional[str] = None,
        variation_index: int = 0
    ) -> Dict[str, Any]:
        """
        Полный цикл генерации профессиональной SMM фотографии и коммерческого визуала (с поддержкой перегенерации).
        """
        prompt_data = self.create_smm_prompt(
            topic=topic,
            niche=niche,
            aspect_ratio=aspect_ratio,
            brand_colors=brand_colors,
            style=style,
            variation_index=variation_index
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
            if await comfy_runner.ensure_server_online():
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
                print("[PhotoGeneratorSkill] ⚠️ Сервер ComfyUI оффлайн даже после автоперезапуска (127.0.0.1:8188 недоступен). Публикация будет выполнена без баннера.")
        except Exception as e:
            print(f"[PhotoGeneratorSkill] ⚠️ Ошибка вызова ComfyUI: {e}")
        # 2. Если ComfyUI не смог сгенерировать фото (оффлайн или ошибка) — НЕ создаем никаких 2D-баннеров!
        # Возвращаем статус no_image, чтобы пост вышел чистым текстом без искусственных картинок.
        if not rendered_via_comfy or not os.path.exists(file_path) or os.path.getsize(file_path) < 100:
            print("[PhotoGeneratorSkill] ℹ️ Фото не сгенерировано ComfyUI. Публикация будет выполнена в чистом текстовом формате без искусственных баннеров.")
            return {
                "status": "no_image",
                "photo_id": None,
                "filename": None,
                "image_url": None,
                "file_path": None,
                "positive_prompt": prompt_data["positive_prompt"],
                "negative_prompt": prompt_data["negative_prompt"],
                "aspect_ratio": aspect_ratio,
                "width": prompt_data["width"],
                "height": prompt_data["height"],
                "created_at": datetime.utcnow().isoformat()
            }

        # 3. Формирование публичного URL реального фото
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


__all__ = ["PhotoGeneratorSkill"]
