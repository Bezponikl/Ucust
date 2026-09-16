"""
Internal Calendar and Temporal Grounding Engine for UCust.AI.
"""
from __future__ import annotations
import os
import re
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
try:
    from collectors.event_holiday_collector import EventHolidayCollector
except ImportError:
    try:
        from ai.collectors.event_holiday_collector import EventHolidayCollector
    except ImportError:
        EventHolidayCollector = None

class InternalCalendarEngine:
    _instance: Optional[InternalCalendarEngine] = None

    DAY_PSYCHOLOGY = {
        0: {"name": "Понедельник", "vibe": "Фокус на целях, планирование недели, старт новых процессов, собранность"},
        1: {"name": "Вторник", "vibe": "Максимальная концентрация, разбор сложных задач и экспертные темы"},
        2: {"name": "Среда", "vibe": "Экватор недели, преодоление рутины, оптимизация, инструменты и автоматизация"},
        3: {"name": "Четверг", "vibe": "Практические результаты, кейсы, подготовка решений и сильных офферов"},
        4: {"name": "Пятница", "vibe": "Итоги недели, легкий тон, предвкушение выходных, специальные предложения и разгрузка"},
        5: {"name": "Суббота", "vibe": "Лайфстайл, отдых, семья, вдохновение, неформальное теплое общение"},
        6: {"name": "Воскресенье", "vibe": "Перезагрузка, мысли о будущем, спокойные размышления и подготовка к старту"}
    }

    SEASONS = {
        (3, 4, 5): {
            "season": "Весна",
            "lighting_mod": "fresh bright spring daylight with gentle floral warmth",
            "palette": "fresh emerald, warm ivory, soft floral tones",
            "narrative_focus": "обновление, свежий старт, весенний рост и пробуждение"
        },
        (6, 7, 8): {
            "season": "Лето",
            "lighting_mod": "vibrant warm summer daylight with crisp defined shadows",
            "palette": "golden sunlight, rich warm neutrals, vibrant accents",
            "narrative_focus": "высокий сезон, динамика, энергия, скорость и активность"
        },
        (9, 10, 11): {
            "season": "Осень",
            "lighting_mod": "subtle golden hour autumn daylight casting gentle organic room shadows",
            "palette": "amber, warm cognac, terracotta, cozy beige, dark walnut",
            "narrative_focus": "деловой сезон, сбор урожая результатов, масштабирование, уют и надежность"
        },
        (12, 1, 2): {
            "season": "Зима",
            "lighting_mod": "soft diffused winter window daylight with warm 3000K interior accent",
            "palette": "deep navy, graphite, warm amber light, cream wool",
            "narrative_focus": "итоги года, новогодние цели, надежность в холода, забота и тепло"
        }
    }

    TIME_OF_DAY_SLOTS = [
        (range(6, 11), {
            "phase": "Утро",
            "code": "morning",
            "vibe": "Утренний фокус, заряд энергии, чашка кофе, бодрость, старт рабочего дня раньше всех",
            "caring_subtext": "Мы уже на месте с первой чашкой кофе, всё настроили и готовы решать ваши задачи с самого утра.",
            "window_lighting": "gentle morning window daylight with soft angled sunbeams, subtle translucent coffee vapor, fresh crisp shadows",
            "indoor_lighting": "crisp focused morning task lighting with soft ambient room falloff, steaming ceramic mug, fresh energetic studio ambiance"
        }),
        (range(11, 17), {
            "phase": "День",
            "code": "afternoon",
            "vibe": "Деловая активность, решение задач, разбор процессов, высокая продуктивность и скорость",
            "caring_subtext": "В самом разгаре рабочего дня — держим руку на пульсе ваших проектов и процессов.",
            "window_lighting": "crisp clean neutral 5000K daylight from windows, balanced realistic micro-shadows, productive atmosphere",
            "indoor_lighting": "balanced neutral task illumination with clean micro-shadows, sharp product clarity, productive studio setting"
        }),
        (range(17, 22), {
            "phase": "Вечер",
            "code": "evening",
            "vibe": "Подведение итогов дня, завершение рабочих процессов, вечерний комфорт, искренняя забота",
            "caring_subtext": "Рабочий день подошел к концу, но мы еще здесь: перепроверяем детали и готовим всё к завтрашнему дню, чтобы вы могли спокойно отдыхать.",
            "window_lighting": "warm directional desk lamp contrasting with soft evening twilight and gentle blurred city skyline lights through window in background",
            "indoor_lighting": "warm focused 3000K desk lamp illuminating the work surface with soft organic light falloff into cozy background, delicate warm ambient room shadows, quiet focused evening studio atmosphere"
        }),
        (range(22, 24), {
            "phase": "Ночь",
            "code": "night",
            "vibe": "Глубокая концентрация, автономная работа 24/7, пока город спит",
            "caring_subtext": "Пока город спит, наши автономные алгоритмы и серверы работают на ваш бизнес 24/7.",
            "window_lighting": "low-key ambient lighting, glowing monitor telemetry, dark nocturnal city skyscraper lights bokeh outside panoramic window",
            "indoor_lighting": "intimate low-key directional task light illuminating subject with deep chiaroscuro shadows, glowing dark-mode screen telemetry, quiet nocturnal focus"
        }),
        (range(0, 6), {
            "phase": "Ночь",
            "code": "night",
            "vibe": "Глубокая концентрация, автономная работа 24/7, пока город спит",
            "caring_subtext": "Пока город спит, наши автономные алгоритмы и серверы работают на ваш бизнес 24/7.",
            "window_lighting": "low-key ambient lighting, glowing monitor telemetry, dark nocturnal city skyscraper lights bokeh outside panoramic window",
            "indoor_lighting": "intimate low-key directional task light illuminating subject with deep chiaroscuro shadows, glowing dark-mode screen telemetry, quiet nocturnal focus"
        })
    ]

    def __init__(self):
        self.collector = EventHolidayCollector() if EventHolidayCollector else None
        self.last_updated_date: Optional[date] = None
        self.cached_context: Dict[str, Any] = {}
        self.refresh()

    @classmethod
    def get_instance(cls) -> InternalCalendarEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def refresh(self, target_dt: Optional[datetime] = None, force: bool = False) -> Dict[str, Any]:
        now = target_dt or datetime.now()
        today = now.date()
        hour = now.hour
        month, day, weekday = now.month, now.day, now.weekday()
        year = now.year

        season_info = next(v for k, v in self.SEASONS.items() if month in k)
        day_info = self.DAY_PSYCHOLOGY[weekday]
        time_info = next(info for r, info in self.TIME_OF_DAY_SLOTS if hour in r)

        today_events = []
        upcoming_events = []
        if self.collector:
            try:
                events_calendar = self.collector.get_calendar_events(country="Россия", city="Москва", niche="all", days_count=14)
                today_events = [e for e in events_calendar if e.get("date") == f"{month:02d}-{day:02d}"]
                upcoming_events = [e for e in events_calendar if e.get("date") != f"{month:02d}-{day:02d}"][:5]
            except Exception:
                pass

        self.last_updated_date = today
        self.cached_context = {
            "current_year": year,
            "current_time_str": now.strftime("%H:%M"),
            "current_date_str": now.strftime(f"%d.%m.{year}"),
            "formatted_date_ru": f"{day} {self._get_month_name_ru(month)} {year} года",
            "day_of_week": day_info["name"],
            "day_vibe": day_info["vibe"],
            "time_phase": time_info["phase"],
            "time_code": time_info["code"],
            "time_vibe": time_info["vibe"],
            "caring_subtext": time_info["caring_subtext"],
            "window_lighting": time_info["window_lighting"],
            "indoor_lighting": time_info["indoor_lighting"],
            "season": season_info["season"],
            "seasonal_lighting": season_info["lighting_mod"],
            "seasonal_palette": season_info["palette"],
            "seasonal_narrative": season_info["narrative_focus"],
            "today_holidays": today_events,
            "upcoming_holidays_14d": upcoming_events
        }
        return self.cached_context

    def get_visual_lighting_anchor(self, topic: str = "", setting_desc: str = "", target_dt: Optional[datetime] = None) -> str:
        ctx = self.refresh(target_dt=target_dt)
        combined_text = f"{topic} {setting_desc}".lower()

        window_regex = r"\b(окн\w*|панорам\w*|балкон\w*|вид\s+на\s+город|скайлайн\w*|небоскреб\w*|витрин\w*|террас\w*|улиц\w*|фасад\w*|window\w*|panoramic|balcony|cityscape|skyline|outdoor)\b"
        has_window = bool(re.search(window_regex, combined_text))

        if has_window:
            return f"{ctx['window_lighting']}, {ctx['seasonal_lighting']}"
        else:
            return f"{ctx['indoor_lighting']}, {ctx['seasonal_lighting']}"

    def get_copywriting_temporal_prompt(self, target_dt: Optional[datetime] = None) -> str:
        ctx = self.refresh(target_dt=target_dt)
        holidays_today_str = ", ".join([h["title"] for h in ctx["today_holidays"]]) if ctx["today_holidays"] else "Обычный рабочий день"
        upcoming_str = "; ".join([f"{h['date']}: {h['title']}" for h in ctx["upcoming_holidays_14d"][:3]]) if ctx["upcoming_holidays_14d"] else "Плановые инфоповоды"

        return (
            f"ВРЕМЕННОЙ ЯКОРЬ И ЭМПАТИЯ КЛИЕНТА:\n"
            f"- Дата: {ctx['formatted_date_ru']} ({ctx['day_of_week']}), время публикации: {ctx['current_time_str']} ({ctx['time_phase']}).\n"
            f"- Сезонная фаза: {ctx['season']} ({ctx['seasonal_narrative']}).\n"
            f"- Психологический тон дня: {ctx['day_vibe']}.\n"
            f"- Подтекст времени суток (Забота о клиенте): {ctx['caring_subtext']}\n"
            f"- Праздники сегодня: {holidays_today_str}.\n"
            f"- Ближайшие инфоповоды (14 дней): {upcoming_str}.\n"
            f"ВАЖНО: Органично отрази в тональности текста время суток и день недели. Не используй банальные «Добрый вечер/день», транслируй заботу и вовлеченность через суть и контекст."
        )

    def _get_month_name_ru(self, m: int) -> str:
        names = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
        return names[m - 1]

__all__ = ["InternalCalendarEngine"]
