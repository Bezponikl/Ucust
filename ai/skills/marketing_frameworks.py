# File: skills/marketing_frameworks.py
"""
Marketing Frameworks & Psychological Triggers Engine for UCust.AI.
Усиливает маркетинговые навыки платформы без дообучения нейросети за счет:
1. 7 классических формул копирайтинга (AIDA, PAS, BAB, 4P, StoryBrand, Hook-Story-Offer, FAB).
2. Лестницы узнавания Бена Ханта (5 ступеней прогрева: Unaware -> Most Aware).
3. Психологических триггеров Чалдини (Social Proof, Scarcity, Authority, Reciprocity, Risk Reversal).
4. Динамического Few-Shot инжектирования золотых эталонов по нишам.
"""

from __future__ import annotations

import random
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple


class HuntStage(str, Enum):
    STAGE_1_UNAWARE = "unaware"                  # Холодные: не знают о проблеме (разрушение мифов, парадоксы)
    STAGE_2_PROBLEM_AWARE = "problem_aware"      # Осознание боли: чувствуют проблему, ищут причины
    STAGE_3_SOLUTION_AWARE = "solution_aware"    # Поиск решений: сравнивают методы и подходы
    STAGE_4_PRODUCT_AWARE = "product_aware"      # Выбор компании: кейсы, отзывы, экспертность бренда
    STAGE_5_MOST_AWARE = "most_aware"            # Горячие: готовы купить, нужен оффер и дедлайн


class MarketingFramework(str, Enum):
    AIDA = "AIDA"                  # Attention -> Interest -> Desire -> Action
    PAS = "PAS"                    # Problem -> Agitation -> Solution
    BAB = "BAB"                    # Before -> After -> Bridge
    FOUR_P = "4P"                  # Picture -> Promise -> Prove -> Push
    STORYBRAND = "StoryBrand"      # Hero -> Problem -> Guide -> Plan -> CTA -> Success
    HOOK_STORY_OFFER = "HSO"       # Hook -> Story -> Offer (Reels / Shorts)
    FAB = "FAB"                    # Feature -> Advantage -> Benefit


class PsychologicalTrigger(str, Enum):
    SOCIAL_PROOF = "social_proof"    # Отзывы, цифры клиентов, рейтинг 4.9
    SCARCITY_FOMO = "scarcity_fomo"  # Дефицит, ограничение по времени/слотам
    AUTHORITY = "authority"          # Оборудование, сертификаты, технологии, опыт
    RECIPROCITY = "reciprocity"      # Бесплатная польза, расчет сметы, чек-лист до продажи
    RISK_REVERSAL = "risk_reversal"  # Гарантия возврата, договор, оплата по результату


