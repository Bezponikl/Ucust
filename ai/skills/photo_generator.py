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
        "low_key": "Low-key directional moody light with natural deep shadows and high contrast, dark ambient background, dramatic light falloff",
        "high_key": "Natural daylight illumination with directional sunbeams and deep defined micro-shadows, stark contrast",
        "chiaroscuro": "Strong directional key side lighting casting deep chiaroscuro shadows, high contrast falloff, un-lifted rich dark shadows",
        "silhouette": "Natural backlit contour against bright background, deep rich blacks",
        "gobo_shadows": "Natural window shadow patterns across the scene with crisp shadow edges and deep contrast",
        "rim_backlight": "Strong directional backlighting contour with stark contrast and un-lifted deep shadows",
        "rembrandt": "Dramatic strong directional side light, Rembrandt lighting with deep micro-shadows, stark contrast and dramatic light falloff",
        "paramount": "Directional overhead light defining facial planes with deep chin and cheek micro-shadows",
        "spotlight": "Warm direct task light illuminating the subject with dramatic light falloff into darkness",
        "lens_flare": "Subtle optical lens flare, organic light leak with deep contrast preservation",
        "soft_diffused": "Directional morning window daylight with natural shadow falloff and deep micro-shadows",
        "dual_office": "Subtle dual lighting with a warm 3000K key lamp glow on subject contrasting with cool 5500K ambient daylight from background windows, stark light falloff",
        "overcast_diffused": "Directional daylight with rich micro-contrast and deep shadows, authentic outdoor depth",
        "warm_pendant": "Hanging pendant filament lamp casting strong directional warm key light with deep ambient shadows and dramatic falloff",
        "hard_chiaroscuro": "Strong single directional warm key light casting deep dramatic chiaroscuro shadows with stark contrast falloff and rich blacks",
        "golden_hour_rim": "Warm directional golden hour key light casting dramatic rim light and deep contrasted shadows",
        "editorial_studio": "Single directional key light from upper-left with deep shadow falloff, stark contrast, un-lifted micro-shadows"
    }

    COLOR_HARMONIES = {
        "teal_orange": "warm foreground key lighting contrasting with subtle cool background ambient light, complementary color temperature separation",
        "warm_analogous": "warm directional key light with deep organic shadows, subtle cool ambient air in background",
        "complementary": "warm foreground subject lighting contrasting with cool background ambient tones",
        "muted_editorial": "natural authentic color reproduction, stark contrast between warm key highlights and cool shadowed background",
        "monochrome": "natural monochrome analog film tones with deep rich blacks and high contrast"
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
        "bokeh_shallow": "smooth progressive focal falloff, authentic optical lens blur, f/1.2 depth of field, blurred object in extreme foreground creating layered 3D depth, creamy natural background falloff",
        "low_angle_heroic": "slightly low-angle perspective, smooth progressive optical focal falloff, f/1.2 lens blur",
        "tabletop_commercial": "45-degree angle tabletop view, smooth progressive optical focal falloff, f/1.4 lens blur, blurred foreground edge framing the subject",
        "candid_eye_level": "35mm prime lens, authentic progressive optical lens blur, f/1.2 depth of field, layered foreground-to-background spatial depth",
        "culinary_macro_eyelevel": "35mm close-up macro lens, f/1.2 smooth optical focal falloff, blurred object in extreme foreground framing the subject, creamy layered background bokeh",
        "culinary_flatlay_topdown": "direct top-down 90-degree overhead perspective with rich micro-shadows and depth",
        "culinary_45_slice": "45-degree angled perspective with smooth optical focal falloff, f/1.4 depth of field, tactile foreground depth",
        "oversized_hero": "centered medium shot framing hero subject, f/1.2 smooth progressive focal falloff, blurred foreground bokeh",
        "candid_counter": "medium eye-level shot, candid interaction across counter, progressive optical lens blur with depth",
        "layered_artisan_table": "layered multi-tiered display, blurred object in extreme foreground, tack-sharp subject, creamy background falloff",
        "contemplative_profile": "medium close-up profile shot, smooth progressive focal falloff, f/1.2 depth of field with creamy bokeh",
        "active_desk_focus": "elevated side-angle desk perspective, blurred foreground coffee cup edge creating layered depth, f/1.2 optical falloff",
        "macro_nail_close_up": "tight macro lens, smooth progressive optical focal falloff, f/1.4 shallow depth of field, blurred foreground fabric edge creating physical layered depth, creamy atmospheric background falloff"
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
        "маникюр": "luxury nail art and aesthetic manicure salon",
        "ногти": "high-end nail design and aesthetic manicure studio",
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
        domain_priority = [
            # 1. Ногти, маникюр и бьюти (макро)
            "маникюр", "ногти", "гель-лак", "нейл", "ногот", "педикюр",
            # 2. Кофейня, латте-арт, бариста и напитки (ДО посуды/керамики!)
            "капучин", "латте", "кофе", "эспрессо", "барист", "круассан",
            # 3. Породы животных и питомцы
            "корги", "шпиц", "померан", "сиба", "хаски", "овчарк", "щенок", "щенк", "собак",
            "кот", "кошк", "котик", "котен", "котён",
            # 4. Гастрономия, блюда и стейки
            "стейк", "рибай", "шеф", "кулинар", "шаурм", "бургер", "пицц", "суши", "ролл",
            # 5. Десерты и выпечка
            "синнабон", "булочк", "печень", "торт", "ганаш", "чизкейк", "кулич", "пасх", "десерт", "пекарн",
            # 6. Флористика
            "флорист", "букет", "пион", "эвкалипт", "цвет",
            # 7. IT-ночь, терминал, мегаполис
            "терминал", "ide", "ночн", "ночь", "ночью", "мегаполис", "небоскреб", "высотк", "балкон",
            # 8. Посуда и керамика (ТОЛЬКО если это не кофе)
            "гончар", "глинян", "фарфор", "посуд", "керамик",
            # 9. Наружная реклама и постеры
            "постер", "плакат", "вывеск", "типографик", "билборд", "лайтбокс",
            # 10. Электроника и инженерия
            "esp32", "esp-32", "плата", "arduino", "микроконтроллер", "чип", "электроник",
            # 11. Общие бизнес-сферы
            "детейлинг", "стоматолог", "недвижим", "блокнот", "конспект", "постель",
            "разработчик", "программист", "it", "saas", "martech"
        ]
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
                {"setting": "modern high-tech software engineering office with polished wooden desk and black gooseneck desk lamp casting a warm focused pool of light", "props": "sleek silver laptop, stack of black notebooks with silver pen, smartphone beside printed charts, white ceramic coffee mug, natural daylight from glass partitions in background"},
                {"setting": "contemporary tech office corner, warm beige fabric floor lamp casting soft ambient shadows against beige wall", "props": "black laptop, smartphone on wooden table, deep contemplation atmosphere"},
                {"setting": "executive analytical workstation with ergonomic black mesh chair", "props": "large curved monitor displaying glowing orange and white dynamic data charts, warm circular desk lamp creating dramatic ambient glow"},
                {"setting": "dimly lit late-night corporate tech office with floor-to-ceiling glass windows", "props": "silver laptop on desk, whiteboard with handwritten charts and sticky notes in soft background, cool blue-gray ambient tones"}
            ],
            "религия": [
                {"setting": "majestic historic cathedral interior with towering stone arches, golden gilded altar details, soft sunbeams filtering through ancient stained glass windows", "props": "glowing beeswax candles in soft chiaroscuro, natural linen cloth, delicate incense haze, tranquil sacred stillness"},
                {"setting": "bright sunlit artisan monastery kitchen courtyard with natural morning daylight, rustic carved wooden table", "props": "fresh spring pussy willow branches, hand-woven natural linen napkin, warm soft window illumination"},
                {"setting": "intimate atmospheric evening chapel with warm glowing candle bokeh and rich architectural textures", "props": "aged brass candlestick, delicate embroidered tablecloth, timeless serenity"},
                {"setting": "festive spring celebration table by an arched stone window overlooking morning sky", "props": "natural terracotta dishware, dried floral accents, peaceful reverent warmth"}
            ],
            "животные": [
                {"setting": "cozy sunlit living room with natural herringbone hardwood floor and soft textured cream knit throw blanket", "props": "delicate dust motes floating in golden afternoon sunbeams, pure domestic comfort"},
                {"setting": "warm sun-drenched living room window nook with natural linen curtains", "props": "soft woven blanket, indoor green plants in background bokeh, peaceful relaxation"},
                {"setting": "modern minimalist living space with light oak flooring and warm rug", "props": "afternoon sunlight patches, serene cozy home haven"},
                {"setting": "warm rustic living room with fireplace hearth", "props": "textured knitted wool blanket, cozy crackling warmth, ultimate comfort"}
            ],
            "зоо": [
                {"setting": "cozy sunlit living room with natural herringbone hardwood floor and soft textured cream knit throw blanket", "props": "delicate dust motes floating in golden afternoon sunbeams, pure domestic comfort"},
                {"setting": "warm sun-drenched living room window nook with natural linen curtains", "props": "soft woven blanket, indoor green plants in background bokeh, peaceful relaxation"},
                {"setting": "modern minimalist living space with light oak flooring and warm rug", "props": "afternoon sunlight patches, serene cozy home haven"},
                {"setting": "warm rustic living room with fireplace hearth", "props": "textured knitted wool blanket, cozy crackling warmth, ultimate comfort"}
            ],
            "кофейня": [
                {"setting": "sunlit rustic specialty craft coffee shop, polished vintage oak counter, soft morning street view in background bokeh", "props": "artisan ceramic cup, delicate rising fragrant steam, roasted coffee bean jar, warm brass accents"},
                {"setting": "minimalist luxury travertine marble counter with clean porcelain ware and fresh botanical eucalyptus", "props": "crisp morning studio daylight, glossy espresso machine reflection, refined modern aesthetic"},
                {"setting": "charming Parisian outdoor cafe bistro table with dark wrought iron accents in golden morning sun", "props": "crumbled buttery croissant flakes, fresh daily newspaper, warm European morning atmosphere"},
                {"setting": "warm atmospheric coffee roastery studio with burlap coffee sacks and glowing pendant lights", "props": "vintage brass coffee scale, roasted beans scattering, rich tactile aroma"}
            ],
            "пекарня": [
                {"setting": "traditional European rustic market stall covered by cream-colored canvas awning, brick building and open field in background under overcast sky", "props": "draped deep green cloth, abundant display of artisanal cheese wheels with white rinds, crumbly wedges, ripe red tomatoes in baskets, wooden crates overflowing with crusty sourdough baguettes"},
                {"setting": "cozy artisan food hall market stall with rustic exposed wooden beams and warm pendant lights", "props": "wooden cutting boards with artisanal cheeses, glass jars of honey and fruit preserves with handwritten labels, fresh chives, linen runner, small chalkboard price tags"},
                {"setting": "artisan French pastry boutique, warm marble countertop with scattered fine flour dust and toasted almond flakes", "props": "flaky golden crust, fresh spring berry garnish, vintage baker's wooden paddle in soft focus"},
                {"setting": "dimly lit professional gourmet restaurant kitchen with dark wooden shelves of wine bottles", "props": "chef knife with black handle slicing deep-red meat on rustic wooden board, stack of clean white ceramic plates, stainless steel pot in Rembrandt chiaroscuro"}
            ],
            "десерт": [
                {"setting": "artisan pastry workshop with dark slate slab and rustic wooden accents", "props": "glossy molten chocolate ganache cascading over layered cake, ripe halved strawberries, fine dark chocolate curls"},
                {"setting": "rustic bakery table covered with textured frayed beige linen runner", "props": "golden-brown cinnamon rolls on circular wooden board, whole dark star anise pods, whole cinnamon sticks, powdered sugar dusting"},
                {"setting": "cozy gourmet bakery packaging counter with natural kraft paper and brown ribbon", "props": "gourmet cookie gift box with crinkled parchment paper, assorted chocolate chunk and walnut cookies"},
                {"setting": "weathered wooden table with rich natural grain and knots", "props": "circular bark-edged wooden serving board, freshly baked chocolate chip cookies, steaming ceramic mug of hot coffee with delicate vapor curls"}
            ],
            "постер": [
                {"setting": "modern urban interior with weathered red brick wall and natural mortar lines", "props": "minimalist dark framed poster with sharp dark-gray typography on white, warm overhead spotlight, natural wood door trim"},
                {"setting": "classical architectural gallery arcade with stone arches and high vaulted ceiling", "props": "hanging circular illuminated lightbox sign with warm golden backlighting, classical stone pillars"},
                {"setting": "corner street facade of a multi-story contemporary concrete and glass building", "props": "massive architectural outdoor billboard, clean sky background, bold high-contrast graphic branding"},
                {"setting": "industrial modern loft staircase with dark steel risers and steps", "props": "crisp white typography stenciled on metal steps, directional side lighting, tactile raw steel texture"}
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
                {"setting": "entrance of a modern flower boutique with weathered red brick wall, textured white mortar, and dark wooden doorway", "props": "massive overflowing wicker basket packed with pink peonies, magenta dahlias, peach carnations, baby's breath, cascading green foliage, wet reflective concrete pavement"},
                {"setting": "picturesque cobblestone street corner with historic architecture in soft overcast daylight", "props": "large natural wicker basket overflowing with crisp white daisies and lush green foliage, beige trench coat and boots aesthetic"},
                {"setting": "sunlit Parisian floral boutique with rustic wooden worktables and arched European windows", "props": "fresh dewy pink peonies, eucalyptus stems, galvanized metal flower buckets, garden shears and ribbon rolls in soft focus"},
                {"setting": "modern minimalist floral atelier with concrete surfaces and clean glass vases", "props": "exquisite white hydrangeas and garden roses, soft natural window daylight, botanical elegance"}
            ],
            "посуд": [
                {"setting": "elegant sunlit artisanal ceramic and tableware boutique with warm open oak display shelves", "props": "handcrafted matte ceramic bowls, delicate bone porcelain plates, organic textured earthenware in soft warm ambient light"},
                {"setting": "minimalist Scandinavian tableware showroom with travertine stone pedestals", "props": "fine porcelain tea set with subtle glaze cracks, linen tablecloth in soft bokeh, timeless craftsmanship"},
                {"setting": "warm luxury porcelain gallery with soft directional gallery spotlights", "props": "exquisite bone china teacups, glazed ceramic vases, elegant refined lifestyle aesthetic"},
                {"setting": "charming European artisan tableware boutique counter with natural morning daylight", "props": "stacked handcrafted ceramic dinnerware, wooden serving spoons, pure tactile authenticity"}
            ],
            "ритейл": [
                {"setting": "modern cozy specialty grocery store with exposed brick wall, black metal shelving and hanging pendant filament bulbs", "props": "dark speckled granite checkout counter, touchscreen POS register, snacks in neat packaging, small potted green plant in metallic pot"},
                {"setting": "contemporary boutique checkout area with warm wooden accents and soft overhead spotlighting", "props": "branded canvas tote bag, organic snack packages on counter, friendly service atmosphere"},
                {"setting": "artisan concept store with warm oak display tables and minimalist signage", "props": "handcrafted goods with minimalist labels, receipt printer, warm inviting customer experience"},
                {"setting": "sunlit specialty gourmet market counter with glass display cases", "props": "freshly packaged artisan goods, chalkboard menu board, warm inviting light"}
            ],
            "бьюти": [
                {"setting": "modern sunlit beauty salon with warm travertine surfaces and fresh botanical accents", "props": "soft indirect lighting, clean mirrors, luxurious calm atmosphere"},
                {"setting": "cozy aesthetic studio with warm neutral beige background bokeh", "props": "textured cream chunky-knit fabric, delicate dried botanicals, soft ambient glow"},
                {"setting": "chic minimalist aesthetic salon with soft daylight", "props": "warm oak table, delicate linen cloth, refined modern elegance"},
                {"setting": "editorial studio setting with dramatic key lighting and deep shadow falloff", "props": "warm amber ambient accents, high-contrast textures, rich depth"}
            ],
            "маникюр": [
                {"setting": "cozy aesthetic nail studio with textured cream chunky-knit fabric in foreground", "props": "delicate dried autumn maple leaves, soft neutral beige background bokeh"},
                {"setting": "warm ambient studio lounge with soft circular golden bokeh lights", "props": "warm ceramic cup, soft textured knitwear, warm intimate glow"},
                {"setting": "minimalist luxury nail bar with warm oak surface and soft diffused daylight", "props": "ribbed knit sweater sleeve cuff, rich tactile textures"},
                {"setting": "chic modern beauty salon with soft indirect lighting", "props": "natural linen cloth, delicate seasonal accents, elegant ambiance"}
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
                {"setting": f"bright minimalist sunlit {niche_en} environment with warm wood accents", "props": "clean architectural lines, fresh botanical touches, soft natural lighting"},
                {"setting": f"warm atmospheric {niche_en} studio with soft evening ambient glow and rich textures", "props": "subtle textured details, sophisticated depth"},
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
        elif any(w in topic_lower for w in ["маникюр", "ногти", "гель-лак", "ногот", "nail", "manicure", "педикюр"]):
            light_key = "soft_diffused" if var % 2 == 0 else "warm_pendant"
            color_key = "warm_analogous"
            comp_key = "rule_of_thirds"
            persp_key = "macro_nail_close_up"
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
        # Приоритет отдан максимально специфичным предметным сущностям и макро-деталям
        # =========================================================================
        from skills.visual_knowledge_researcher import VisualKnowledgeResearcher
        visual_spec = VisualKnowledgeResearcher.research_visual_spec_sync(topic)

        # 1. МАНИКЮР, НОГТИ И БЬЮТИ МАКРО (3 РАЗНЫХ КАНОНИЧЕСКИХ ПОЗЫ)
        if any(w in topic_lower for w in ["маникюр", "ногти", "гель-лак", "нейл", "ногот", "педикюр", "nail", "manicure"]):
            if any(w in topic_lower for w in ["сапфир", "синий", "navy", "синем", "голубой"]):
                color_desc = "deep glossy sapphire-navy gel polish with delicate gold leaf foil accent flakes"
            elif any(w in topic_lower for w in ["бордо", "марсал", "вишн", "burgundy"]):
                color_desc = "rich glossy deep burgundy wine gel polish with subtle mirror shine"
            elif any(w in topic_lower for w in ["шоколад", "кофе", "brown", "коричнев"]):
                color_desc = "rich glossy warm chocolate-brown and matte nude tones with delicate gold foil leaf art"
            elif any(w in topic_lower for w in ["нюд", "беж", "пастел", "nude"]):
                color_desc = "clean minimalist nude milk-bath gel polish with pristine gloss"
            elif any(w in topic_lower for w in ["терракот", "оранж", "карамел"]):
                color_desc = "warm autumn terracotta and caramel gloss finish with delicate botanical micro-line art"
            else:
                color_desc = "rich elegant glossy gel polish with flawless mirror reflection and pristine cuticles"

            shape_desc = "soft square" if any(w in topic_lower for w in ["квадрат", "square"]) else "flawless almond"

            nail_poses = [
                # Вариация 0: Классический лайфстайл (ладони расслабленно скрещены на свитере)
                f"extreme macro close-up photography of slender well-manicured female hands gently crossed over a soft cream knit sweater, {shape_desc} shaped nails with {color_desc}, razor-sharp focus on pristine cuticles and smooth nail plates, natural skin texture with visible pores, no full person visible",
                # Вариация 1: Ладонь (одна рука мягко подогнута к мягкой подушечке ладони)
                f"macro close-up photography of a single manicured female hand gently curled inward toward palm showing {shape_desc} nails with {color_desc} against soft inner palm skin, clean ring-light studio reflection, crisp cuticle alignment",
                # Вариация 2: Встречные руки сверху и снизу кадра (как на референсе)
                f"editorial beauty photography of two manicured hands entering the frame from opposite top and bottom angles with fingers fanned out in parallel symmetry meeting in center, ribbed sweater sleeves framing the frame from above and below, showcasing pristine {shape_desc} nails with {color_desc}"
            ]
            subject = nail_poses[var % len(nail_poses)]
            environment = "warm aesthetic studio background in soft creamy bokeh, cozy autumn ambiance, beautiful textured knitwear in soft focus"
            persp_key = "macro_nail_close_up"

        # 2. КОФЕЙНЯ, КАПУЧИНО, ЛАТТЕ-АРТ (РУКИ, ЧАШКА, ПАР, КРЕМА 40-60%)
        elif any(w in topic_lower for w in ["кофе", "капучин", "латте", "эспрессо", "раф", "флэт", "круассан", "coffee", "cappuccino", "latte", "croissant"]):
            latte_art = "intricate swan pattern latte art" if any(w in topic_lower for w in ["лебед", "swan"]) else ("intricate rosetta latte art" if any(w in topic_lower for w in ["розетт", "rosetta"]) else "silky velvety microfoam latte art")
            table_desc = "rustic dark oak table" if any(w in topic_lower for w in ["дуб", "дерев", "стол", "oak", "wood"]) else "minimalist wooden cafe table"
            pastry_desc = ", accompanied by a fresh golden-brown flaky French butter croissant on a textured linen napkin with visible buttery layers" if any(w in topic_lower for w in ["круассан", "croissant", "выпечк"]) else ""
            cup_desc = "handcrafted matte ceramic sage-green or earthy cup" if any(w in topic_lower for w in ["керамик", "чашк", "кружк", "cup", "ceramic"]) else "artisan ceramic cup"

            coffee_archetypes = [
                # Вариация 0: Руки греются об чашку (эмоция уюта)
                f"candid close-up lifestyle photo of female hands in cozy knitted sweater sleeves gently cupping a warm {cup_desc} with both palms to warm up, {latte_art} with contrasting dark espresso rim, whisper of translucent warm vapor rising, on a {table_desc}",
                # Вариация 1: Хват за ручку (момент дегустации)
                f"candid side-angle photo of a clean hand holding the {cup_desc} by its handle lifting it slightly above ceramic saucer{pastry_desc}, glossy espresso crema and microfoam, subtle translucent heat shimmer rising, morning sunlight on {table_desc}",
                # Вариация 2: Стол без людей (предметный вид: крема 40-60% или ровный арт)
                f"macro commercial tabletop photography of a steaming {cup_desc} with golden-brown crema and microfoam covering 50% of surface, placed on a {table_desc} beside roasted coffee beans and a ceramic saucer, subtle translucent heat shimmer"
            ]
            subject = coffee_archetypes[var % len(coffee_archetypes)]
            environment = "cozy sunlit specialty craft coffee shop, warm morning sunbeams streaming through window, soft golden bokeh in background"
            persp_key = "culinary_macro_eyelevel" if var % 2 == 0 else "tabletop_commercial"

        # 3. КУЛИНАРИЯ: ШЕФ-ПОВАР, СТЕЙК, МЯСНОЙ БУТИК (ПРАВИЛЬНЫЙ ХВАТ, ШПАГАТ, ОВОЩИ-ГРИЛЬ)
        elif any(w in topic_lower for w in ["стейк", "рибай", "мясо", "steak", "ribeye", "bbq", "барбекю", "мясн"]) or (any(w in topic_lower for w in ["шеф", "повар", "chef"]) and any(w in topic_lower for w in ["кухн", "кулинар", "нарез", "жар", "блюд"])):
            garlic_and_herbs = "a caramelized charred roasted garlic bulb with golden edges, fresh rosemary sprig, and crunchy Maldon sea salt crystals on aged dark walnut board"
            steak_archetypes = [
                # Вариация 0: Хват повара (claw grip) и нарезка под 45°
                f"a professional master chef's hands in action, left hand firmly securing the resting steak in a professional claw grip, right hand slicing a prime ribeye steak against the grain at 45 degrees with a sharp Japanese knife on an aged dark walnut board, {garlic_and_herbs}, tender juicy pink medium-rare center with resting meat juices glistening, subtle translucent culinary heat shimmer",
                # Вариация 1: Крафтовая упаковка / Мясной бутик (шпагат, пергамент, овощи с прогарками от решетки)
                "candid culinary photography of a raw marbled prime beef steak resting on crinkled brown butcher kraft paper, loosely tied with natural rustic jute cooking twine with a partially unspooled twine spool on the side, accompanied by colorful grilled vegetables with distinct dark charred grill marks — blistered cherry tomatoes, roasted corn wheels and zucchini slices, with scattered coarse peppercorns and roasted garlic cloves on a dark butcher table",
                # Вариация 2: Макро-срез сочных медальонов и ресторанная подача
                f"extreme macro eye-level culinary photography of carved juicy medium-rare ribeye steak medallions laid out neatly on a dark slate board, pink marbled interior texture, glistening natural meat juices pooling, sprinkled with flaky Maldon salt and roasted garlic cloves, {garlic_and_herbs}"
            ]
            subject = steak_archetypes[var % len(steak_archetypes)]
            environment = "dimly lit professional gourmet restaurant open kitchen or artisan butcher workshop, warm dramatic Rembrandt chiaroscuro lighting, stainless steel accents and wine bottles in deep atmospheric bokeh"
            persp_key = "culinary_macro_eyelevel" if var % 2 == 0 else "culinary_45_slice"

        # 4. IT / РАЗРАБОТЧИК / КОМАНДА / DEVPULSE (КОМАНДА, МОНИТОРЫ, ПРАВИЛЬНЫЙ СВЕТ)
        elif any(w in topic_lower for w in ["команд", "team", "стартап", "startup", "devpulse", "ucust"]) and any(w in niche_lower or w in topic_lower for w in ["it", "saas", "martech", "бизнес", "разработк", "маркетинг"]):
            team_archetypes = [
                # Вариация 0: Командный брейншторм у монитора / архитектурной доски
                "a dynamic collaborative software development team of 2-3 young energetic engineers collaborating in a modern loft studio office, pointing at a large high-resolution monitor displaying system architecture diagrams and dark-mode code, whiteboard with flowcharts in background, engaged positive atmosphere",
                # Вариация 1: Инженер за рабочим местом с правильным светом (лампа светит на стол, не на экран)
                "a focused software developer working at modern oak desk with dual high-resolution matte monitors displaying dark-theme IDE code editor with real syntax highlighting, warm desk lamp positioned to illuminate the desk surface without glare on screens, clean cable management, matte ceramic coffee mug",
                # Вариация 2: POV разработчика (руки на клавиатуре, глубина офиса)
                "first-person POV over-the-shoulder shot of hands typing on a sleek low-profile mechanical keyboard, crisp dark-mode code terminal running build telemetry on matte monitor, blurred modern open-space tech office with warm ambient lights in background"
            ]
            subject = team_archetypes[var % len(team_archetypes)]
            environment = "modern tech open-space loft office, warm ambient interior lighting, exposed brick and glass partitions in soft bokeh"
            light_key = "dual_office"
            color_key = "teal_orange"
            persp_key = "candid_eye_level"
        elif any(w in topic_lower for w in ["разработчик", "программист", "инженер", "кодер", "developer", "tech developer"]) or any(w in topic_lower for w in ["терминал", "ide", "архитектур"]) or (any(w in topic_lower for w in ["ночь", "ночью", "ночн", "мегаполис", "небоскреб"]) and any(w in niche_lower for w in ["it", "saas", "martech", "бизнес", "разработк"])):
            if any(w in topic_lower for w in ["ночь", "ночью", "ночн", "дожд", "мегаполис", "небоскреб", "панорам", "терминал", "ide", "темн"]):
                subject = "a focused software developer in dark clothing working late at night, seen from side angle focused on dual high-resolution matte monitors displaying real syntax-highlighted code in dark-theme IDE, terminal command logs and telemetry metrics, typing on a sleek low-profile keyboard beside a matte ceramic coffee mug"
                environment = "contemporary high-rise office with panoramic floor-to-ceiling glass windows overlooking a dark rainy illuminated nocturnal metropolis with glowing skyscraper lights and traffic reflections, soft cool cyan and amber rim lighting on aluminum laptop"
                light_key = "low_key"
                color_key = "teal_orange"
                persp_key = "bokeh_shallow"
            else:
                it_archetypes = [
                    "a focused young tech specialist in denim jacket typing intently on a sleek silver laptop displaying clean IDE interface, warm desk lamp directed downward onto wooden desk surface",
                    "a contemplative tech architect in clear glasses in deep analytical thought, seated at oak desk with laptop and code terminal under warm ambient lighting",
                    "a professional software engineer seated in ergonomic mesh chair, looking at curved monitor with glowing data graphs and code structure, clean desk setup",
                    "a dedicated engineer at modern desk, laptop and whiteboard with architecture diagram in background"
                ]
                subject = it_archetypes[var % len(it_archetypes)]
                environment = f"{niche_universe['setting']}, {niche_universe['props']}"

        # 5. ЖИВОТНЫЕ: КОШКИ
        elif any(w in topic_lower for w in ["кот", "кошк", "котик", "котен", "котён", "cat", "kitten"]):
            cat_archetypes = [
                "macro eye-level pet portrait of an adorable ginger tabby kitten with vibrant orange stripes and luminous blue-green eyes, stretching playfully in a warm diagonal sunbeam across a rustic wooden floor",
                "high-angle top-down macro shot of a tiny fluffy gray and white kitten lying curled on a soft ivory knit blanket, gazing directly up at the camera with wide curious amber eyes",
                "sleek black cat with glossy midnight fur and striking golden-yellow eyes, nestled comfortably on a cozy cream-toned textured fleece blanket in warm ambient lighting",
                "charming fluffy black cat with luminous emerald eyes, sitting on a wooden desk with a tiny pink tongue peeking out in a playful blep expression beside soft warm lamplight"
            ]
            if any(w in topic_lower for w in ["черн", "black"]):
                subject = cat_archetypes[2] if var % 2 == 0 else cat_archetypes[3]
            elif any(w in topic_lower for w in ["рыж", "ginger", "orange"]):
                subject = cat_archetypes[0]
            elif any(w in topic_lower for w in ["сер", "gray", "grey", "бел", "white"]):
                subject = cat_archetypes[1]
            else:
                subject = cat_archetypes[var % len(cat_archetypes)]
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"

        # 6. ЖИВОТНЫЕ: СОБАКИ, ЩЕНКИ И КОРГИ (3 РАЗНЫХ РАКУРСА И ПОЗЫ)
        elif any(w in topic_lower for w in ["собак", "щенок", "щенк", "корги", "шпиц", "померан", "сиба", "хаски", "овчарк"]) or any(re.search(rf'\b{w}\b', topic_lower) for w in ["пес", "пёс", "dog", "puppy"]):
            blanket_desc = "sitting on a soft cream chunky-knit blanket in golden afternoon sunbeams" if any(w in topic_lower for w in ["плед", "одеял", "вязаном", "blanket", "rug"]) else "sitting on a textured light oak floor in warm sunlight"
            
            corgi_variations = [
                # Вариация 0: Портрет крупно (наклон головы, выразительные глаза)
                "an adorable Welsh Corgi puppy with golden-red and white fur, upright rounded fox-like ears, cute curious head tilt, large expressive dark amber eyes, sitting comfortably on a soft cream chunky-knit blanket in warm morning sunbeams, razor-sharp eye focus and individual whisker details",
                # Вариация 1: Вид сверху / Top-down (щенок лежит на спине/боку на пледе)
                "high-angle top-down commercial pet photo of a playful Corgi puppy lying on its back on a thick knit blanket with paws up, joyful happy expression, soft sunlight patterns across the room",
                # Вариация 2: Ракурс от пола (Ground-level dynamic)
                "low ground-level action photo of a Corgi puppy stretching forward playfully on a light oak floor, sniffing toward camera, shallow depth of field with cozy room background in warm bokeh"
            ]
            
            dog_archetypes = [
                f"a fluffy, golden-furred puppy with soft long light golden fur, {blanket_desc}, ultra-detailed soft lifelike fur catching natural backlighting",
                corgi_variations[var % len(corgi_variations)],
                f"a fluffy cream-colored Pomeranian puppy with curious dark eyes, {blanket_desc}, playful expression",
                f"a neat red Shiba Inu with alert triangular ears and bright dark eyes, standing on light oak hardwood floor in golden afternoon light",
                f"a striking Siberian Husky puppy with piercing ice-blue eyes and thick silver-gray coat, {blanket_desc}",
                f"a loyal German Shepherd with rich black and tan coat, resting peacefully on lush green grass in soft golden hour light with alert intelligent gaze"
            ]
            if any(w in topic_lower for w in ["корги", "corgi"]):
                subject = corgi_variations[var % len(corgi_variations)]
            elif any(w in topic_lower for w in ["померан", "шпиц", "pomeranian", "spitz"]):
                subject = dog_archetypes[2]
            elif any(w in topic_lower for w in ["сиба", "shiba"]):
                subject = dog_archetypes[3]
            elif any(w in topic_lower for w in ["хаски", "husky"]):
                subject = dog_archetypes[4]
            elif any(w in topic_lower for w in ["овчарк", "shepherd"]):
                subject = dog_archetypes[5]
            elif any(w in topic_lower for w in ["щенок", "щенк", "puppy"]):
                subject = corgi_variations[var % len(corgi_variations)] if any(w in topic_lower for w in ["корги"]) else dog_archetypes[0]
            else:
                subject = dog_archetypes[var % len(dog_archetypes)]
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"

        # 7. ФЛОРИСТИКА (ПРИЛАВОК, ВРУЧЕНИЕ ЗРИТЕЛЮ POV, УЛЫБКА, БЕЗ НОУТБУКОВ)
        elif any(w in topic_lower for w in ["флорист", "девушка-флорист", "букет", "пион", "эвкалипт", "разнообрази", "однообрази", "авторский букет", "композици", "цветочн", "цветы", "далии", "гортензи"]):
            florist_archetypes = [
                # Вариация 0: POV вручение букета зрителю у прилавка с улыбкой
                "first-person POV candid photo of a friendly smiling female florist in a linen apron behind a rustic wooden flower shop counter, warmly extending and handing over a lavish bespoke bouquet of soft-pink peonies, white ranunculus, peach roses and silver eucalyptus directly toward the viewer, warm genuine welcoming smile",
                # Вариация 1: Процесс создания букета за верстаком
                "candid side-angle photo of an artisan florist in linen apron at a wooden workbench, carefully tying a silk ribbon around fresh flower stems, surrounded by garden shears, craft paper rolls and scattered dewy rose petals, warm sunlit flower boutique interior",
                # Вариация 2: Макро-натюрморт букета на мраморной витрине
                "close-up macro 45-degree angle photography of a breathtaking multi-flower artisan bouquet on a marble shop counter, individual fresh water droplets on delicate pink peony petals, blurred aesthetic flower boutique in soft golden background bokeh",
                # Вариация 3: Корзина с цветами
                "a cheerful florist holding a massive, overflowing woven wicker basket centered in frame with palms supporting the base, packed with diverse fresh blooms, layered pink peonies, white hydrangeas, magenta dahlias, chamomile, and lush eucalyptus foliage"
            ]
            subject = florist_archetypes[var % len(florist_archetypes)]
            environment = "bright sunlit artisan flower boutique, shelves with glass vases, fresh botanicals, warm morning light streaming through windows"

        # 8. ДЕСЕРТЫ И ВЫПЕЧКА (ПЕРЕМЕННАЯ ПОСУДА, РАЗРЕЗ С НАЧИНКОЙ, АСИММЕТРИЯ ПОЛИВАНИЯ)
        elif any(w in topic_lower for w in ["синнабон", "булочк", "кориц", "cinnamon", "rolls", "roll"]):
            subject = "three golden-brown artisan cinnamon rolls with perfectly spiraled glossy surfaces dusted generously with fine powdered sugar on a rustic circular wooden cutting board, accompanied by dark brown whole star anise pods, whole cinnamon sticks, and scattered brown sugar crystals, with a small creamy glaze bowl in background"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["печень", "печеньк", "кукис", "cookie", "cookies"]):
            cookie_archetypes = [
                "a generous pile of freshly baked golden-brown chocolate chip cookies with melted dark chocolate chunks on a rustic circular wooden serving board with rough natural bark edge, beside a steaming ceramic mug of coffee emitting delicate wisps of steam",
                "a rustic kraft paper gift box lined with crinkled parchment paper, filled with an assortment of freshly baked gourmet cookies studded with melted dark chocolate chunks and chopped walnuts, tied with natural jute twine",
                "macro eye-level shot of freshly baked chewy cookies on a marble pastry counter, with chocolate chips glistening and scattered cocoa nibs in soft focus"
            ]
            subject = cookie_archetypes[var % len(cookie_archetypes)]
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["торт", "ганаш", "шоколадн", "чизкейк", "пирог", "срез", "разрез", "начинк", "cake", "ganache"]):
            cake_archetypes = [
                # Вариация 0: Процесс глазирования (асимметричные подтеки, огибающие ягоды, полив из керамического кувшина)
                "gourmet artisanal multi-layered chocolate fudge cake on a dark slate board, rich dark chocolate glaze being poured smoothly from a ceramic pitcher corner, asymmetrical luscious glossy drips naturally cascading and deflecting around whole fresh ripe strawberries, delicate chocolate shavings on top, culinary action shot",
                # Вариация 1: Отрезанный кусочек рядом на фарфоре (демонстрация начинки)
                "luxurious gourmet chocolate cake on a vintage white porcelain plate with gold rim, with a cleanly cut appetizing single slice placed beside the cake revealing rich moist cocoa sponge layers, creamy mousse filling and glossy fruit confit cross-section, dessert fork resting on linen napkin",
                # Вариация 2: Целый торт на вращающейся мраморной подставке (Pedestal Stand)
                "a magnificent whole gourmet celebration cake garnished with fresh berries and chocolate curls, displayed elegantly on an elevated marble rotating cake stand with brass base, blurred warm French pastry boutique in background"
            ]
            subject = cake_archetypes[var % len(cake_archetypes)]
            environment = "cozy sunlit artisan pastry shop, warm morning window light, delicate ambient cafe bokeh"
        elif any(w in topic_lower for w in ["сыр", "сыроварн", "фермер", "рынок", "ярмарк", "сырные"]):
            subject = "a cheerful artisan seller wearing a beige knitted sweater and dark apron behind a rustic stall display of soft-ripened cheese wheels with white rinds, crumbly wedges, and crusty sourdough baguettes"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["касса", "магазин", "ритейл", "покупк", "продукты", "супермаркет"]):
            subject = "a friendly cashier in a black short-sleeved shirt and apron operating a black touchscreen POS cash register across a dark speckled counter, candid store interaction"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["балкон", "ночн", "небоскреб", "высотк", "сити", "balcony", "cityscape", "night city"]):
            subject = "a person seated on a modern high-rise balcony with a glass railing, hands typing on an open silver laptop displaying code lines, overlooking a sprawling illuminated nocturnal city skyline with glowing skyscrapers and street traffic bokeh below"
            environment = "modern evening balcony overlooking illuminated high-rise metropolis, cool night sky with warm glowing building windows"
        elif any(w in topic_lower for w in ["постель", "кровать", "одеял", "простын", "bed", "bedroom", "sheets", "linen"]):
            subject = "an open sleek silver laptop resting on rumpled cream-colored linen bedsheets beside a ceramic mug of hot tea and an open paperback book, bathed in soft golden morning sunlight streaming through sheer curtains"
            environment = "cozy sunlit bedroom with natural linen textures, morning sunbeams, peaceful relaxing atmosphere"
        elif any(w in topic_lower for w in ["блокнот", "конспект", "тетрадь", "учеб", "студент", "flatlay desk", "канцеляр"]):
            subject = "a neat top-down flatlay of a wooden study desk featuring an open spiral notebook with crisp handwritten ink notes and diagrams, a pair of classic tortoiseshell round glasses, a matte ceramic coffee cup with latte art, and a small potted green succulent"
            environment = "sunlit organized study workspace, natural oak desk surface, soft morning daylight, crisp educational aesthetic"
        elif any(w in topic_lower for w in ["постер", "плакат", "вывеск", "баннер", "билборд", "типографик", "надпись", "лайтбокс", "poster", "lightbox", "billboard", "signage"]):
            ooh_archetypes = [
                "a sleek minimalist framed poster mounted on a textured red-brown brick wall with visible mortar lines, featuring bold clean dark-gray typography against a crisp white background, with soft diffused overhead spotlighting and a light beige wooden door trim on the side",
                "an illuminated minimalist circular black metal lightbox sign hanging from a classical arched stone ceiling arcade, with warm golden backlighting highlighting subtle architectural stone textures",
                "a large clean architectural billboard mounted on the corner facade of a modern multi-story concrete and glass building against a clear blue sky, showing high-contrast minimalist graphic design",
                "bold motivational typography stenciled in crisp white paint across dark metallic industrial staircase risers, leading upward with dramatic directional side lighting and tactile metal textures"
            ]
            subject = ooh_archetypes[var % len(ooh_archetypes)]
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["посуд", "фарфор", "гончар", "глинян"]) or (any(w in topic_lower for w in ["керамик", "чаш", "блюд"]) and not any(w in topic_lower for w in ["кофе", "капучин", "латте", "чай", "маникюр", "ногти"])):
            subject = "an artisan ceramist wearing a casual long-sleeved shirt under an apron, holding a handcrafted bone porcelain cup in hands, distinct individual fingers, authentic tactile grip"
            environment = "Sunlit artisanal ceramic and tableware boutique, open oak display shelves"
        elif any(w in topic_lower for w in ["кожанк", "косух", "рок", "байкер", "тату", "biker", "leather jacket"]):
            subject = "a charismatic young woman in a textured black leather biker jacket with silver snaps and interlocking chain necklaces, candid expressive face, solid matte dark background"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["свитер", "осень", "парк", "уют", "скамейк", "autumn", "knitwear", "cozy"]):
            subject = "a young woman in an oversized cream cable-knit sweater and straight-leg denim jeans, sitting casually on a weathered wooden park bench with scattered autumn leaves in golden hour"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["человек", "основател", "фаундер", "девушк", "парен", "мужчин", "женщин", "портрет", "лицо"]):
            subject = "a confident young professional wearing modest casual clothes with genuine relaxed expression, looking into camera"
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
        non_human_terms = [
            "плата", "esp32", "esp-32", "arduino", "чип", "десерт", "торт", "синнабон", "булочк",
            "печень", "ролл", "выпечк", "стейк", "турбин", "перфоратор", "кот", "кошк", "котик",
            "котен", "собак", "щенок", "щенк", "корги", "шпиц", "померан", "сиба", "хаски",
            "овчарк", "постер", "плакат", "вывеск", "типографик", "билборд", "флэтлей", "flatlay",
            "блокнот", "конспект", "тетрадь"
        ]
        is_human_scene = (
            any(w in topic_lower or w in subject.lower() for w in [
                "человек", "девушк", "модел", "парень", "мужчин", "женщин", "лицо", "портрет",
                "мастер", "доктор", "врач", "тренер", "студент", "бариста", "юрист", "основател",
                "фаундер", "разработчик", "программист", "инженер", "model", "woman", "man",
                "person", "barista", "doctor", "founder", "florist", "developer", "engineer", "male", "female"
            ]) and not any(w in topic_lower or w in subject.lower() for w in non_human_terms)
        )
        
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
            is_action_hands = any(w in topic_lower or w in subject.lower() for w in ["маникюр", "ногти", "nail", "manicure", "держит", "руки", "пайк", "осциллограф", "инструмент", "букет", "пион", "чашк", "кружк", "holding", "hands", "soldering", "workbench", "bouquet", "cup", "mug"])

            optics_extra = ""
            if any(w in topic_lower or w in subject.lower() for w in ["маникюр", "ногти", "nail", "manicure", "ногот"]):
                optics_extra = "distinct anatomically correct 5 slender fingers with neat natural cuticles, perfectly shaped smooth nail plates, clean separation between fingers, "
            elif is_action_hands:
                optics_extra = "distinct clean separation between fingers and held objects, anatomically correct 5 fingers with clear knuckles, natural hand grasp, "
            elif is_full_body:
                optics_extra = "sharp full-body frame, crisp clothing fabric texture, "

            # Физический материализованный якорь переднего плана (СТРОГАЯ ИЗОЛЯЦИЯ ПО НИШАМ)
            if any(w in topic_lower or w in subject.lower() for w in ["корги", "щенок", "щенк", "собак", "кот", "кошк", "котен", "питомц", "puppy", "dog", "cat"]):
                foreground_anchor = "(blurred edge of cozy knit blanket in extreme foreground:1.2)"
            elif any(w in topic_lower or w in subject.lower() for w in ["маникюр", "ногти", "гель-лак", "нейл", "ногот", "nail", "manicure"]):
                foreground_anchor = "(blurred edge of soft knitwear sleeve in extreme foreground:1.2)"
            elif any(w in topic_lower or w in subject.lower() for w in ["кофе", "капучин", "латте", "эспрессо", "круассан", "coffee", "cappuccino", "croissant"]):
                foreground_anchor = "(blurred edge of rustic ceramic saucer in extreme foreground:1.2)"
            elif any(w in topic_lower or w in subject.lower() for w in ["стейк", "рибай", "шеф", "повар", "мясо", "steak", "ribeye", "кулинар"]):
                foreground_anchor = "(blurred wine glass stem and edge of walnut board in extreme foreground:1.2)"
            elif any(w in topic_lower or w in subject.lower() for w in ["разработчик", "программист", "терминал", "ide", "ноутбук", "клавиатур", "developer", "команд", "startup", "devpulse"]):
                foreground_anchor = "(blurred edge of modern desk and ceramic mug in extreme foreground:1.2)"
            elif any(w in topic_lower or w in subject.lower() for w in ["десерт", "торт", "мусс", "пирожн", "чизкейк", "выпечк", "синнабон", "dessert", "pastry", "cake"]):
                foreground_anchor = "(blurred vintage dessert fork and linen napkin in extreme foreground:1.2)"
            elif any(w in topic_lower or w in subject.lower() for w in ["букет", "пион", "флорист", "цвет"]):
                foreground_anchor = "(blurred dewy flower petal and craft twine in extreme foreground:1.2)"
            elif any(w in topic_lower or w in subject.lower() for w in ["плата", "esp32", "пайк", "электроник"]):
                foreground_anchor = "(blurred precision tweezers and wire spool in extreme foreground:1.2)"
            else:
                foreground_anchor = "(blurred foreground edge in extreme foreground:1.1)"

            depth_atmosphere = (
                f"{foreground_anchor}, "
                "smooth progressive focal falloff, f/1.2 depth of field, anamorphic bokeh, "
                "volumetric lighting, subtle atmospheric haze, floating dust particles, cinematic atmosphere, "
                "warm foreground key lighting contrasting with subtle cool background ambient light, "
                "strong directional side light, Rembrandt lighting, deep micro-shadows, dramatic light falloff"
            )

            full_prompt = (
                f"35mm analog photography, candid snapshot of {subject}. "
                f"{environment}, {depth_atmosphere}, {optics_extra}"
                f"{texture_desc}."
            )
        else:
            texture_desc = (
                "tactile material texture, physical surface imperfections, natural reflections, "
                "(35mm film grain, ISO 400:1.1), authentic analog depth"
            )
            # Физический материализованный якорь переднего плана
            if any(w in topic_lower or w in subject.lower() for w in ["корги", "щенок", "щенк", "собак", "кот", "кошк", "котен", "питомц", "puppy", "dog", "cat"]):
                foreground_anchor = "(blurred edge of cozy knit blanket in extreme foreground:1.2)"
            elif any(w in topic_lower or w in subject.lower() for w in ["маникюр", "ногти", "гель-лак", "нейл", "ногот", "nail", "manicure"]):
                foreground_anchor = "(blurred edge of soft knitwear sleeve in extreme foreground:1.2)"
            elif any(w in topic_lower or w in subject.lower() for w in ["кофе", "капучин", "латте", "эспрессо", "круассан", "coffee", "cappuccino", "croissant"]):
                foreground_anchor = "(blurred edge of rustic ceramic saucer in extreme foreground:1.2)"
            elif any(w in topic_lower or w in subject.lower() for w in ["стейк", "рибай", "шеф", "повар", "мясо", "steak", "ribeye", "кулинар"]):
                foreground_anchor = "(blurred wine glass stem and edge of walnut board in extreme foreground:1.2)"
            elif any(w in topic_lower or w in subject.lower() for w in ["разработчик", "программист", "терминал", "ide", "ноутбук", "клавиатур", "developer", "команд", "startup", "devpulse"]):
                foreground_anchor = "(blurred edge of modern desk and ceramic mug in extreme foreground:1.2)"
            elif any(w in topic_lower or w in subject.lower() for w in ["десерт", "торт", "мусс", "пирожн", "чизкейк", "выпечк", "синнабон", "dessert", "pastry", "cake"]):
                foreground_anchor = "(blurred vintage dessert fork and linen napkin in extreme foreground:1.2)"
            elif any(w in topic_lower or w in subject.lower() for w in ["букет", "пион", "флорист", "цвет"]):
                foreground_anchor = "(blurred dewy flower petal and craft twine in extreme foreground:1.2)"
            elif any(w in topic_lower or w in subject.lower() for w in ["плата", "esp32", "пайк", "электроник"]):
                foreground_anchor = "(blurred precision tweezers and wire spool in extreme foreground:1.2)"
            else:
                foreground_anchor = "(blurred foreground edge in extreme foreground:1.1)"

            depth_atmosphere = (
                f"{foreground_anchor}, "
                "smooth progressive focal falloff, f/1.2 depth of field, anamorphic bokeh, "
                "volumetric lighting, subtle atmospheric haze, floating dust particles, cinematic atmosphere, "
                "warm foreground key lighting contrasting with subtle cool background ambient light, "
                "strong directional side lighting, deep chiaroscuro micro-shadows, dramatic light falloff"
            )
            full_prompt = (
                f"35mm analog photography, candid snapshot of {subject}. "
                f"{environment}, {depth_atmosphere}, "
                f"{lighting}. {perspective}, {texture_desc}."
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
        "(flat lighting, HDR, softbox, even illumination, lifted shadows, studio fill light:1.35), "
        "(tone mapping, washed out blacks, washed out shadows, aggressive shadow recovery:1.3), "
        "(fake chroma key blur, abrupt cut-and-paste background, cardboard cutout look, computational fake blur:1.3), "
        "(extra fingers, mutated joints, fused fingers:1.3), (deformed knuckles, missing phalanges, melting fingers, hand-object fusion:1.25), (stems penetrating through fingers, objects melting into hands:1.2), "
        "(dense smoke, thick steam plumes, vape smoke overlay, opaque white smoke, cigarette smoke:1.3), "
        "(lamp pointed directly at screen, screen glare, financial stock trading charts on screens, sad depressed expression in retail:1.25), "
        "(yarn ball in food or restaurant, mechanical keyboard in bakery or food, out of place objects:1.25), "
        "(identical cloned drips, symmetrical plastic icing drips, artificial repetitive patterns:1.2), "
        "bare shoulders, sideboob, bare back, bare arms, naked under apron, open-back, halter top, cleavage, exposed skin, bare chest, shirtless, half-naked, unclothed, revealing clothing, deep neckline, bare midriff, lingerie, swimsuit, bikini, underwear, suggestive, erotic, "
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
        if custom_prompt and len(custom_prompt.strip()) > 30:
            prompt_data["positive_prompt"] = custom_prompt
            print(f"[PhotoGeneratorSkill] 🎯 Использован пользовательский кастомный промпт:\n  👉 {custom_prompt}\n")

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
