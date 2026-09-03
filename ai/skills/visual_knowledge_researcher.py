# File: ai/skills/visual_knowledge_researcher.py
"""
VisualKnowledgeResearcher — Универсальный мульти-доменный модуль параллельного поиска
и визуальной спецификации объектов (автобизнес/тюнинг, электроника/микроконтроллеры,
fashion/белье, гастрономия, инженерия) для сверхточного промпт-инжиниринга в ComfyUI.
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
    автокомпонентов, одежды и сложных товаров.
    Переводит инженерные аббревиатуры и SKU в фотореалистичные физические дескрипторы для ComfyUI.
    """

    # Предустановленная верифицированная база точных спецификаций сложных объектов
    CURATED_VISUAL_SPECS: Dict[str, Dict[str, str]] = {
        # =========================================================================
        # 1. АВТОСПОРТ, ТЮНИНГ, ТУРБОНАДДУВ И JDM
        # =========================================================================
        "gt2871": {
            "en_term": "Garrett GT2871R turbocharger",
            "visual_description": "precision-engineered GT2871 turbocharger with CNC-machined billet aluminum compressor wheel, cast nickel-alloy turbine housing with T25 5-bolt exhaust flange, polished internal wastegate actuator, braided stainless steel AN oil feed lines, raw machined metal luster, precision automotive photography",
            "text_story": "культовая производительная турбина GT2871 для моторов SR20-DET: быстрый спул на фланце T25, стабильный наддув и честная отдача для Nissan Silvia S13/S14/S15"
        },
        "sr20": {
            "en_term": "Nissan Silvia SR20-DET turbo engine",
            "visual_description": "high-performance Nissan SR20-DET red top turbocharged engine bay in a clean Silvia S13/S14 chassis, polished aluminum intake manifold, customized tubular turbo manifold with T25 flange, silicone coupler hoses, raw mechanical JDM beauty",
            "text_story": "легендарный японский турбомотор SR20-DET: идеальный баланс массы, прочности блока и потенциала для дрифта и кольца"
        },
        "турбин": {
            "en_term": "high-performance turbocharger",
            "visual_description": "precision motorsport turbocharger with polished compressor housing, precision curved impeller blades, heavy-duty cast exhaust housing with manifold studs, braided fluid lines",
            "text_story": "профессиональная система турбонаддува: мгновенный отклик на педаль газа и запас прочности при экстремальных нагрузках"
        },
        "койловер": {
            "en_term": "adjustable motorsport coilover suspension",
            "visual_description": "pair of anodized adjustable racing coilovers with stiff brightly colored springs, threaded damper body with height-locking rings, pillowball top mounts",
            "text_story": "регулируемая винтовая подвеска: точная настройка клиренса, жесткости и угла схода-развала для идеального зацепа"
        },

        # =========================================================================
        # 2. ЭЛЕКТРОНИКА, МИКРОКОНТРОЛЛЕРЫ И IOT
        # =========================================================================
        "esp-32": {
            "en_term": "ESP32 30-pin Type-C development board",
            "visual_description": "compact 30-pin ESP32 NodeMCU development board with matte black PCB substrate, modern USB Type-C port, ESP-WROOM-32 shielded metal RF module, two parallel rows of gold-plated 15-pin headers (30 pins total), dual tactile EN/BOOT buttons, CP2102 chip, copper circuit traces, extreme macro photography",
            "text_story": "компактная 30-пиновая отладочная плата ESP-32 с удобным разъемом Type-C: двухъядерный процессор Xtensa LX6, встроенный Wi-Fi и Bluetooth BLE для умных устройств и IoT-автоматизации"
        },
        "esp32": {
            "en_term": "ESP32 30-pin Type-C development board",
            "visual_description": "compact 30-pin ESP32 NodeMCU development board with matte black PCB substrate, modern USB Type-C port, ESP-WROOM-32 shielded metal RF module, two parallel rows of gold-plated 15-pin headers (30 pins total), dual tactile EN/BOOT buttons, CP2102 chip, copper circuit traces, extreme macro photography",
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
        "raspberry pi": {
            "en_term": "Raspberry Pi single-board computer",
            "visual_description": "Raspberry Pi single-board computer with rich green PCB, silver Broadcom SoC processor with thermal paste pad, 40-pin GPIO header, micro-HDMI ports, USB 3.0 ports, Ethernet jack and USB-C power port",
            "text_story": "полноценный одноплатный микрокомпьютер Raspberry Pi: высокая производительность в компактном форм-факторе для медиацентров, серверов и edge-ИИ"
        },

        # =========================================================================
        # 3. FASHION, ПЛЯЖ И ПРИВАТ
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
        },

        # =========================================================================
        # 4. КУЛИНАРИЯ, ДЕСЕРТЫ И РЕСТОРАНЫ
        # =========================================================================
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
        "горячие камни": {
            "en_term": "basalt hot stones SPA therapy",
            "visual_description": "smooth polished volcanic black basalt massage stones glistening with aromatic botanical essential oils placed along spine",
            "text_story": "прогретые базальтовые камни вулканического происхождения, глубоко прогревающие мышцы и снимающие стресс"
        }
    }

    @classmethod
    async def research_visual_spec(cls, topic: str) -> Dict[str, str]:
        """
        Ищет точную визуальную специфику для любого объекта, SKU, компонента или одежды.
        Сначала проверяет локальную базу, при необходимости делает запрос к поисковику.
        """
        if not topic:
            return {}

        topic_lower = topic.lower()

        # 1. Проверяем локальную экспертную базу
        for key, spec in cls.CURATED_VISUAL_SPECS.items():
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
                            "query": f"what is {topic} visual components physical appearance materials design",
                            "max_results": 2
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        results = data.get("results", [])
                        if results:
                            snippet = results[0].get("content", "")[:250]
                            # Очищаем сниппет от лишних спецсимволов
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
        for key, spec in cls.CURATED_VISUAL_SPECS.items():
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
                            "query": f"what is {topic} components visual appearance materials",
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
            "visual_description": f"authentic commercial representation of {topic} with crisp engineering textures",
            "text_story": topic
        }
