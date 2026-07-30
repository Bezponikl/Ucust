"""
Нейросетевой генеративный модуль (заглушка) для стратегии.
"""

from __future__ import annotations

from typing import List

from schemas.models import StrategyPlanSchema


class GenerativeCore:
    """
    Нейросетевой генеративный модуль для генерации стратегий.

    В реальной системе может использовать Saiga для генерации контента.
    """

    def process_request(self, context: str) -> StrategyPlanSchema:
        """
        Имитирует генерацию стратегии на основе входного контекста.

        :param context: агрегированный контекст.
        :return: стратегия, риски и рекомендации.
        """

        strategy = f"Стратегия сформирована для контекста: {context[:120]}..."
        risks: List[str] = ["Недостаточно данных о конкурентах", "Слабая уникальность контента"]
        recommendations: List[str] = ["Уточнить позиционирование", "Провести тестовый спринт публикаций"]
        technical_log = [
            "Нейросетевой генеративный модуль: старт",
            "Нейросетевой генеративный модуль: контекст обработан",
            "Нейросетевой генеративный модуль: стратегия сформирована",
        ]
        return StrategyPlanSchema(
            strategy=strategy,
            risks=risks,
            recommendations=recommendations,
            technical_log=technical_log,
        )

    def verify_facts(
        self,
        system_prompt: str,
        facts_context: str,
        draft_text: str,
        framework: Optional[Any] = None,
    ) -> tuple[str, List[str]]:
        """
        Имитирует верификацию фактов и структуры фреймворка нейросетью Saiga / LLM.
        Применяет правило дифференциации (Rule of Differentiation):
        - Разрешает риторические маркетинговые уловки и психологические триггеры (FOMO, эмоции).
        - Запрещает выдуманные конкретные акционные скидки и гарантии, которых нет в анкете клиента.
        """
        removed_claims: List[str] = []
        cleaned_text = draft_text

        # 1. Проверка на галлюцинации и невалидированные суперлативы
        if ("100%" in draft_text or "unverified_claim" in draft_text.lower()) and "ПРЕДЫДУЩАЯ ОШИБКА" not in draft_text:
            removed_claims.append("Удалены невалидированные метрики эффективности и суперлативы.")
            cleaned_text = draft_text.replace("100%", "").replace("unverified_claim", "")

        # 2. Проверка на выдуманные скидки и акции (Rule of Differentiation)
        if ("скидка 20%" in draft_text.lower() or "выдуманная акция" in draft_text.lower()) and "ПРЕДЫДУЩАЯ ОШИБКА" not in draft_text:
            if "скидка 20%" not in facts_context.lower() and "выдуманная акция" not in facts_context.lower():
                removed_claims.append("Выдумана акция/скидка, не подтвержденная клиентом.")
                cleaned_text = draft_text.replace("скидка 20%", "").replace("выдуманная акция", "")

        # 3. Проверка соответствия фреймворку (наличие CTA / призыва к действию)
        if "missing_cta" in draft_text.lower() and "ПРЕДЫДУЩАЯ ОШИБКА" not in draft_text:
            removed_claims.append("Отсутствует обязательный призыв к действию (CTA) согласно фреймворку.")
            cleaned_text = draft_text.replace("missing_cta", "")

        return cleaned_text, removed_claims

    def extract_visual_identity(self, posts_text: str) -> dict[str, str]:
        """
        Извлекает визуальный ДНК бренда (Tone of Voice, корпоративные цвета, маскоты, сфера деятельности)
        из прошлых публикаций клиента с помощью LLM (Saiga 3 / GPT-4).

        :param posts_text: Агрегированный текст последних 10-15 постов клиента.
        :return: Словарь с описанием визуального ДНК бренда.
        """
        return {
            "visual_tone_of_voice": "Минималистичный, футуристичный, высокотехнологичный B2B стиль",
            "corporate_colors": "Глубокий синий (#0F172A), неоновый циановый (#06B6D4), чистый белый (#FFFFFF)",
            "visual_anchors": "Геометрические светящиеся линии, голографические интерфейсы, динамическое освещение",
            "mascot_or_logo": "Лаконичный светящийся логотип UCust.AI в правом верхнем углу кадра",
            "industry": "Искусственный интеллект, IT-решения и автоматизация маркетинга",
        }

    def analyze_images(self, image_paths: List[str], prompt: str) -> dict[str, Any]:
        """
        Скелет (skeleton) для Vision-модели (LLaVA, GPT-4 Vision, Qwen-VL).
        Анализирует нарезку ключевых кадров .mp4 на наличие нейросетевых артефактов
        (анатомические ошибки, морфинг объектов, нарушение физики).

        :param image_paths: Пути к сохраненным JPG/PNG кадрам из видео.
        :param prompt: Промпт-инструкция для VLM.
        :return: Словарь с результатом анализа ('PASSED' | 'FAILED'), списком найденных артефактов и описанием.
        """
        # Скелет логики VLM: по умолчанию считает генерацию успешной (PASSED).
        # Для тестирования цикла QA регенерации можно раскомментировать симуляцию сбоя:
        # return {
        #     "status": "FAILED",
        #     "artifacts": ["extra_fingers", "object_morphing", "color_flicker"],
        #     "details": "Обнаружен морфинг фона и искажение формы пальцев на 2 и 3 кадре."
        # }

        return {
            "status": "PASSED",
            "artifacts": [],
            "details": "Кадры проверены VLM. Анатомических и физических артефактов не обнаружено.",
        }

    def extract_questionnaire_from_raw_text(self, raw_input: str) -> Any:
        """
        Text2Schema: Преобразует свободный текст ответа клиента в структурированную Pydantic-модель UserQuestionnaire.
        """
        from schemas.models import (
            QuestionnaireStep1,
            QuestionnaireStep2,
            QuestionnaireStep3,
            QuestionnaireStep4,
            QuestionnaireStep5,
            UserQuestionnaire,
        )

        snippet = raw_input[:200] if raw_input else "Дефолтный бриф"

        return UserQuestionnaire(
            step1=QuestionnaireStep1(
                business_name=f"Brand-{snippet[:20]}",
                mission=f"Автоматизация и маркетинг на базе: {snippet}",
                region="Москва и РФ",
            ),
            step2=QuestionnaireStep2(
                target_audience="B2B предприниматели и руководители",
                demographics="Мужчины и женщины 25-50 лет",
                age_range="25-50 лет",
                geo="Москва, Санкт-Петербург, РФ",
                core_audience_description="B2B предприниматели и руководители IT-стартапов",
                pain_points="Высокие затраты на ручной SMM и нехватка времени",
            ),
            step3=QuestionnaireStep3(
                tone_of_voice="Экспертный, уверенный",
                content_formats="Посты-кейсы, разборы, гайды",
                taboo_topics="Политика, незаверенные обещания",
            ),
            step4=QuestionnaireStep4(
                goals="Увеличение охватов и конверсия в лиды",
                kpi="ER, количество заявок",
                frequency="3 раза в неделю",
            ),
            step5=QuestionnaireStep5(
                competitors="CompetitorA, CompetitorB",
                references="IT-бренды и стартапы",
                additional_notes="Автоматически извлечено из неструктурированного текста",
            ),
        )

    GAP_ANALYSIS_SYSTEM_PROMPT = (
        "Ты — строго валидирующий AI-маркетолог системы UCust.AI.\n"
        "Твоя задача — проверить полноту демографических и смысловых данных целевой аудитории (ЦА) в анкете клиента.\n"
        "Правила проверки:\n"
        "1. ВОЗРАСТ (age_range): Должен быть явно указан возрастной диапазон (например, '25-45 лет'). Отсеивай 'все', 'любой', '0+'.\n"
        "2. ГЕОГРАФИЯ (geo): Должен быть указан конкретный город, регион или страна. Отсеивай 'везде', 'весь мир'.\n"
        "3. ЯДРО АУДИТОРИИ (core_audience_description / target_audience): Отсеивай размытые формулировки ('все люди', 'все подряд').\n"
        "Если хотя бы один параметр не валиден — верни статус FAILED и задай уточняющий вопрос пользователю."
    )

    def evaluate_questionnaire_gaps(self, questionnaire: Any) -> tuple[bool, str]:
        """
        Gap Analysis: Семантическая валидация маркетинговой пригодности брифа и полноты демографии ЦА.
        Переносит всю ответственность за демографию на диалог Интервьюера с клиентом.
        """
        step2 = getattr(questionnaire, "step2", None)
        if step2:
            ta = str(getattr(step2, "target_audience", "")).lower().strip()
            age = str(getattr(step2, "age_range", "")).lower().strip()
            geo = str(getattr(step2, "geo", "")).lower().strip()
            core_desc = str(getattr(step2, "core_audience_description", "")).lower().strip()

            vague_terms = {"все", "все люди", "все подряд", "любой", "все 18+", "everyone", "везде", "весь мир", "0+"}

            # Проверка 1: Размытое описание ЦА
            if ta in vague_terms or len(ta) < 5 or core_desc in vague_terms:
                return (
                    False,
                    "Опишите ваше ядро аудитории: примерный возраст, город/страна и главная проблема, которую решает ваш продукт.",
                )

            # Проверка 2: Отсутствие или невалидность возраста
            if not age or age in vague_terms or len(age) < 2:
                return (
                    False,
                    "Опишите ваше ядро аудитории: примерный возраст, город/страна и главная проблема, которую решает ваш продукт.",
                )

            # Проверка 3: Отсутствие или невалидность географии
            if not geo or geo in vague_terms or len(geo) < 2:
                return (
                    False,
                    "Опишите ваше ядро аудитории: примерный возраст, город/страна и главная проблема, которую решает ваш продукт.",
                )

        step1 = getattr(questionnaire, "step1", None)
        if step1 and len(step1.business_name.strip()) < 2:
            return (False, "Укажите корректное название компании или бренда (минимум 2 символа).")

        return (True, "Бриф прошел семантическую валидацию демографии и целевой аудитории.")

    def moderate_content_intent(self, text_or_questionnaire: Any) -> bool:
        """
        Intent & Moderation: Проверка брифа на NSFW, политику, экстремизм и спам.
        Returns True если бриф безопасен, и False если содержит нарушения.
        """
        raw_str = str(text_or_questionnaire).lower()
        forbidden_keywords = {"nsfw", "casino", "казино", "наркотики", "экстремизм", "fake_spam_bot"}

        for kw in forbidden_keywords:
            if kw in raw_str:
                return False

        return True

    def generate_search_queries_for_tactics(self, niche_description: str) -> List[str]:
        """
        Growth Hacker Step 1: Генерирует 2-3 сфокусированных поисковых запроса для веб-поиска
        успешных воронок, кейсов продаж и психологических триггеров в нише клиента.
        """
        niche_clean = niche_description[:60].strip() if niche_description else "B2B SMM"
        return [
            f"кейсы продаж {niche_clean} психологические триггеры",
            f"маркетинговые уловки воронки продаж {niche_clean}",
            f"лучшие офферы и лид-магниты {niche_clean} примеры",
        ]

    def extract_niche_sales_tactics(self, niche_description: str, raw_search_results: str) -> Any:
        """
        Growth Hacker Step 3: Передает результаты веб-поиска в LLM для структурирования
        в Pydantic-модель NicheSalesTacticsSchema.
        """
        from schemas.models import NicheSalesTacticsSchema

        niche_clean = niche_description[:40] if niche_description else "Маркетинг и IT"

        return NicheSalesTacticsSchema(
            niche_name=niche_clean,
            psychological_hooks=[
                "Синдром упущенной выгоды (FOMO) через ограниченный таймер спецпредложения",
                "Триггер экспертности: социальные доказательства и логотипы известных клиентов",
                "Эффект контраста цены: демонстрация упущенных расходов без нашего решения",
            ],
            successful_cases=[
                "Воронка через бесплатный экспресс-аудит с последующим оффером на внедрение",
                "Лид-магнит 'Чек-лист 10 ошибок SMM' с конверсией в демо-звонок 18%",
            ],
            promotional_mechanics=[
                "Формат '1+1' при годовой подписке на сервис",
                "Гарантия возврата средств в течение 14 дней при невыполнении KPI",
            ],
        )

    def normalize_niche_name(self, user_description: str) -> str:
        """
        Нормализует неструктурированное описание бизнеса клиента в стандартизированный snake_case slug
        (например: 'Делаем кухни и шкафы на заказ' -> 'custom_furniture').
        """
        if not user_description or not user_description.strip():
            return "general_marketing"

        text = user_description.lower().strip()
        if any(w in text for w in ["кухни", "шкафы", "мебель"]):
            return "custom_furniture"
        elif any(w in text for w in ["b2b", "автоматизация", "it", "софт", "продаж"]):
            return "b2b_saas_automation"
        elif any(w in text for w in ["недвижимость", "риелтор", "квартиры"]):
            return "real_estate"
        elif any(w in text for w in ["курсы", "обучение", "образование"]):
            return "edtech_education"
        elif any(w in text for w in ["косметика", "салон", "красота"]):
            return "beauty_salon"

        import re
        words = re.findall(r"[a-zA-Z0-9_]+", text)
        slug_words = [w for w in words if len(w) > 2][:3]
        if not slug_words:
            return "general_niche"
        return "_".join(slug_words)


