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
        "soft_diffused": "Soft diffused morning window daylight with gentle natural gradients",
        "dual_office": "Subtle dual lighting with a warm 3000K matte black desk lamp glow contrasting with cool 5500K natural daylight from office windows",
        "overcast_diffused": "Soft diffused natural daylight under an overcast sky, gentle even wrap with no harsh specular highlights",
        "warm_pendant": "Hanging pendant filament lamps casting a soft warm ambient glow, rich environmental depth",
        "hard_chiaroscuro": "Strong single directional warm key light casting deep dramatic chiaroscuro shadows with high contrast falloff",
        "golden_hour_rim": "Warm directional golden hour glow casting gentle rim light along hair and shoulders with creamy atmospheric bokeh",
        "editorial_studio": "Single directional studio key light from upper-left with deep shadow falloff, high-contrast micro-textures"
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
        "culinary_45_slice": "45-degree angled perspective with crisp focal depth",
        "oversized_hero": "Centered medium shot framing an oversized overflowing basket in front of torso, sharp macro focus on textures and petals",
        "candid_counter": "Medium eye-level shot, candid transactional interaction across a speckled counter with POS touch register",
        "layered_artisan_table": "Layered multi-tiered tabletop display, deep foreground arrangement with rustic wooden cutting boards, linen cloth, and chalk price tags",
        "contemplative_profile": "Medium close-up profile shot, subject leaning thoughtfully, shallow depth of field with creamy bokeh",
        "active_desk_focus": "Slightly elevated side-angle desk perspective, subject leaning forward typing intently, foreground notebooks and coffee cup",
        "macro_nail_close_up": "Tight macro close-up lens, f/2.8 shallow depth of field, razor-sharp focus on nail plate curvature and neat cuticles, creamy background bokeh"
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
            "маникюр", "ногти", "гель-лак", "постер", "плакат", "вывеск", "типографик", "билборд",
            "цвет", "флорист", "букет", "пион", "посуд", "фарфор", "керамик", "глинян", "гончар",
            "кофе", "пекарн", "десерт", "торт", "синнабон", "булочк", "печень", "шоколад",
            "электроник", "плата", "кот", "кошк", "котик", "котен", "собак", "щенок", "щенк",
            "корги", "шпиц", "померан", "сиба", "хаски", "овчарк", "детейлинг", "стоматолог",
            "недвижим", "балкон", "блокнот", "конспект", "постель", "it", "saas", "martech"
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
                {"setting": "urban outdoor park with gray cobblestone walkway scattered with golden autumn leaves in late afternoon golden hour", "props": "ornate wrought-iron wooden bench, sparse golden trees and warm glowing streetlights in creamy background bokeh"},
                {"setting": "scenic nature overlook with mature tree trunk and rugged bark at sunset golden hour", "props": "cozy cream ribbed knit sweater, thick earthy plaid scarf, panoramic warm skyline in dreamy bokeh"},
                {"setting": "editorial studio portrait setting against a solid matte dark background", "props": "textured black leather biker jacket with silver snaps, layered interlocking silver chain necklaces, high-contrast single key light"},
                {"setting": "intimate atmospheric vintage room with warm orange lamp light casting dramatic long shadows", "props": "worn denim armchair with frayed texture, muted rose tones, cinematic chiaroscuro mood"}
            ],
            "маникюр": [
                {"setting": "cozy aesthetic nail studio with textured cream chunky-knit fabric in foreground", "props": "delicate dried autumn maple leaves, soft neutral beige background bokeh"},
                {"setting": "warm ambient coffee lounge with soft circular golden bokeh lights", "props": "glossy ceramic coffee cup with intricate white latte art, warm intimate glow"},
                {"setting": "minimalist luxury nail bar with warm oak surface and soft diffused daylight", "props": "ribbed maroon knit sweater sleeve cuff, rich tactile textures"},
                {"setting": "chic modern beauty salon with soft indirect lighting", "props": "natural linen cloth, scattered burnt orange autumn leaves, elegant seasonal ambiance"}
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
        # Кадр фиксирует кульминацию арки: идеальный момент гармонии, радости или безопасности.
        # =========================================================================
        from skills.visual_knowledge_researcher import VisualKnowledgeResearcher
        visual_spec = VisualKnowledgeResearcher.research_visual_spec_sync(topic)

        # 1. Проверяем конкретные сущности из темы (Topic Subjects) ПЕРЕД общими нишами
        if any(w in topic_lower for w in ["кот", "кошк", "котик", "котен", "котён", "cat", "kitten"]):
            cat_archetypes = [
                "macro eye-level pet portrait of an adorable ginger tabby kitten with vibrant orange stripes and luminous blue-green eyes, stretching playfully in a warm diagonal sunbeam across a rustic wooden floor",
                "high-angle top-down macro shot of a tiny fluffy gray and white kitten lying curled on a soft ivory knit blanket, gazing directly up at the camera with wide curious amber eyes",
                "sleek black cat with glossy midnight fur and striking golden-yellow eyes, nestled comfortably on a cozy cream-toned textured fleece blanket in warm ambient lighting",
                "charming fluffy black cat with luminous emerald eyes, sitting on a wooden desk with a tiny pink tongue peeking out in a playful blep expression beside soft warm lamplight",
                "macro eye-level commercial pet portrait of a gorgeous fluffy domestic tabby cat with bright sharp amber eyes and long white whiskers, resting comfortably on a wooden desk beside an open laptop displaying clean analytics charts"
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
        elif any(w in topic_lower for w in ["собак", "щенок", "щенк", "корги", "шпиц", "померан", "сиба", "хаски", "овчарк"]) or any(re.search(rf'\b{w}\b', topic_lower) for w in ["пес", "пёс", "dog", "puppy"]):
            dog_archetypes = [
                "a fluffy, golden-furred puppy with soft long light golden fur, sitting upright on a textured beige carpet, gazing with large expressive round dark eyes and head tilted curiously to the right",
                "an adorable Welsh Corgi with golden and white fur, upright rounded ears, and joyful face, sitting happily on a wooden floor in bright morning sunlight",
                "a fluffy cream-colored Pomeranian puppy sitting on a soft woven rug, playfully raising one front paw in the air with delicate black paw pads visible and a cheerful pant",
                "a neat red Shiba Inu with alert triangular ears and bright dark eyes, standing on light oak hardwood floor in golden afternoon light, looking into the lens with keen curiosity",
                "a striking Siberian Husky with piercing ice-blue eyes and thick silver-gray coat, seated in a car passenger seat looking out the window with an astonished, wide-eyed curious expression",
                "a loyal German Shepherd with rich black and tan coat, resting peacefully on lush green grass in soft golden hour light with alert intelligent gaze"
            ]
            if any(w in topic_lower for w in ["корги", "corgi"]):
                subject = dog_archetypes[1]
            elif any(w in topic_lower for w in ["померан", "шпиц", "pomeranian", "spitz"]):
                subject = dog_archetypes[2]
            elif any(w in topic_lower for w in ["сиба", "shiba"]):
                subject = dog_archetypes[3]
            elif any(w in topic_lower for w in ["хаски", "husky"]):
                subject = dog_archetypes[4]
            elif any(w in topic_lower for w in ["овчарк", "shepherd"]):
                subject = dog_archetypes[5]
            elif any(w in topic_lower for w in ["щенок", "щенк", "puppy"]):
                subject = dog_archetypes[0]
            else:
                subject = dog_archetypes[var % len(dog_archetypes)]
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["флорист", "девушка-флорист", "букет", "пион", "эвкалипт", "цветочн", "цветы", "далии", "гортензи"]):
            subject = "a florist holding a massive, overflowing woven wicker basket centered in frame with palms supporting the base, filled with dense fresh blooms, pink peonies, magenta dahlias and cascading green foliage"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["шеф", "повар", "кулинар", "кухня", "стейк", "мясо", "chef", "culinary"]):
            subject = "a focused male chef wearing a simple white short-sleeved t-shirt beneath a textured dark apron, gripping a chef's knife slicing through deep-red meat on a rustic wooden board, Rembrandt chiaroscuro"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["сыр", "сыроварн", "фермер", "рынок", "ярмарк", "сырные"]):
            subject = "a cheerful artisan seller wearing a beige knitted sweater and dark apron behind a rustic stall display of soft-ripened cheese wheels with white rinds, crumbly wedges, and crusty sourdough baguettes"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["касса", "магазин", "ритейл", "покупк", "продукты", "супермаркет"]):
            subject = "a friendly cashier in a black short-sleeved shirt and apron operating a black touchscreen POS cash register across a dark speckled counter, candid store interaction"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["синнабон", "булочк", "кориц", "cinnamon", "rolls", "roll"]):
            subject = "three golden-brown artisan cinnamon rolls with perfectly spiraled glossy surfaces dusted generously with fine powdered sugar on a rustic circular wooden cutting board, accompanied by dark brown whole star anise pods, whole cinnamon sticks, and scattered brown sugar crystals, with a small creamy glaze bowl in background"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["печень", "печеньк", "кукис", "cookie", "cookies"]):
            cookie_archetypes = [
                "a generous pile of freshly baked golden-brown chocolate chip cookies with melted dark chocolate chunks on a rustic circular wooden serving board with rough natural bark edge, beside a steaming ceramic mug of coffee emitting delicate wisps of steam",
                "a rustic kraft paper gift box lined with crinkled parchment paper, filled with an assortment of freshly baked gourmet cookies studded with melted dark chocolate chunks and chopped walnuts, tied with natural jute twine",
                "macro eye-level shot of freshly baked chewy cookies on a marble pastry counter, with chocolate chips glistening and scattered cocoa nibs in soft focus",
                "an artisan baker's tray with warm freshly baked chocolate chunk cookies resting on a textured linen cloth with soft morning window light"
            ]
            subject = cookie_archetypes[var % len(cookie_archetypes)]
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["торт", "ганаш", "шоколадн", "чизкейк", "пирог", "срез", "разрез", "начинк", "cake", "ganache"]):
            cake_archetypes = [
                "a decadent multi-layered chocolate fudge cake with dark chocolate sponge and rich cream, thick glossy molten chocolate ganache being poured over the top cascading down the sides in luscious drips, crowned with fresh ripe strawberries and shaved chocolate curls on a dark slate board",
                "luxurious gourmet artisanal cake on a minimalist white porcelain plate, with a cleanly cut appetizing single slice placed beside it revealing moist rich sponge layers and creamy filling, dusted with shaved chocolate flakes, commercial dessert showcase",
                "a delicate layered berry mousse cake garnished with fresh raspberries, blueberries and mint leaves, on a vintage ceramic stand in soft morning window light",
                "a velvety Basque cheesecake with a caramelized golden-brown top, set on a rustic wooden board with a dollop of cream and blackberry coulis"
            ]
            subject = cake_archetypes[var % len(cake_archetypes)]
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
        elif any(w in topic_lower for w in ["разработчик", "программист", "инженер", "developer", "tech developer", "кодер", "аналитик"]) or any(w in niche_lower for w in ["it", "saas", "martech", "ии"]):
            it_archetypes = [
                "a focused young man with neat beard wearing a denim jacket over a plain white t-shirt, typing intently on a sleek silver laptop under a warm desk lamp",
                "a contemplative tech specialist in clear glasses with right hand curled at chin in deep thought, seated at wooden table with black laptop under warm floor lamp",
                "a professional data analyst in dark charcoal sweater seated in ergonomic mesh chair, looking at large curved monitor with glowing data graphs",
                "a dedicated engineer in light blue button-up shirt with rolled sleeves at office desk, hand resting on forehead in deep focus, laptop with whiteboard in background"
            ]
            subject = it_archetypes[var]
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["свитер", "осень", "парк", "уют", "скамейк", "autumn", "knitwear", "cozy"]):
            subject = "a young woman in an oversized cream cable-knit sweater and straight-leg denim jeans, sitting casually on a weathered wooden park bench with scattered autumn leaves in golden hour"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["кожанк", "косух", "рок", "байкер", "тату", "biker", "leather jacket"]):
            subject = "a charismatic young woman in a textured black leather biker jacket with silver snaps and interlocking chain necklaces, candid expressive face, solid matte dark background"
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["маникюр", "ногти", "гель-лак", "ногот", "nail", "manicure", "педикюр"]):
            nail_archetypes = [
                "macro close-up of a slender hand with modern squared-off almond nails in matte deep navy blue adorned with delicate stylized orange maple leaf nail art, resting gently against a plush neutral knit fabric",
                "macro shot of elegant hands with long almond-shaped nails in a smooth matte gradient ombre transitioning from deep burgundy to warm terracotta, gently cradling a glossy orange ceramic coffee cup with latte leaf foam art",
                "pair of slender fair-skinned hands in relaxed overlapping pose resting on a cream-colored chunky-knit sweater, showcasing nails with shimmering copper-amber magnetic finish and delicate autumn leaf decals",
                "close-up of a woman's hand with almond-shaped nails painted in rich chocolate brown and matte off-white with fine burnt-orange maple leaf brushwork, fingers elegantly curled over warm wooden table"
            ]
            subject = nail_archetypes[var]
            environment = f"{niche_universe['setting']}, {niche_universe['props']}"
        elif any(w in topic_lower for w in ["посуд", "фарфор", "керамик", "чаш", "блюд", "гончар", "глинян"]):
            subject = "an artisan wearing a casual long-sleeved shirt under an apron, holding a handcrafted bone porcelain cup in hands, distinct individual fingers, authentic tactile grip"
            environment = "Sunlit artisanal ceramic and tableware boutique, open oak display shelves"
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
        "(extra fingers, mutated joints, fused fingers:1.3), (deformed knuckles, missing phalanges, melting fingers, hand-object fusion:1.25), (stems penetrating through fingers, objects melting into hands:1.2), "
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
