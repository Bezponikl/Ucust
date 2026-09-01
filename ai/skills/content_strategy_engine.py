# File: skills/content_strategy_engine.py
"""
Content Strategy & User Persona Engine for UCust.AI.
Generates full-funnel marketing strategies (TOFU/MOFU/BOFU), hook libraries, and deep buyer personas.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional

class ContentStrategyEngine:
    def __init__(self):
        pass

    def generate_strategy(self, company_name: str, niche: str, target_audience: str = "", key_usp: str = "") -> Dict[str, Any]:
        buyer_persona = {
            "core_demographics": target_audience or "Предприниматели, руководители и B2B/B2C клиенты 25-50 лет",
            "jobs_to_be_done": [
                "Сэкономить время и деньги на рутинных задачах",
                "Получить предсказуемый и надежный результат без срывов сроков",
                "Быстро масштабировать продажи или бизнес-процессы"
            ],
            "primary_pains": [
                "Высокие цены при непонятном качестве услуг",
                "Срыв дедлайнов и отсутствие гарантий",
                "Сложные громоздкие решения, в которых трудно разобраться"
            ],
            "buying_triggers": [
                "Наглядные кейсы с измеримыми цифрами (было / стало)",
                "Бесплатный тест / демо / консультация без обязательств",
                "Прозрачная фиксированная цена и гарантия возврата"
            ]
        }

        funnel_matrix = {
            "tofu_awareness": {
                "goal": "Привлечение широкого охвата и новой аудитории",
                "formats": ["Вирусные Shorts/Reels", "Инфографика", "Посты-разборы ошибок"],
                "topics": [
                    f"«5 фатальных ошибок в сфере {niche}, которые сжигают бюджет»",
                    f"«Как устроена внутренняя кухня в {company_name}: закулисье работы»"
                ]
            },
            "mofu_consideration": {
                "goal": "Прогрев доверия, снятие возражений и демонстрация экспертности",
                "formats": ["Кейсы клиентов", "Сравнения до/после", "Пошаговые гайды"],
                "topics": [
                    f"«Реальный кейс {company_name}: как мы решили сложную задачу клиента за 3 дня»",
                    "«Почему дешевые альтернативы выходят в 3 раза дороже (честный расчет)»"
                ]
            },
            "bofu_conversion": {
                "goal": "Прямые продажи и закрытие на заявку / покупку",
                "formats": ["Спецпредложения", "Ограниченные акции", "Демонстрация продукта в действии"],
                "topics": [
                    f"«Специальное предложение от {company_name}: получите аудит бесплатно»",
                    "«Осталось 3 свободных слота на этой неделе: напишите в директ для брони»"
                ]
            }
        }

        hooks_arsenal = [
            f"«Если вы работаете в {niche}, перестаньте делать это немедленно...»",
            f"«3 вещи, которые клиенты {company_name} узнают на 1-й день работы»",
            "«Секрет, который скрывают 90% экспертов на рынке...»",
            f"«Как получить максимум пользы от {company_name} уже сегодня: инструкция»"
        ]

        return {
            "status": "success",
            "company_name": company_name,
            "niche": niche,
            "buyer_persona": buyer_persona,
            "funnel_matrix": funnel_matrix,
            "hooks_arsenal": hooks_arsenal,
            "summary_plan": f"Стратегия для {company_name} ({niche}): 3 уровня воронки (TOFU/MOFU/BOFU) + 4 виральных хука."
        }

    def generate_content_plan(
        self,
        company_name: str,
        niche: str,
        visual_grid_dna: Optional[Dict[str, Any]] = None,
        rag_insights: Optional[Dict[str, Any]] = None,
        days_count: int = 7,
        country: str = "Россия",
        city: str = "Москва",
        start_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Генерирует контент-план на N дней, привязанный к болям аудитории из RAG,
        сопоставленный со слотами 3x3 визуальной сетки ленты и обогащенный
        государственными, профессиональными и городскими праздниками.
        """
        from collectors.event_holiday_collector import EventHolidayCollector

        grid_slots = (visual_grid_dna or {}).get("grid_3x3_slots", [])
        brand_colors = (visual_grid_dna or {}).get("brand_hex_palette", ["#1F2937", "#3B82F6", "#F3F4F6"])
        pains = (rag_insights or {}).get("pain_points", [
            "Страх некачественного результата",
            "Высокие цены и скрытые переплаты",
            "Нехватка времени и сложный процесс"
        ])
        competitor_adv = (rag_insights or {}).get("competitor_advantages", "Гарантия результата, прозрачный прайс и быстрое обслуживание")

        # 1. Поиск праздников и инфоповодов на заданный период
        holiday_collector = EventHolidayCollector()
        events_list = holiday_collector.get_calendar_events(
            country=country,
            city=city,
            niche=niche,
            start_date=start_date,
            days_count=days_count
        )
        # Словарь событий по номеру дня (1..days_count)
        events_by_day = {e["day_number"]: e for e in events_list}

        stages = ["TOFU", "MOFU", "BOFU", "TOFU", "MOFU", "BOFU", "MOFU"]
        plan_items = []

        for day in range(1, days_count + 1):
            slot_idx = (day - 1) % (len(grid_slots) if grid_slots else 9)
            slot_info = grid_slots[slot_idx] if grid_slots and slot_idx < len(grid_slots) else {
                "slot": slot_idx + 1,
                "type": "lifestyle",
                "title": "Брендовый кадр",
                "description": "Эстетичный кадр с фирменными цветами"
            }
            pain = pains[(day - 1) % len(pains)]

            # Проверка, выпадает ли на этот день праздник
            holiday_event = events_by_day.get(day)

            if holiday_event:
                stage = "BOFU" if "подарок" in holiday_event["vibe"].lower() or "скидк" in holiday_event["vibe"].lower() else "TOFU"
                h_title = holiday_event["title"]
                topic = f"🎉 [Праздник: {h_title}] Поздравление от «{company_name}» и праздничный комплимент клиентам"
                format_type = "Праздничный ситуативный пост + Поздравление + Промокод"
                target_pain = f"Праздничное настроение и забота о клиентах: {h_title} ({holiday_event['vibe']})"
            else:
                stage = stages[(day - 1) % len(stages)]
                if stage == "TOFU":
                    topic = f"Как избежать главной ошибки в {niche}: секреты профессионалов"
                    format_type = "Пост-разбор + Вопрос в комментариях"
                elif stage == "MOFU":
                    topic = f"Честно о том, как мы закрываем проблему «{pain}» в {company_name}"
                    format_type = "Кейс До/После + Демонстрация процесса"
                else: # BOFU
                    topic = f"Специальное предложение от «{company_name}»: гарантия качества и выгода"
                    format_type = "Продающий оффер + Промокод + CTA"
                target_pain = pain

            plan_items.append({
                "day": day,
                "stage": stage,
                "topic": topic,
                "target_pain_point": target_pain,
                "format": format_type,
                "is_holiday": bool(holiday_event),
                "holiday_info": holiday_event,
                "grid_slot": {
                    "slot_number": slot_info.get("slot", slot_idx + 1),
                    "shot_type": slot_info.get("type"),
                    "visual_title": slot_info.get("title"),
                    "visual_guidance": f"Съемка в стиле '{slot_info.get('title')}'. Палитра: {', '.join(brand_colors[:2])}."
                }
            })

        return {
            "status": "success",
            "company_name": company_name,
            "niche": niche,
            "country": country,
            "city": city,
            "total_days": days_count,
            "holidays_included_count": len(events_by_day),
            "plan_days": plan_items,
            "brand_palette": brand_colors,
            "summary": f"Контент-план на {days_count} дней успешно сбалансирован: внедрено {len(events_by_day)} праздничных инфоповодов для г. {city} ({country})."
        }
