# File: ai/skills/visual_knowledge_researcher.py
"""
VisualKnowledgeResearcher — Универсальный мульти-доменный модуль параллельного поиска
и визуальной спецификации объектов для ВСЕХ сфер бизнеса (стоматология, кулинария,
кофейни/десерты, косметика/бьюти, инструмент/ремонт, автотюнинг, электроника/IoT,
ювелирные изделия, флористика, фитнес, недвижимость, fashion/приват).
"""

from __future__ import annotations

import os
import re
import asyncio
import logging
from typing import Dict, Any, List, Optional

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger("visual_knowledge_researcher")


class VisualKnowledgeResearcher:
    """
    Исследователь визуальных деталей и точных спецификаций оборудования, микроэлектроники,
    медицинских систем, блюд высокой кухни, строительных инструментов и предметов роскоши.
    Переводит инженерные термины и SKU в фотореалистичные физические дескрипторы для ComfyUI.
    """

    # Исчерпывающий мастер-реестр верифицированных физических спецификаций
    CURATED_VISUAL_SPECS: Dict[str, Dict[str, str]] = {
        # =========================================================================
        # 1. СТОМАТОЛОГИЯ, ИМПЛАНТОЛОГИЯ И МЕДИЦИНА
        # =========================================================================
        "винир": {
            "en_term": "ultra-thin E-max ceramic dental veneers",
            "visual_description": "ultra-thin handcrafted E-max ceramic dental veneers with lifelike translucent incisal enamel layering, realistic micro-textured tooth surface reflecting ring-flash highlights, natural mamelon anatomy, resting on a clean clinical titanium tray, precision macro dental photography",
            "text_story": "ультратонкие керамические виниры E-max: естественная полупрозрачность режущего края, анатомическая глубина цвета и голливудская эстетика без гипертрофированной белизны"
        },
        "имплант": {
            "en_term": "precision medical titanium dental implant and zirconia abutment",
            "visual_description": "precision-milled medical-grade titanium dental implant fixture with microscopic bone-integration threads, polished anatomical zirconia abutment crown, clean sterile stainless steel dental instrument tray, clinical macro lighting",
            "text_story": "премиальные дентальные имплантаты из биосовместимого титана с гидрофильной поверхностью для надежной остеоинтеграции и пожизненной гарантии"
        },
        "элайнер": {
            "en_term": "crystal-clear invisible orthodontic dental aligners",
            "visual_description": "pair of crystal-clear medical polymer invisible orthodontic aligners, pristine transparent gloss with laser-etched precision staging markers, resting beside a sleek modern matte pastel case with glistening water drops",
            "text_story": "прозрачные ортодонтические элайнеры: незаметное и комфортное исправление прикуса без металлических брекетов и ограничений в рационе"
        },
        "отбеливан": {
            "en_term": "professional dental whitening treatment",
            "visual_description": "radiant healthy natural smile with flawless enamel gloss, gentle cool-blue LED curing light reflection, immaculate oral aesthetics, macro portrait",
            "text_story": "бережное кабинетное отбеливание зубов на 6–8 тонов: укрепление эмали минеральным комплексом и стойкий белоснежный результат"
        },
        "брекет": {
            "en_term": "aesthetic sapphire / ceramic orthodontic brackets",
            "visual_description": "aesthetic crystal-clear monocrystalline sapphire dental brackets with white rhodium aesthetic archwire, glistening teeth enamel in macro view",
            "text_story": "сапфировые эстетические брекет-системы: кристальная прозрачность на зубах, надежная фиксация и быстрый путь к ровной улыбке"
        },

        # =========================================================================
        # 2. КУЛИНАРИЯ, РЕСТОРАНЫ И ГАСТРОНОМИЯ
        # =========================================================================
        "стейк": {
            "en_term": "perfectly seared Wagyu ribeye steak",
            "visual_description": "thick dry-aged Wagyu ribeye steak with deep caramelized diamond sear marks, warm pink medium-rare center, sprinkled with flaky Maldon sea salt crystals and fresh cracked black pepper, garnished with a sprig of charred fresh rosemary on a rustic charred oak board",
            "text_story": "мраморный стейк Рибай зернового откорма сухого вызревания: карамелизованная хрустящая корочка, тающая текстура и насыщенный мясной сок"
        },
        "рибай": {
            "en_term": "perfectly seared Wagyu ribeye steak",
            "visual_description": "thick dry-aged Wagyu ribeye steak with deep caramelized diamond sear marks, warm pink medium-rare center, sprinkled with flaky Maldon sea salt crystals and fresh cracked black pepper, garnished with a sprig of charred fresh rosemary on a rustic charred oak board",
            "text_story": "мраморный стейк Рибай зернового откорма сухого вызревания: карамелизованная хрустящая корочка, тающая текстура и насыщенный мясной сок"
        },
        "устриц": {
            "en_term": "fresh Fine de Claire oysters on crushed ice platter",
            "visual_description": "platter of freshly shucked premium Fine de Claire oysters nestled on a bed of glistening crushed crystal ice, accompanied by fresh sliced Meyer lemon wedges, delicate shallot mignonette sauce, cold seawater brine glistening in sunlight",
            "text_story": "отборные устрицы Фин де Клер на ледяном плато: свежайший морской бриз, минеральные ноты и подача с классическим луковым соусом миньонет"
        },
        "пицц": {
            "en_term": "authentic wood-fired Neapolitan pizza",
            "visual_description": "authentic wood-fired Neapolitan pizza with blistered leopard-spotted airy charred crust, molten creamy Fior di Latte mozzarella, vibrant red San Marzano tomato sauce, fresh fragrant green basil leaves, glistening drizzle of extra virgin olive oil",
            "text_story": "неаполитанская пицца из дровяной печи: воздушные бортики с леопардовой корочкой, сыр фиор ди латте и томаты Сан-Марцано"
        },
        "суши": {
            "en_term": "artisan premium sushi and nigiri platter",
            "visual_description": "exquisite omakase sushi platter featuring glossy fresh Atlantic salmon nigiri, marbled bluefin otoro tuna, brushed with nikiri soy glaze, delicate pickled ginger flower, freshly grated wasabi on a slate black stone platter",
            "text_story": "авторские суши и нигири с охлажденным диким лососем и мраморным тунцом блюфин: идеальный баланс теплого риса и свежайшей рыбы"
        },
        "бургер": {
            "en_term": "gourmet smash burger on toasted brioche",
            "visual_description": "mouthwatering gourmet double smash burger on a glossy toasted golden brioche bun, overflowing with melting aged cheddar cheese, crispy smoked bacon ribbons, caramelized shallot jam, crisp iceberg lettuce and house secret sauce dripping",
            "text_story": "сочный авторский бургер на сливочной булочке бриошь: двойная котлета из мраморной говядины с хрустящей корочкой smash и выдержанным чеддером"
        },

        # =========================================================================
        # 3. КОФЕЙНИ, БАРИСТА, ВЫПЕЧКА И ДЕСЕРТЫ
        # =========================================================================
        "латте": {
            "en_term": "specialty latte art in handcrafted ceramic cup",
            "visual_description": "specialty cafe latte with silky glossy microfoam latte art rosetta pouring in a heavy matte ceramic artisanal cup, contrasting rich golden-brown espresso crema ring, freshly roasted coffee beans scattered on a warm natural oak counter",
            "text_story": "авторский латте на спешелти зерне свежей обжарки: шелковистая микропена, сбалансированный сливочно-ореховый вкус и безупречный латте-арт"
        },
        "капучино": {
            "en_term": "specialty cappuccino with silky microfoam",
            "visual_description": "velvety specialty cappuccino with thick glossy microfoam dome, delicate chocolate dusting swirl in a warm ceramic cup, steaming aroma in golden morning light",
            "text_story": "классический капучино с плотной бархатистой пеной: идеальный баланс плотного эспрессо и натурального фермерского молока"
        },
        "фильтр": {
            "en_term": "specialty V60 pour-over single-origin coffee",
            "visual_description": "single-origin pour-over filter coffee brewed through a crystal V60 dripper into an elegant glass carafe, glowing amber translucence, delicate steam rising",
            "text_story": "фильтр-кофе светлой обжарки сорта спешелти: раскрытие тонких дескрипторов бергамота, спелых ягод и жасмина"
        },
        "круассан": {
            "en_term": "artisan flaky French butter croissant",
            "visual_description": "freshly baked artisan French butter croissant with ultra-crisp golden honeycomb lamination crust, delicate butter flakes glistening, soft airy steaming interior cross-section",
            "text_story": "настоящий французский круассан на новозеландском сливочном масле 82.5%: сотни тончайших слоев, хруст корочки и тающая сердцевина"
        },
        "чизкейк": {
            "en_term": "Basque burnt San Sebastian cheesecake",
            "visual_description": "slice of authentic San Sebastian Basque burnt cheesecake with deeply caramelized charred dark top, oozy creamy molten center gently collapsing on a handcrafted ceramic plate",
            "text_story": "знаменитый баскский чизкейк Сан-Себастьян: карамелизованная обожженная корочка и нежнейший, почти жидкий сливочный центр"
        },
        "дубайский шоколад": {
            "en_term": "Dubai Fix pistachio kataifi chocolate",
            "visual_description": "thick artisanal milk chocolate bar broken open showing vibrant emerald pistachio cream layered with crisp golden toasted kataifi pastry threads",
            "text_story": "хрустящее золотистое тесто катаифи, насыщенная натуральная фисташковая паста и премиальный молочный шоколад"
        },
        "франжипан": {
            "en_term": "Frangipane almond cream pastry",
            "visual_description": "golden layered puff pastry roll filled with rich velvety almond frangipane cream, topped with toasted caramelized sliced almond flakes and fine powdered sugar",
            "text_story": "классический французский крем франжипан из тертого отборного миндаля, запеченный в хрустящем слоеном тесте"
        },
        "тирамису": {
            "en_term": "classic Venetian artisanal Tiramisu",
            "visual_description": "rustic glass dish of artisanal Italian Tiramisu, layered with espresso-soaked Savoiardi ladyfingers, velvety mascarpone cream and dusted with a generous cloud of dark Dutch cocoa powder",
            "text_story": "традиционный венецианский тирамису: печенье савоярди, пропитанное крепким эспрессо с марсалой, и крем из свежего маскарпоне"
        },
        "кулич": {
            "en_term": "traditional tall artisanal Easter Kulich in pleated panettone paper mold with dripping white glaze",
            "visual_description": "tall cylindrical golden-brown artisanal Easter Kulich brioche cake baked in a decorative pleated brown parchment paper Panettone baking mold with subtle gold filigree patterns, crowned with a thick snowy-white royal sugar glaze dripping naturally down the domed crust, artfully garnished with dried lavender flowers, chopped green pistachios, candied orange peel and delicate pastel sugar pearls, warm festive daylight",
            "text_story": "пышный сдобный пасхальный кулич в рифленой форме для панеттоне: волокнистый золотистый мякиш с вымоченным в роме изюмом, плотная белоснежная глазурь с аппетитными подтеками и авторский весенний декор"
        },
        "пасх": {
            "en_term": "traditional truncated pyramid cottage cheese Paskha with embossed relief",
            "visual_description": "sculpted four-sided truncated pyramid of rich velvety farm cottage cheese Paskha with embossed traditional relief lettering on its sides, garnished with candied fruits, toasted sliced almonds, dried cranberries and spring flowers on a porcelain stand",
            "text_story": "традиционная творожная пасха в форме усеченной пирамиды из отборного фермерского творога со сливочным маслом, цукатами и лепестками миндаля"
        },
        "форм": {
            "en_term": "pleated parchment panettone paper baking molds and wooden paskha molds",
            "visual_description": "set of premium pleated brown parchment paper Panettone baking molds with elegant gold filigree patterns standing on a rustic baker's floured wooden table, alongside a carved wooden paskha pyramid mold, surrounded by fresh farm eggs and cinnamon sticks",
            "text_story": "жаропрочные формы для выпечки куличей и панеттоне из гофрированного пергамента с золотым тиснением и разборные пасочницы для творожной пасхи"
        },
        "торт": {
            "en_term": "gourmet artisanal multi-layer cake with cleanly cut slice",
            "visual_description": "luxurious gourmet artisanal cake on a minimalist white porcelain plate, with a cleanly cut appetizing single slice placed beside it revealing moist rich sponge layers and creamy filling, dusted with shaved chocolate curls or fresh berry garnish, commercial dessert showcase",
            "text_story": "авторский торт ручной работы: нежные пропитанные бисквитные коржи, воздушный сливочный крем и гармоничный баланс сладости"
        },
        "синнабон": {
            "en_term": "warm fresh cinnamon roll with cream cheese frosting",
            "visual_description": "warm freshly baked swirled cinnamon roll pastry overflowing with melting rich cream cheese vanilla glaze, glistening spiced caramelized cinnamon sugar spirals, soft steaming crumb",
            "text_story": "ароматная булочка с корицей сорта макассар и щедрой шапкой тающего сливочного крема"
        },
        "эклер": {
            "en_term": "gourmet French chocolate choux pastry eclairs",
            "visual_description": "trio of elegant French choux pastry eclairs with mirror-like dark chocolate glaze, filled with luscious vanilla bean cream, garnished with delicate gold leaf flakes",
            "text_story": "французские эклеры из заварного теста с шелковистым кремом дипломат и зеркальной шоколадной глазурью"
        },
        "макарон": {
            "en_term": "delicate French almond macarons",
            "visual_description": "stack of delicate pastel French almond macarons with ruffled feet (pied) and smooth glossy shells, sandwiched with rich velvety fruit ganache, on a marble tray",
            "text_story": "настоящие французские макарон из тончайшей миндальной муки с сочными ягодными и шоколадными начинками"
        },
        "шаурм": {
            "en_term": "crispy grilled artisan chicken shawarma wrap",
            "visual_description": "crispy toasted golden lavash shawarma wrap cut in half with visible grill marks, overflowing with juicy marinated roasted chicken, crisp fresh cucumbers, ripe tomatoes, fresh herbs and garlic sauce",
            "text_story": "сочная сытная шаурма в хрустящем лаваше с гриля: отборное мясо, свежие хрустящие овощи и фирменный чесночный соус"
        },
        "пицц": {
            "en_term": "authentic Neapolitan wood-fired pizza with leopard crust",
            "visual_description": "authentic wood-fired Neapolitan pizza with puffy charred leopard-spotted crust, bubbling melted buffalo mozzarella, San Marzano tomato sauce and fresh green basil leaves, stringy cheese pull slice being lifted",
            "text_story": "римская и неаполитанская пицца из дровяной печи: воздушные бортики длительной ферментации, тянущаяся моцарелла и спелые томаты"
        },
        "ролл": {
            "en_term": "premium Philadelphia salmon sushi roll",
            "visual_description": "premium Philadelphia sushi roll wrapped with thick glistening fresh Atlantic salmon, stuffed with rich creamy cheese and crisp cucumber, garnished with flying fish roe on dark slate with wasabi and pickled ginger",
            "text_story": "классическая Филадельфия с толстым слоем охлажденного лосося, нежным творожным сыром и идеально сваренным рисом"
        },
        "суши": {
            "en_term": "artisan nigiri sushi assortment on ceramic plate",
            "visual_description": "freshly prepared artisan nigiri sushi featuring glistening salmon and tuna cuts over seasoned vinegared rice, brush-applied soy glaze and freshly grated real wasabi",
            "text_story": "аутентичные суши и нигири из свежайшей рыбы: чистый вкус моря и вековые традиции японской кухни"
        },

        # =========================================================================
        # 4. БЬЮТИ, КОСМЕТИКА, КРЕМЫ И ПОМАДЫ
        # =========================================================================
        "крем": {
            "en_term": "luxury hydrating skincare cream in heavy frosted glass jar",
            "visual_description": "luxurious heavy frosted glass skincare jar with a polished champagne-gold metallic screw cap, rich whipped velvety white cream texture slightly swirling inside, fresh glistening micro-droplets of water on the cool glass, displayed on a minimalist travertine stone podium",
            "text_story": "насыщенный увлажняющий крем с шелковистой тающей текстурой, натуральными пептидами и гиалуроновой кислотой для глубокого восстановления и сияния кожи"
        },
        "сыворотк": {
            "en_term": "luxury botanical facial serum in glass dropper bottle",
            "visual_description": "amber glass apothecary serum bottle with a delicate glass dropper dispensing a single crystal-clear luminous serum droplet, soft diffused lighting, resting on a smooth natural river stone with delicate water ripples",
            "text_story": "концентрированная сыворотка с легкой формулой: мгновенное проникновение в глубокие слои кожи, выравнивание тона и мощный антиоксидантный эффект"
        },
        "помад": {
            "en_term": "ultra-luxury satin lipstick in fluted gold magnetic case",
            "visual_description": "ultra-luxury satin lipstick in a heavy magnetic fluted gold case with a pristine sharp diagonal bullet tip, rich velvety pigmented texture with subtle dewy moisture sheen, accompanied by an artistic smooth pigment swatch on textured slate stone",
            "text_story": "роскошная помада с сатиновым финишем: насыщенный стойкий пигмент, бархатное скольжение и ухаживающие растительные масла в составе"
        },
        "блеск для губ": {
            "en_term": "high-shine plumping lip gloss / lip oil",
            "visual_description": "crystal-clear luxury lip oil tube with thick acrylic walls, plush doe-foot applicator pulled out glistening with luminous reflective pink-peach glaze and micro-shimmer",
            "text_story": "масло-блеск с зеркальным глянцевым эффектом: визуальный объем, комфортное увлажнение и нежный полупрозрачный оттенок без ощущения липкости"
        },
        "массаж": {
            "en_term": "basalt hot stones SPA therapy",
            "visual_description": "smooth polished volcanic black basalt massage stones glistening with aromatic botanical essential oils placed along spine",
            "text_story": "прогретые базальтовые камни вулканического происхождения, глубоко прогревающие мышцы и снимающие стресс"
        },

        # =========================================================================
        # 5. СТРОИТЕЛЬНЫЙ ИНСТРУМЕНТ И РЕМОНТ
        # =========================================================================
        "шуруповерт": {
            "en_term": "heavy-duty cordless brushless drill driver",
            "visual_description": "high-end 20V brushless cordless drill driver with knurled metal keyless chuck, ergonomic dual-injection rubberized grip, high-capacity slide-in lithium-ion battery with bright LED fuel gauge, crisp metallic torque selector ring, placed on rustic workshop wood with delicate cedar shavings",
            "text_story": "мощный бесщеточный шуруповерт с высоким крутящим моментом, металлическим быстрозажимным патроном и емким аккумулятором для точной работы без перегрева"
        },
        "дрель": {
            "en_term": "heavy-duty cordless brushless drill driver",
            "visual_description": "high-end 20V brushless cordless drill driver with knurled metal keyless chuck, ergonomic dual-injection rubberized grip, high-capacity slide-in lithium-ion battery with bright LED fuel gauge, crisp metallic torque selector ring, placed on rustic workshop wood with delicate cedar shavings",
            "text_story": "мощный бесщеточный шуруповерт с высоким крутящим моментом, металлическим быстрозажимным патроном и емким аккумулятором для точной работы без перегрева"
        },
        "перфоратор": {
            "en_term": "professional SDS-Plus rotary hammer drill",
            "visual_description": "rugged professional SDS-Plus rotary hammer drill with heavy-duty cast aluminum gear housing, anti-vibration rubberized rear handle, precision steel depth gauge, durable textured composite body with dust-sealed ventilation ports",
            "text_story": "профессиональный перфоратор с патроном SDS-Plus, надежным пневматическим ударным механизмом и эффективной системой гашения вибрации для бурения твердого бетона"
        },
        "лазерный уровень": {
            "en_term": "360-degree self-leveling green beam laser level",
            "visual_description": "compact rugged 360-degree 3D self-leveling green beam laser level with impact-resistant rubber overmolded housing, glowing crisp emerald laser projection windows, mounted on a sleek aluminum micro-adjust tripod in a sunlit renovation space",
            "text_story": "самовыравнивающийся лазерный уровень с ярким зеленым лучом 360°: безупречная видимость разметки даже при ярком свете и точность до миллиметра"
        },
        "болгарк": {
            "en_term": "heavy-duty cordless angle grinder",
            "visual_description": "heavy-duty brushless angle grinder with quick-lock wheel nut, precision spark guard, textured slim ergonomic body and brushed metal gearbox housing, placed on a dark steel workbench",
            "text_story": "производительная углошлифовальная машина с плавным пуском, защитой от заклинивания диска и эргономичным хватом для уверенного реза металла и камня"
        },

        # =========================================================================
        # 6. ЮВЕЛИРНЫЕ ИЗДЕЛИЯ И ЧАСЫ
        # =========================================================================
        "кольцо": {
            "en_term": "platinum solitaire diamond engagement ring",
            "visual_description": "exquisite platinum engagement ring featuring a flawless round brilliant-cut center diamond in a four-prong setting, fiery rainbow light refractions, pavé-set micro-diamonds along the band, resting on dark midnight velvet",
            "text_story": "помолвочное кольцо из платины с бриллиантом безупречной огранки: завораживающая игра граней и непреходящий символ искренних чувств"
        },
        "часы": {
            "en_term": "luxury Swiss automatic mechanical chronograph watch",
            "visual_description": "luxury Swiss mechanical chronograph watch with polished stainless steel case, anti-reflective sapphire crystal, intricate guilloché textured sunburst dial, blued steel hands, exposed automatic movement balance wheel, genuine alligator leather strap",
            "text_story": "механический хронограф со швейцарским калибром и сапфировым стеклом: статус, выверенная точность хода и классический часовой дизайн"
        },

        # =========================================================================
        # 7. ФЛОРИСТИКА И БУКЕТЫ
        # =========================================================================
        "букет": {
            "en_term": "luxurious designer floral bouquet",
            "visual_description": "lush designer floral bouquet of soft pink Sarah Bernhardt peonies, creamy French garden roses, ruffled white ranunculus and dusty silver dollar eucalyptus, wrapped in textured matte kraft paper with silk trailing ribbons, glistening morning mist drops",
            "text_story": "авторский букет из пионов Сара Бернар, французских роз и эвкалипта: нежная палитра, пьянящий аромат и безупречная стойкость"
        },
        "пион": {
            "en_term": "freshly bloomed Sarah Bernhardt peonies bouquet",
            "visual_description": "freshly bloomed lush Sarah Bernhardt peonies with delicate layered tissue-thin petals, soft dewy pastel glow in natural morning light",
            "text_story": "пышные пионы с тонким цветочным ароматом и воздушными лепестками: идеальный подарок для особенного настроения"
        },

        # =========================================================================
        # 8. АВТОСПОРТ, ТЮНИНГ И ДЕТЕЙЛИНГ
        # =========================================================================
        "gt2871": {
            "en_term": "compact Garrett GT2871R ball bearing automotive turbocharger",
            "visual_description": "compact handheld automotive turbocharger (Garrett GT2871R, 20 cm tabletop size, small lightweight part easily held in two hands), resting neatly on a garage workbench, precision silver cast aluminum radial compressor volute housing, compact 70mm circular front air intake with gleaming CNC-machined curved aluminum impeller blades and center lock nut, 90-degree charge pipe outlet, compact cylindrical wastegate actuator with black hose, realistic accurate real-world scale and proportions, tabletop commercial automotive product photography",
            "text_story": "культовая производительная турбина GT2871 для моторов SR20-DET: быстрый спул на фланце T25, стабильный наддув и честная отдача для Nissan Silvia S13/S14/S15"
        },
        "турбин": {
            "en_term": "compact automotive turbocharger",
            "visual_description": "compact handheld car turbocharger assembly (20 cm tabletop scale, realistic small component), cast aluminum radial compressor volute housing, circular front intake with sharp curved impeller blades, compact side wastegate actuator, accurate real-world proportions, tabletop automotive product photography",
            "text_story": "профессиональная система турбонаддува: мгновенный отклик на педаль газа и запас прочности при экстремальных нагрузках"
        },
        "sr20": {
            "en_term": "Nissan Silvia SR20-DET turbo engine",
            "visual_description": "high-performance Nissan SR20-DET red top turbocharged engine bay in a clean Silvia S13/S14 chassis, polished aluminum intake manifold, customized tubular turbo manifold with T25 flange, silicone coupler hoses, raw mechanical JDM beauty",
            "text_story": "легендарный японский турбомотор SR20-DET: идеальный баланс массы, прочности блока и потенциала для дрифта и кольца"
        },
        "детейлинг": {
            "en_term": "flawless hydrophobic 9H ceramic coating car detailing",
            "visual_description": "glossy mirror-finish car hood coated in 9H hydrophobic ceramic protection under workshop halo LED inspection lights, deep wet reflections, rolling spherical water beading droplets",
            "text_story": "многоэтапная полировка кузова и нанесение нанокерамики 9H: глубокий зеркальный глянец, защита от сколов и мощный гидрофобный эффект"
        },

        # =========================================================================
        # 9. ЭЛЕКТРОНИКА, МИКРОКОНТРОЛЛЕРЫ И IOT
        # =========================================================================
        "esp-32": {
            "en_term": "ESP32 30-pin Type-C NodeMCU development board",
            "visual_description": "narrow vertical rectangular (52mm x 28mm) matte black FR-4 PCB microcontroller board, strictly dual-in-line DIP-30 layout with exactly two straight parallel rows of 15 gold-plated header pins along the long left and right side edges only (15 pins left + 15 pins right = 30 pins total, strictly NO pins on top or bottom edges), silver metallic rectangular shielded RF module at the upper half with laser-etched 'ESP-32' logo and serpentine WiFi antenna, modern USB Type-C port centered at the bottom edge flanked by two tiny black tactile buttons labeled EN and BOOT, CP2102 chip, clean copper circuit traces, extreme macro tabletop photography",
            "text_story": "компактная 30-пиновая отладочная плата ESP-32 с удобным разъемом Type-C: двухъядерный процессор Xtensa LX6, встроенный Wi-Fi и Bluetooth BLE для умных устройств и IoT-автоматизации"
        },
        "esp32": {
            "en_term": "ESP32 30-pin Type-C NodeMCU development board",
            "visual_description": "narrow vertical rectangular (52mm x 28mm) matte black FR-4 PCB microcontroller board, strictly dual-in-line DIP-30 layout with exactly two straight parallel rows of 15 gold-plated header pins along the long left and right side edges only (15 pins left + 15 pins right = 30 pins total, strictly NO pins on top or bottom edges), silver metallic rectangular shielded RF module at the upper half with laser-etched 'ESP-32' logo and serpentine WiFi antenna, modern USB Type-C port centered at the bottom edge flanked by two tiny black tactile buttons labeled EN and BOOT, CP2102 chip, clean copper circuit traces, extreme macro tabletop photography",
            "text_story": "компактная 30-пиновая отладочная плата ESP-32 с удобным разъемом Type-C: двухъядерный процессор Xtensa LX6, встроенный Wi-Fi и Bluetooth BLE для умных устройств и IoT-автоматизации"
        },
        "arduino uno": {
            "en_term": "Arduino Uno R3 development board",
            "visual_description": "authentic Arduino UNO R3 microcontroller board with classic vibrant royal blue matte PCB, gold-plated female header sockets, socketed ATmega328P DIP microchip, 16MHz silver crystal oscillator, standard USB port, red reset button, crisp white silkscreen pin labels, macro electronics workbench photography",
            "text_story": "классическая отладочная плата Arduino UNO R3 на микроконтроллере ATmega328P: надежный стандарт для быстрого прототипирования и обучения робототехнике"
        },
        "ардуино": {
            "en_term": "Arduino Uno R3 development board",
            "visual_description": "authentic Arduino UNO R3 microcontroller board with classic vibrant royal blue matte PCB, gold-plated female header sockets, socketed ATmega328P DIP microchip, 16MHz silver crystal oscillator, standard USB port, red reset button, crisp white silkscreen pin labels, macro electronics workbench photography",
            "text_story": "классическая отладочная плата Arduino UNO R3 на микроконтроллере ATmega328P: надежный стандарт для быстрого прототипирования и обучения робототехнике"
        },

        # =========================================================================
        # 10. КОМПЬЮТЕРЫ И НОУТБУКИ С УНИКАЛЬНОЙ АРХИТЕКТУРОЙ (LAPTOP SIGNATURES)
        # =========================================================================
        "gx701": {
            "en_term": "ASUS ROG Zephyrus S GX701 gaming laptop",
            "visual_description": "ASUS ROG Zephyrus S GX701 ultra-slim 17-inch gaming laptop, signature forward-positioned RGB per-key keyboard shifted to the front edge, vertical side-mounted touchpad on the right doubling as an illuminated digital number pad, large stylish perforated brushed magnesium intake plate above the keyboard with luminous ROG eye logo, Active Aerodynamic System (AAS) bottom chassis vent visibly lifted 5mm at the rear for cooling, ultra-thin screen bezels, premium matte black metal body with copper diamond-cut chamfered edges",
            "text_story": "флагманский 17-дюймовый ультрабук ASUS ROG Zephyrus GX701: уникальная компоновка с клавиатурой у переднего края, цифровым тачпадом сбоку и активной системой охлаждения AAS с приподнимающимся днищем"
        },
        "zephyrus": {
            "en_term": "ASUS ROG Zephyrus gaming laptop",
            "visual_description": "ASUS ROG Zephyrus ultra-slim gaming laptop with CNC AniMe Matrix LED lid, forward-shifted ergonomic keyboard, side-mounted precision touchpad with numpad mode, active aerodynamic intake vents, premium dark magnesium-aluminum chassis",
            "text_story": "ультратонкий игровой флагман ASUS ROG Zephyrus с продуманным охлаждением, матричным дисплеем на крышке и эргономичной раскладкой"
        },
        "zenbook duo": {
            "en_term": "ASUS ZenBook Duo dual-screen laptop",
            "visual_description": "ASUS ZenBook Duo revolutionary dual-screen laptop with primary OLED display and secondary tilted matte touchscreen (ScreenPad Plus) spanning the upper half of the base deck above the keyboard, keyboard shifted to the front edge with vertical numeric trackpad, spun-metal celestial blue chassis",
            "text_story": "революционный двухэкранный ноутбук ASUS ZenBook Duo: дополнительный сенсорный экран ScreenPad Plus над клавиатурой для максимальной продуктивности"
        },
        "asus duo": {
            "en_term": "ASUS ZenBook Duo dual-screen laptop",
            "visual_description": "ASUS ZenBook Duo revolutionary dual-screen laptop with primary OLED display and secondary tilted matte touchscreen (ScreenPad Plus) spanning the upper half of the base deck above the keyboard, keyboard shifted to the front edge with vertical numeric trackpad, spun-metal celestial blue chassis",
            "text_story": "революционный двухэкранный ноутбук ASUS ZenBook Duo: дополнительный сенсорный экран ScreenPad Plus над клавиатурой для максимальной продуктивности"
        },
        "thinkpad": {
            "en_term": "Lenovo ThinkPad X1 laptop",
            "visual_description": "iconic Lenovo ThinkPad X1 business laptop in matte raven-black soft-touch carbon fiber chassis, iconic bright red TrackPoint rubber nub centered between G-H-B keys, physical mouse click buttons with red accent line above trackpad, glowing red LED dot on the ThinkPad logo at palm rest, dual stainless steel 180-degree hinges",
            "text_story": "легендарный бизнес-ноутбук ThinkPad: матовый прочный корпус из углеволокна, фирменный красный трекпоинт и эргономичная клавиатура с защитой от влаги"
        },
        "macbook": {
            "en_term": "Apple MacBook Pro Space Black laptop",
            "visual_description": "Apple MacBook Pro laptop in unibody anodized Space Black CNC aluminum, centered giant glass Force Touch trackpad, black anodized keyboard well with full-height function keys and Touch ID, slim braided MagSafe 3 cable connected, edge-to-edge Liquid Retina XDR display with rounded top corners and centered camera notch",
            "text_story": "культовый Apple MacBook Pro в цельнометаллическом корпусе Space Black: дисплей Liquid Retina XDR, трекпад Force Touch и процессор Apple Silicon для максимальной автономности"
        },

        # =========================================================================
        # 10. FASHION, ПЛЯЖ И ПРИВАТ
        # =========================================================================
        "микробикини": {
            "en_term": "micro-bikini",
            "visual_description": "exquisite minimalist micro-bikini swimwear crafted from shimmering spandex with ultra-thin elastic string ties, tiny triangular fabric coverage designed for maximum tan lines, delicate stitching and authentic fabric stretch",
            "text_story": "ультра-минималистичный крой для идеального загара, тонкие завязки и премиальный металлизированный эластан"
        },
        "стринги": {
            "en_term": "extreme thong swimsuit / string thong",
            "visual_description": "ultra-minimalist high-cut Brazilian thong swimwear with delicate side ties, smooth seamless fabric edges and elegant silhouette",
            "text_story": "высокий вырез, подчеркивающий силуэт, и безупречная посадка из бесшовных премиальных материалов"
        },
        "купальник для загара": {
            "en_term": "tanning swimsuit / minimalist bandeau bikini",
            "visual_description": "minimalist tanning bikini with strapless bandeau top and ultra-low coverage bottoms designed to minimize tan lines, high-grade quick-dry matte lycra",
            "text_story": "модель бандо без бретелей для ровного бронзового загара из быстросохнущей матовой лайкры"
        },
        "кимоно": {
            "en_term": "Mulberry silk kimono robe",
            "visual_description": "flowing luxurious Mulberry silk kimono robe with smooth lustrous sheen, elegant wide sleeves and delicate golden embroidery accents",
            "text_story": "струящийся натуральный шелк малбери, изысканный блеск и свободный силуэт для моментов домашней роскоши"
        },
        "корсет": {
            "en_term": "structured Victorian boned corset",
            "visual_description": "tailored satin corset with structured vertical boning channels, delicate lace trim and satin back ribbon lacing",
            "text_story": "скульптурирующий силуэт на гибких косточках с атласной шнуровкой и нежным кружевом"
        }
    }

    @classmethod
    async def research_visual_spec(cls, topic: str) -> Dict[str, str]:
        """
        Ищет точную визуальную специфику для любого объекта, SKU, инструмента, блюда или услуги.
        Сначала проверяет локальную экспертную базу (по наибольшему совпадению), при необходимости делает фоновый запрос к поисковику.
        """
        if not topic:
            return {}

        topic_lower = topic.lower()

        # 1. Проверяем локальную экспертную базу по наибольшей специфичности (длинные ключи первыми)
        sorted_specs = sorted(cls.CURATED_VISUAL_SPECS.items(), key=lambda x: len(x[0]), reverse=True)
        for key, spec in sorted_specs:
            if key in topic_lower:
                logger.info(f"[VisualKnowledgeResearcher] 🎯 Найдена точная спецификация для «{key}»")
                return spec

        # 2. Если сложный технический термин / SKU не найден — выполняем параллельный веб-поиск через Tavily
        try:
            tavily_key = os.getenv("TRAVITY_API_KEY") or os.getenv("TAVILY_API_KEY")
            if tavily_key and httpx is not None:
                async with httpx.AsyncClient(timeout=6.0) as client:
                    resp = await client.post(
                        "https://api.tavily.com/search",
                        json={
                            "api_key": tavily_key,
                            "query": f"what is {topic} visual components physical appearance materials design layout",
                            "max_results": 2
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        results = data.get("results", [])
                        if results:
                            snippet = results[0].get("content", "")[:250]
                            clean_snippet = re.sub(r'[\r\n\t]+', ' ', snippet).strip()
                            return {
                                "en_term": topic,
                                "visual_description": f"authentic precision representation of {topic}, featuring {clean_snippet}",
                                "text_story": f"высокая надежность, выверенная эргономика и внимание к деталям: {topic}"
                            }
        except Exception as ex:
            logger.debug(f"[VisualKnowledgeResearcher] Web search fallback: {ex}")

        # Fallback по умолчанию
        return {
            "en_term": topic,
            "visual_description": f"authentic professional representation of {topic} with accurate physical textures, materials and real-world proportions",
            "text_story": topic
        }

    @classmethod
    def research_visual_spec_sync(cls, topic: str) -> Dict[str, str]:
        """
        Синхронная обертка для быстрого вызова из генераторов промптов.
        """
        topic_lower = topic.lower()
        sorted_specs = sorted(cls.CURATED_VISUAL_SPECS.items(), key=lambda x: len(x[0]), reverse=True)
        for key, spec in sorted_specs:
            if key in topic_lower:
                return spec
                
        # Если есть Tavily API ключ, пробуем выполнить поиск
        try:
            tavily_key = os.getenv("TRAVITY_API_KEY") or os.getenv("TAVILY_API_KEY")
            if tavily_key and httpx is not None:
                with httpx.Client(timeout=4.0) as client:
                    resp = client.post(
                        "https://api.tavily.com/search",
                        json={
                            "api_key": tavily_key,
                            "query": f"what is {topic} components visual appearance materials layout",
                            "max_results": 1
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        results = data.get("results", [])
                        if results:
                            snippet = results[0].get("content", "")[:200]
                            clean_snippet = re.sub(r'[\r\n\t]+', ' ', snippet).strip()
                            return {
                                "en_term": topic,
                                "visual_description": f"authentic representation of {topic}, {clean_snippet}",
                                "text_story": f"надежность и профессиональное исполнение: {topic}"
                            }
        except Exception:
            pass

        return {
            "en_term": topic,
            "visual_description": f"authentic commercial representation of {topic} with crisp physical textures",
            "text_story": topic
        }