class MarketingFrameworkDirector:
    """
    Арт-директор маркетинговых фреймворков и прогрева:
    - Управляет архитектурой продающего текста без дообучения весов.
    - Автоматически выбирает оптимальный фреймворк под цель публикации и ступень воронки.
    - Инжектирует триггеры поведенческой экономики.
    """

    FRAMEWORK_DESCRIPTIONS = {
        MarketingFramework.AIDA: {
            "name": "AIDA (Attention, Interest, Desire, Action)",
            "goal": "Классическая универсальная продающая структура для промо и анонсов",
            "blocks": ["1. Взрывной заголовок (Внимание)", "2. Любопытный факт или инсайт (Интерес)", "3. Образ выгоды и результат (Желание)", "4. Прямой призыв к действию (Действие)"]
        },
        MarketingFramework.PAS: {
            "name": "PAS (Problem, Agitation, Solution)",
            "goal": "Пробитие баннерной слепоты через реальную боль клиента и ее нагнетание",
            "blocks": ["1. Обозначение острой проблемы (Боль)", "2. Что будет, если не решать проблему (Усиление боли)", "3. Решение от нашего бренда (Выход)"]
        },
        MarketingFramework.BAB: {
            "name": "BAB (Before, After, Bridge)",
            "goal": "Наглядная демонстрация трансформации клиента (до / после / инструмент)",
            "blocks": ["1. Как было плохо/сложно ДО обращения (Before)", "2. Как стало идеально и легко ПОСЛЕ (After)", "3. Как продукт бренда стал этим мостом (Bridge)"]
        },
        MarketingFramework.FOUR_P: {
            "name": "4P (Picture, Promise, Prove, Push)",
            "goal": "Эмоциональное погружение с твердыми доказательствами и дедлайном",
            "blocks": ["1. Яркая визуальная картинка мечты (Picture)", "2. Четкое обещание результата (Promise)", "3. Факты, цифры и отзывы (Prove)", "4. Дедлайн и жесткий призыв (Push)"]
        },
        MarketingFramework.STORYBRAND: {
            "name": "StoryBrand (7-Part Framework)",
            "goal": "Превращение клиента в главного Героя, а бренда — в мудрого Проводника",
            "blocks": ["1. Цель Героя-клиента", "2. Препятствие/Проблема", "3. Проводник (Наш бренд)", "4. Понятный план из 3 шагов", "5. Призыв к действию и образ триумфа"]
        },
        MarketingFramework.HOOK_STORY_OFFER: {
            "name": "Hook-Story-Offer (Reels / Shorts / Клипы)",
            "goal": "Удержание внимания в первые 3 секунды с переходом в историю и оффер",
            "blocks": ["1. 3-секундный хук-стоппер", "2. Короткая динамичная история / закулисье", "3. Финальный оффер с ограничением по времени"]
        },
        MarketingFramework.FAB: {
            "name": "FAB (Feature, Advantage, Benefit)",
            "goal": "Перевод технических характеристик продукта на язык личной выгоды покупателя",
            "blocks": ["1. Характеристика (Что сделано)", "2. Преимущество (Почему лучше аналогов)", "3. Выгода клиента (Сколько сэкономит / как облегчит жизнь)"]
        }
    }

    # Золотые эталонные хуки и триггеры по ступеням Ханта
    HUNT_STAGE_STRATEGIES = {
        HuntStage.STAGE_1_UNAWARE: {
            "framework": MarketingFramework.BAB,
            "trigger": PsychologicalTrigger.RECIPROCITY,
            "hook_formula": "«90% людей даже не подозревают, почему...»",
            "vibe": "Разрушение мифов, вовлечение, легкий юмор, лайфстайл"
        },
        HuntStage.STAGE_2_PROBLEM_AWARE: {
            "framework": MarketingFramework.PAS,
            "trigger": PsychologicalTrigger.AUTHORITY,
            "hook_formula": "«Знакомая ситуация: вы платите за X, а получаете...»",
            "vibe": "Точный удар в скрытые риски, переплаты и потерянное время"
        },
        HuntStage.STAGE_3_SOLUTION_AWARE: {
            "framework": MarketingFramework.FAB,
            "trigger": PsychologicalTrigger.AUTHORITY,
            "hook_formula": "«Сравнение в лоб: метод А против метода Б. Что выбрать в 2026 году?»",
            "vibe": "Экспертное сравнение подходов, факты, прозрачный расчет сметы"
        },
        HuntStage.STAGE_4_PRODUCT_AWARE: {
            "framework": MarketingFramework.STORYBRAND,
            "trigger": PsychologicalTrigger.SOCIAL_PROOF,
            "hook_formula": "«Кейс: как мы решили нестандартную задачу клиента за 48 часов»",
            "vibe": "Твердые кейсы, отзывы, демонстрация процессов в цеху/клинике, гарантии"
        },
        HuntStage.STAGE_5_MOST_AWARE: {
            "framework": MarketingFramework.AIDA,
            "trigger": PsychologicalTrigger.SCARCITY_FOMO,
            "hook_formula": "«Только до [дедлайн]: специальное предложение для тех, кто планировал...»",
            "vibe": "Прямая продажа, дедлайн, скидка, бронь слота, четкий CTA"
        }
    }

    # Психологические триггеры Чалдини
    TRIGGER_TEMPLATES = {
        PsychologicalTrigger.SOCIAL_PROOF: "⭐ Социальное доказательство: более {client_count} довольных клиентов, средний рейтинг {rating}/5 на основе реальных отзывов.",
        PsychologicalTrigger.SCARCITY_FOMO: "⏳ Дефицит и дедлайн: спецпредложение действует только до конца недели (осталось {slots_count} свободных слота).",
        PsychologicalTrigger.AUTHORITY: "🏆 Авторитет и технологии: сертифицированное оборудование, строгие стандарты качества и опыт мастеров от 10 лет.",
        PsychologicalTrigger.RECIPROCITY: "🎁 Взаимный обмен: напишите нам сейчас и получите бесплатный расчет сметы / 3D-визуализацию в подарок до оформления заказа.",
        PsychologicalTrigger.RISK_REVERSAL: "🛡️ Снятие рисков: официальный договор, фиксированная цена без скрытых доплат и гарантия качества до 5 лет."
    }

    @classmethod
    def get_stage_for_day(cls, day_index: int, total_days: int = 30) -> HuntStage:
        """
        Равномерно и циклично распределяет дни контент-плана по лестнице прогрева Ханта.
        """
        cycle = [
            HuntStage.STAGE_1_UNAWARE,
            HuntStage.STAGE_2_PROBLEM_AWARE,
            HuntStage.STAGE_3_SOLUTION_AWARE,
            HuntStage.STAGE_4_PRODUCT_AWARE,
            HuntStage.STAGE_5_MOST_AWARE,
            HuntStage.STAGE_2_PROBLEM_AWARE,
            HuntStage.STAGE_4_PRODUCT_AWARE
        ]
        return cycle[day_index % len(cycle)]

    @classmethod
    def construct_marketing_prompt(
        cls,
        company_name: str,
        niche: str,
        topic: str,
        framework: Optional[MarketingFramework] = None,
        hunt_stage: Optional[HuntStage] = None,
        trigger: Optional[PsychologicalTrigger] = None,
        brand_dna: Optional[Dict[str, Any]] = None,
        website_dossier: Optional[str] = None,
        pain_points: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Генерирует высокоточный когнитивный промпт для LLM с жесткой структурой фреймворка,
        ступенью лестницы Ханта и поведенческим триггером.
        """
        stage = hunt_stage or HuntStage.STAGE_3_SOLUTION_AWARE
        stage_meta = cls.HUNT_STAGE_STRATEGIES[stage]
        
        chosen_framework = framework or stage_meta["framework"]
        chosen_trigger = trigger or stage_meta["trigger"]

        framework_info = cls.FRAMEWORK_DESCRIPTIONS[chosen_framework]
        trigger_text = cls.TRIGGER_TEMPLATES[chosen_trigger].format(
            client_count="1 200+",
            rating="4.9",
            slots_count="3"
        )

        pains_str = ", ".join(pain_points[:3]) if pain_points else "страх некачественной работы, переплаты, срыв сроков"

        prompt_instructions = (
            f"Ты — элитный маркетинговый стратег и копирайтер высшей категории.\n"
            f"Напиши публикацию для компании «{company_name}» (Ниша: {niche}).\n\n"
            f"🎯 ТЕМА ПУБЛИКАЦИИ: {topic}\n"
            f"🪜 СТУПЕНЬ ПРОГРЕВА ЦА (Лестница Ханта): {stage.value.upper()} ({stage_meta['vibe']})\n"
            f"📐 МАРКЕТИНГОВЫЙ ФРЕЙМВОРК: {framework_info['name']}\n"
            f"Обязательная структура текста:\n"
            + "\n".join([f"  • {b}" for b in framework_info['blocks']]) + "\n\n"
            f"🧠 ПСИХОЛОГИЧЕСКИЙ ТРИГГЕР ДЛЯ ВШИВАНИЯ: {chosen_trigger.value.upper()}\n"
            f"Формула триггера: «{trigger_text}»\n\n"
            f"⚡ БОЛИ АУДИТОРИИ ДЛЯ ЗАКРЫТИЯ: {pains_str}\n"
            f"🚫 СТРОГИЕ ПРАВИЛА: Никаких штампов («мы динамично развиваемся», «рады представить»). Только факты, польза, живой ритм и понятный призыв к действию."
        )

        return {
            "framework": chosen_framework.value,
            "framework_name": framework_info["name"],
            "hunt_stage": stage.value,
            "psychological_trigger": chosen_trigger.value,
            "trigger_prompt": trigger_text,
            "full_marketing_prompt": prompt_instructions
        }

    @classmethod
    def generate_post_with_framework(
        cls,
        company_name: str,
        niche: str,
        topic: str,
        framework: MarketingFramework = MarketingFramework.PAS,
        hunt_stage: HuntStage = HuntStage.STAGE_2_PROBLEM_AWARE,
        trigger: PsychologicalTrigger = PsychologicalTrigger.SOCIAL_PROOF,
        pain_points: Optional[List[str]] = None,
        contacts: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Генерирует готовый эталонный пост, строго следующий выбранному фреймворку
        (AIDA, PAS, BAB, 4P, StoryBrand, Hook-Story-Offer, FAB) с вшитым психологическим триггером.
        """
        f_info = cls.FRAMEWORK_DESCRIPTIONS[framework]
        t_text = cls.TRIGGER_TEMPLATES[trigger].format(client_count="1 200+", rating="4.9", slots_count="3")
        
        lead = ""
        body = ""
        cta = ""

        # 1. AIDA
        if framework == MarketingFramework.AIDA:
            lead = f"🔥 «{topic}» — как получить максимум результата в {niche}?"
            body = (
                f"Интересный факт: 8 из 10 клиентов сталкиваются с тем, что результат не оправдывает ожиданий из-за скрытых компромиссов в качестве.\n\n"
                f"В «{company_name}» мы выстроили процесс иначе: европейские стандарты, прозрачная смета и пошаговый контроль на каждом этапе.\n\n"
                f"{t_text}"
            )
            cta = "👉 Напишите в сообщения сообщества слово «КОНСУЛЬТАЦИЯ» — забронируйте спецпредложение до конца недели!"

        # 2. PAS (Боль -> Усиление -> Решение)
        elif framework == MarketingFramework.PAS:
            lead = f"⚠️ Почему 90% попыток сэкономить на услугах в сфере {niche} заканчиваются переплатой в 2 раза?"
            body = (
                f"Проблема: вы заказываете услугу, надеясь на быстрый результат, но получаете срыв сроков, переделки и скрытые доплаты.\n\n"
                f"Чем дольше тянуть с исправлением, тем выше итоговые затраты и потерянные нервы.\n\n"
                f"Решение от «{company_name}»: мы берем на себя полную ответственность по официальному договору. {t_text}"
            )
            cta = "📩 Оставьте заявку в директ или напишите в комментарии «+» — рассчитаем точную стоимость за 15 минут!"

        # 3. BAB (Before -> After -> Bridge)
        elif framework == MarketingFramework.BAB:
            lead = f"🔄 До и После: реальная трансформация с «{company_name}»"
            body = (
                f"❌ ДО: долгий поиск надежных исполнителей, сомнения в качестве и постоянный стресс из-за дедлайнов.\n\n"
                f"✅ ПОСЛЕ: идеальный результат точно в срок, премиальный внешний вид и абсолютное спокойствие за каждую деталь.\n\n"
                f"🌉 МОСТ: наш авторский подход и строгий контроль качества помогли закрыть эту задачу без единой переделки. {t_text}"
            )
            cta = "✨ Хотите такой же результат? Напишите нам в личные сообщения для детального разбора вашего проекта!"

        # 4. 4P (Picture -> Promise -> Prove -> Push)
        elif framework == MarketingFramework.FOUR_P:
            lead = f"✨ Представьте: ваш проект в сфере {niche} реализован безупречно с первого раза"
            body = (
                f"Картина: вы получаете именно то, о чем мечтали — стильно, надежно и без головной боли.\n\n"
                f"Обещание «{company_name}»: мы гарантируем соблюдение всех технических норм и фиксируем финальную цену в договоре.\n\n"
                f"Доказательства: {t_text}\n\n"
                f"Дедлайн: бронирование льготных условий открыто только до воскресенья!"
            )
            cta = "🚀 Жмите на кнопку сообщения или звоните прямо сейчас — не упустите свой слот!"

        # 5. StoryBrand (Клиент - Герой, Бренд - Проводник)
        elif framework == MarketingFramework.STORYBRAND:
            lead = f"📖 История одного решения: как преодолеть главное препятствие в {niche}"
            body = (
                f"Каждый наш клиент стремится к совершенству, но на пути часто встают недобросовестные подрядчики и раздутые сметы.\n\n"
                f"Команда «{company_name}» выступает вашим надежным проводником. Наш план предельно прост:\n"
                f"1. Бесплатный аудит и расчет\n"
                f"2. Заключение прозрачного договора\n"
                f"3. Сдача идеального результата под ключ\n\n"
                f"{t_text}"
            )
            cta = "🎯 Сделайте первый шаг к цели — напишите нам в личные сообщения прямо сейчас!"

        # 6. Hook-Story-Offer (Reels/Shorts)
        elif framework == MarketingFramework.HOOK_STORY_OFFER:
            lead = f"⚡ Перестаньте делать это, если хотите идеальный результат в {niche}!"
            body = (
                f"Вчера на объекте команда «{company_name}» столкнулась с классической ошибкой: клиент доверился обещаниям на словах и потерял 3 недели.\n\n"
                f"Мы исправили ситуацию за 2 дня благодаря отлаженным технологиям и опыту команды.\n\n"
                f"{t_text}"
            )
            cta = "🔥 Пишите «ХОЧУ» в комментариях — вышлем персональный оффер и чек-лист от «" + company_name + "» в личные сообщения!"

        # 7. FAB (Feature -> Advantage -> Benefit)
        else:
            lead = f"💎 В чем секрет качества «{company_name}»? Разбор на пальцах"
            body = (
                f"Характеристика (Feature): мы используем только оригинальные сертифицированные материалы и технологии.\n\n"
                f"Преимущество (Advantage): это исключает износ, деформацию и брак, в отличие от бюджетных аналогов.\n\n"
                f"Выгода для вас (Benefit): вы экономите до 40% бюджета в долгосрочной перспективе и наслаждаетесь результатом годами.\n\n"
                f"{t_text}"
            )
            cta = "📲 Узнайте подробности и оформите заявку в сообщениях сообщества!"

        full_post = f"{lead}\n\n{body}\n\n{cta}"

        return {
            "status": "success",
            "company_name": company_name,
            "niche": niche,
            "topic": topic,
            "framework": framework.value,
            "framework_name": f_info["name"],
            "hunt_stage": hunt_stage.value,
            "psychological_trigger": trigger.value,
            "post_text": full_post,
            "hashtags": f"#{niche.replace(' ', '')} #{company_name.replace(' ', '')} #маркетинг #качество"
        }
