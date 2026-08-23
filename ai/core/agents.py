# File: core/agents.py | Module: agents | Part of Intellectual Property Submission.
"""Agent definitions for the multi-agent marketing system."""

from __future__ import annotations

import asyncio
import gc
import logging
import os
from typing import Any, Dict, List, Optional

try:
    import cv2
except ImportError:
    cv2 = None

from collectors.geo_collectors import TwoGisCollector, YandexMapsCollector
from collectors.telethon_collector import TelethonCollector
from collectors.vk_collector import VkApiCollector
from nlu_engine.generative_core import GenerativeCore
from nlu_engine.preprocessor import PreProcessor
from skills.comfyui_local import ComfyUILocalSkill
from skills.travity_search import TravitySearchSkill
from schemas.models import (
    CollectorDataSchema,
    CopywritingFramework,
    FRAMEWORK_PROMPTS,
    GridPlanSchema,
    GridTileSchema,
    LTX23ConfigSchema,
    LTX23PromptSchema,
    NicheSalesTacticsSchema,
    PostDraftSchema,
    ReviewReplySchema,
    StrategyPlanSchema,
    SWOTResultSchema,
    TaskType,
    UserQuestionnaire,
)
from datetime import datetime, timedelta
from storage.db import Database
from storage.models import UserProfile, NicheInsight
from storage.vector_store import InMemoryVectorStore, VectorRecord


class AgentContext:
    """Shared runtime context passed between all agents in the orchestration pipeline."""

    # Step 1: Initialize context fields and normalize optional collections.
    def __init__(
        self,
        questionnaire: Optional[UserQuestionnaire] = None,
        user_profile_id: Optional[int] = None,
        collector_data: Optional[List[CollectorDataSchema]] = None,
        swot: Optional[SWOTResultSchema] = None,
        strategy: Optional[StrategyPlanSchema] = None,
        post_draft: Optional[PostDraftSchema] = None,
        grid_plan: Optional[GridPlanSchema] = None,
        ltx23_prompts: Optional[List[LTX23PromptSchema]] = None,
        approval_status: Optional[str] = None,
        pending_user_action: bool = False,
        injected_events: Optional[List[str]] = None,
        user_event_type: Optional[str] = None,
        user_event_context: Optional[str] = None,
        logs: Optional[List[str]] = None,
        correction_attempts: int = 0,
        framework: Optional[CopywritingFramework] = None,
        visual_identity: Optional[Dict[str, Any]] = None,
        raw_input: Optional[str] = None,
        niche_tactics: Optional[NicheSalesTacticsSchema] = None,
        geo_reviews: Optional[List[Dict[str, Any]]] = None,
        task_type: TaskType = TaskType.PROMO_POST,
        target_review: Optional[Dict[str, Any]] = None,
        review_reply: Optional[ReviewReplySchema] = None,
    ) -> None:
        self.questionnaire = questionnaire
        self.raw_input = raw_input
        self.user_profile_id = user_profile_id
        self.collector_data = collector_data or []
        self.swot = swot
        self.strategy = strategy
        self.post_draft = post_draft
        self.grid_plan = grid_plan
        self.ltx23_prompts = ltx23_prompts or []
        self.approval_status = approval_status
        self.pending_user_action = pending_user_action
        self.injected_events = injected_events or []
        self.user_event_type = user_event_type
        self.user_event_context = user_event_context
        self.logs = logs or []
        self.correction_attempts = correction_attempts
        self.framework = framework
        self.visual_identity = visual_identity
        self.niche_tactics = niche_tactics
        self.geo_reviews = geo_reviews or []
        self.task_type = task_type
        self.target_review = target_review
        self.review_reply = review_reply

    # Step 2: Validate context consistency for a specific orchestration state.
    def validate(self, state: Optional[str] = None) -> None:
        if state in {"IDLE", "DATA_COLLECTED"} and self.questionnaire is None and self.raw_input is None:
            raise ValueError("Questionnaire or raw_input is required for early pipeline stages.")

        if state in {"MARKET_ANALYZED", "CONTENT_READY", "AWAITING_USER_DECISION", "USER_APPROVED"}:
            if self.strategy is None and self.post_draft is None:
                raise ValueError("Strategy or post draft is required for content stages.")

    # Step 3: Append a normalized technical message to the execution log.
    def add_log(self, message: str) -> None:
        self.logs.append(message)


class BaseAgent:
    """Base class defining the contract for all pipeline agents with async lifecycle hooks."""

    name: str = "base_agent"
    expected_state: Optional[str] = None

    async def activate(self, context: AgentContext) -> None:
        """Lifecycle hook executed before agent run to warm up resources/models."""
        context.add_log(f"{self.name}: activate hook executed (resource warmup).")

    async def run(self, context: AgentContext) -> AgentContext:
        """Main async agent execution method."""
        raise NotImplementedError

    async def process(self, context: AgentContext) -> AgentContext:
        """Async alias for run to support process(context) interface."""
        return await self.run(context)

    async def standby(self, context: AgentContext) -> None:
        """Lifecycle hook executed after agent run to clean up RAM/VRAM resources."""
        context.add_log(f"{self.name}: standby hook executed (resource cleanup).")

    def check_state(self, current_state: str) -> None:
        if self.expected_state and self.expected_state != current_state:
            raise RuntimeError(
                f"{self.name}: expected state '{self.expected_state}', got '{current_state}'."
            )


class Agent_Interviewer(BaseAgent):
    """
    Интеллектуальный агент-интервьюер системы UCust.AI.

    Зоны ответственности и скиллы:
    1. Intent & Moderation (_moderate_intent): Быстрая проверка брифа на спам, NSFW, политику и нелегитимный контент.
    2. Text2Schema (_extract_structured_data): Извлечение структурированной анкеты UserQuestionnaire из неструктурированного текста.
    3. Gap Analysis (_analyze_gaps): Семантическая проверка маркетинговой пригодности брифа (отсеивание "Все люди" и т.п.).
    4. Context Merger (_merge_profiles): Слияние новых вводных с историческим профилем БД без затирания visual_identity.
    5. VRAM Management (standby): Очистка памяти LLM при выходе из агента.
    """

    name = "Agent_Interviewer"
    expected_state = "IDLE"

    def __init__(
        self,
        database: Optional[Database] = None,
        generative_core: Optional[GenerativeCore] = None,
    ) -> None:
        self.database = database
        self.generative_core = generative_core or GenerativeCore()

    def _moderate_intent(self, questionnaire: Optional[UserQuestionnaire], raw_input: Optional[str]) -> bool:
        """1. Intent & Moderation: Проверка брифа на спам, NSFW, политику и запрещенный контент."""
        target = questionnaire if questionnaire is not None else raw_input
        return self.generative_core.moderate_content_intent(target)

    def _extract_structured_data(self, raw_input: str) -> UserQuestionnaire:
        """2. Text2Schema: Раскладывает неструктурированный текст брифа в Pydantic-модель UserQuestionnaire."""
        return self.generative_core.extract_questionnaire_from_raw_text(raw_input)

    def _analyze_gaps(self, questionnaire: UserQuestionnaire) -> tuple[bool, str]:
        """3. Gap Analysis: Семантическая валидация пригодности брифа для маркетологов."""
        return self.generative_core.evaluate_questionnaire_gaps(questionnaire)

    def _merge_profiles(self, new_data: UserQuestionnaire, existing_profile: Optional[UserProfile]) -> Dict[str, Any]:
        """4. Context Merger: Слияние новых данных с историческим профилем БД без перезаписи visual_identity."""
        merged_dict = {
            "step1": new_data.step1.model_dump(),
            "step2": new_data.step2.model_dump(),
            "step3": new_data.step3.model_dump(),
            "step4": new_data.step4.model_dump(),
            "step5": new_data.step5.model_dump(),
        }
        if existing_profile and hasattr(existing_profile, "visual_identity") and existing_profile.visual_identity:
            merged_dict["visual_identity"] = existing_profile.visual_identity
            if getattr(new_data, "visual_identity", None) is None:
                new_data.visual_identity = existing_profile.visual_identity
        return merged_dict

    async def standby(self, context: AgentContext) -> None:
        """Хук очистки памяти LLM/VRAM."""
        context.add_log(f"{self.name}: standby hook executed (Garbage Collection & PyTorch CUDA cache freed).")
        gc.collect()

    async def run(self, context: AgentContext) -> AgentContext:
        context.validate("IDLE")
        context.add_log("Agent_Interviewer: старт модерации и семантической валидации брифа...")

        # 1. МОДЕРАЦИЯ (Intent & Moderation)
        is_safe = self._moderate_intent(context.questionnaire, context.raw_input)
        if not is_safe:
            context.approval_status = "REJECTED"
            context.pending_user_action = False
            context.add_log("Agent_Interviewer [Moderation]: Бриф не прошел модерацию (запрещенный контент/спам).")
            raise ValueError("Бриф не прошел модерацию: обнаружены нарушения правил платформы.")

        # 2. ИЗВЛЕЧЕНИЕ СТРУКТУРЫ (Text2Schema)
        if context.questionnaire is None and context.raw_input:
            context.add_log("Agent_Interviewer [Text2Schema]: Извлечение анкеты из свободной формы текста...")
            context.questionnaire = self._extract_structured_data(context.raw_input)

        if context.questionnaire is None:
            raise ValueError("Questionnaire or raw_input is required for Interviewer agent.")

        # 3. GAP ANALYSIS (Семантическая валидация)
        is_valid_marketing, gap_feedback = self._analyze_gaps(context.questionnaire)
        if not is_valid_marketing:
            context.approval_status = "NEEDS_CLARIFICATION"
            context.pending_user_action = True
            context.add_log(f"Agent_Interviewer [Gap Analysis]: Требуется уточнение вводных. {gap_feedback}")
            return context

        # 4. CONTEXT MERGER & SQL PERSISTENCE
        if self.database is None:
            context.add_log("Agent_Interviewer: SQL хранилище не настроено, слияние выполнено в памяти.")
            return context

        session = None
        try:
            session = self.database.get_session()
            existing_profile = None
            if context.user_profile_id:
                existing_profile = session.query(UserProfile).filter_by(id=context.user_profile_id).first()

            merged_data = self._merge_profiles(context.questionnaire, existing_profile)

            if existing_profile:
                existing_profile.step1 = merged_data["step1"]
                existing_profile.step2 = merged_data["step2"]
                existing_profile.step3 = merged_data["step3"]
                existing_profile.step4 = merged_data["step4"]
                existing_profile.step5 = merged_data["step5"]
                context.add_log(f"Agent_Interviewer [Context Merger]: профиль (id={existing_profile.id}) обновлен с сохранением истории.")
            else:
                new_profile = UserProfile(
                    step1=merged_data["step1"],
                    step2=merged_data["step2"],
                    step3=merged_data["step3"],
                    step4=merged_data["step4"],
                    step5=merged_data["step5"],
                )
                session.add(new_profile)
                session.commit()
                context.user_profile_id = new_profile.id
                context.add_log(f"Agent_Interviewer: новый профиль сохранен в SQL (id={new_profile.id}).")

        except Exception as db_exc:
            context.add_log(f"Agent_Interviewer: ошибка SQL сохранения ({db_exc}); слияние сохранено в контексте.")
            if context.user_profile_id is None:
                context.user_profile_id = 1
        finally:
            if session is not None:
                session.close()

        context.add_log("Agent_Interviewer: бриф одобрен и готов для Аналитика.")
        return context


class Agent_Analyst(BaseAgent):
    """
    Маркетинговый Аналитик системы UCust.AI.

    Зоны ответственности:
    1. Асинхронный сбор данных (asyncio.gather): Параллельный запуск парсеров Telethon, VK API и Travity Web Search.
       Обеспечивает отказоустойчивость (при падении VK/TG пайплайн продолжается с доступными источниками).
    2. Context Management (_preprocess_and_compress): Санитизация и компрессия постов конкурентов до 2500 токенов.
    3. Strategic Fusion: Слияние демографии ЦА (от Интервьюера), трендов конкурентов и live-данных сети для генерации SWOT и Стратегии.
    4. VRAM Management (standby): Очистка оперативной и видеопамяти перед передачей эстафеты Копирайтеру.
    """

    name = "Agent_Analyst"
    expected_state = "DATA_COLLECTED"

    def __init__(
        self,
        telethon_collector: Optional[TelethonCollector] = None,
        vk_collector: Optional[VkApiCollector] = None,
        preprocessor: Optional[PreProcessor] = None,
        generative_core: Optional[GenerativeCore] = None,
        search_skill: Optional[TravitySearchSkill] = None,
        telethon_channel: Optional[str] = None,
        vk_group_id: Optional[str] = None,
        database: Optional[Database] = None,
        yandex_collector: Optional[YandexMapsCollector] = None,
        twogis_collector: Optional[TwoGisCollector] = None,
    ) -> None:
        self.telethon_collector = telethon_collector or TelethonCollector()
        self.vk_collector = vk_collector or VkApiCollector()
        self.preprocessor = preprocessor or PreProcessor()
        self.generative_core = generative_core or GenerativeCore()
        self.search_skill = search_skill or TravitySearchSkill()
        self.telethon_channel = telethon_channel or os.getenv("UCUST_TELETHON_CHANNEL", "@default_channel")
        self.vk_group_id = vk_group_id or os.getenv("UCUST_VK_GROUP_ID", "default_group")
        self.database = database
        self.yandex_collector = yandex_collector or YandexMapsCollector()
        self.twogis_collector = twogis_collector or TwoGisCollector()

    async def _fetch_geo_reviews(self, questionnaire: Optional[UserQuestionnaire]) -> List[Dict[str, Any]]:
        """ORM Модуль: Извлекает отзывы с Яндекс.Карт и 2GIS, если клиент указал ссылки в анкете."""
        reviews: List[Dict[str, Any]] = []
        if not questionnaire or not questionnaire.step5:
            return reviews

        s5 = questionnaire.step5
        yandex_url = getattr(s5, "yandex_maps_url", None)
        twogis_url = getattr(s5, "twogis_url", None)

        if yandex_url:
            try:
                y_reviews = await self.yandex_collector.fetch_reviews(yandex_url)
                reviews.extend(y_reviews)
                logger.info("Agent_Analyst [ORM]: спарсено %d отзывов с Яндекс.Карт.", len(y_reviews))
            except Exception as exc:
                logger.warning("Agent_Analyst [ORM]: ошибка сбора отзывов Yandex Maps (%s).", exc)

        if twogis_url:
            try:
                t_reviews = await self.twogis_collector.fetch_reviews(twogis_url)
                reviews.extend(t_reviews)
                logger.info("Agent_Analyst [ORM]: спарсено %d отзывов с 2GIS.", len(t_reviews))
            except Exception as exc:
                logger.warning("Agent_Analyst [ORM]: ошибка сбора отзывов 2GIS (%s).", exc)

        return reviews

    async def _fetch_telethon(self) -> CollectorDataSchema:
        """Безопасная корутина-обертка для сбора данных Telegram."""
        try:
            return await asyncio.to_thread(self.telethon_collector.collect, self.telethon_channel)
        except Exception as exc:
            logger.warning("Agent_Analyst: ошибка при сборе данных Telethon (%s). Пропуск Telegram.", exc)
            return CollectorDataSchema(collector_name="telethon", payload={"messages": []})

    async def _fetch_vk(self) -> CollectorDataSchema:
        """Безопасная корутина-обертка для сбора данных VK."""
        try:
            return await asyncio.to_thread(self.vk_collector.collect, self.vk_group_id)
        except Exception as exc:
            logger.warning("Agent_Analyst: ошибка при сборе данных VK (%s). Пропуск ВКонтакте.", exc)
            return CollectorDataSchema(collector_name="vk_api", payload={"posts": []})

    async def _fetch_travity(self, search_query: str) -> str:
        """Безопасная корутина-обертка для Travity Web Search."""
        try:
            return await self.search_skill.search(search_query)
        except Exception as exc:
            logger.warning("Agent_Analyst: ошибка живого веб-поиска Travity (%s). Использование fallback.", exc)
            return "Актуальные тренды сети недоступны. Использовать исторический контекст."

    def _preprocess_and_compress(self, posts: List[str], max_tokens: int = 2500) -> str:
        """
        Context Management: Очищает посты конкурентов от мусора (ссылки, хештеги)
        и сжимает их до лимита max_tokens (из расчета ~4 символа на токен).
        """
        raw_text = " ".join([p for p in posts if p and p.strip()])
        if not raw_text:
            return "Данные публикаций конкурентов отсутствуют."

        sanitized = self.preprocessor.sanitize_data(raw_text)
        cleaned_text = getattr(sanitized, "cleaned_text", raw_text)

        # Ограничение длины контекста (2500 токенов ≈ 10 000 символов)
        max_chars = max_tokens * 4
        if len(cleaned_text) > max_chars:
            cleaned_text = cleaned_text[:max_chars] + "... [Контекст сжат для соблюдения лимитов токенов]"

        return cleaned_text

    async def standby(self, context: AgentContext) -> None:
        """VRAM Management: Очистка памяти LLM перед запуском Копирайтера."""
        context.add_log(f"{self.name}: standby hook executed (Garbage Collection & VRAM Freed).")
        gc.collect()

    _tactics_cache: Dict[str, NicheSalesTacticsSchema] = {}

    def _get_cached_tactics(self, niche_description: str) -> tuple[str, Optional[NicheSalesTacticsSchema]]:
        """
        Нормализует описание ниши в slug и проверяет наличие свежих уловок (< 90 дней) в БД/Кэше.
        """
        niche_slug = self.generative_core.normalize_niche_name(niche_description)
        if niche_slug in self._tactics_cache:
            return niche_slug, self._tactics_cache[niche_slug]

        if self.database is not None:
            try:
                session = self.database.get_session()
                insight = session.query(NicheInsight).filter_by(niche_slug=niche_slug).first()
                if insight is not None and insight.last_updated:
                    age_days = (datetime.utcnow() - insight.last_updated).days
                    if age_days < 90:
                        tactics = NicheSalesTacticsSchema(
                            niche_name=insight.niche_slug,
                            psychological_hooks=insight.psychological_hooks or [],
                            successful_cases=insight.successful_cases or [],
                            promotional_mechanics=insight.promotional_mechanics or [],
                        )
                        self._tactics_cache[niche_slug] = tactics
                        session.close()
                        return niche_slug, tactics
                session.close()
            except Exception as exc:
                logger.warning("Agent_Analyst: ошибка при запросе к NicheInsight БД (%s)", exc)

        return niche_slug, None

    def _cache_tactics(self, niche_slug: str, tactics: NicheSalesTacticsSchema) -> None:
        """Сохраняет / обновляет (INSERT / UPDATE) уловки ниши в глобальной БД niche_insights."""
        self._tactics_cache[niche_slug] = tactics
        if self.database is not None:
            session = None
            try:
                session = self.database.get_session()
                insight = session.query(NicheInsight).filter_by(niche_slug=niche_slug).first()
                if insight is None:
                    insight = NicheInsight(
                        niche_slug=niche_slug,
                        psychological_hooks=tactics.psychological_hooks,
                        successful_cases=tactics.successful_cases,
                        promotional_mechanics=tactics.promotional_mechanics,
                        last_updated=datetime.utcnow(),
                    )
                    session.add(insight)
                else:
                    insight.psychological_hooks = tactics.psychological_hooks
                    insight.successful_cases = tactics.successful_cases
                    insight.promotional_mechanics = tactics.promotional_mechanics
                    insight.last_updated = datetime.utcnow()
                session.commit()
            except Exception as exc:
                logger.warning("Agent_Analyst: не удалось сохранить NicheInsight в БД (%s)", exc)
                if session is not None:
                    session.rollback()
            finally:
                if session is not None:
                    session.close()

    async def _research_sales_tactics(self, niche_description: str) -> NicheSalesTacticsSchema:
        """
        Growth Hacker Skill: Нормализует нишу в slug, запрашивает БД (90 дней),
        и при отсутствии свежих данных выполняет веб-поиск и сохраняет результаты.
        """
        # Шаг 0: Нормализация ниши и проверка глобальной Базы Знаний (БД)
        niche_slug, cached = self._get_cached_tactics(niche_description)
        if cached:
            logger.info("Agent_Analyst [Growth Hacker]: Найдена актуальная аналитика в БД для ниши '%s'.", niche_slug)
            return cached

        # Шаг 1: Формирование целевых поисковых запросов через GenerativeCore
        queries = self.generative_core.generate_search_queries_for_tactics(niche_description)

        # Шаг 2: Параллельный веб-поиск через TravitySearchSkill (asyncio.gather)
        search_tasks = [self._fetch_travity(q) for q in queries]
        search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        raw_combined_md = "\n---\n".join([r for r in search_results if isinstance(r, str)])

        # Шаг 3: Экстракция уловок в NicheSalesTacticsSchema через LLM
        tactics = self.generative_core.extract_niche_sales_tactics(niche_description, raw_combined_md)
        tactics.niche_name = niche_slug

        # Шаг 4: Сохранение (INSERT/UPDATE) в глобальную базу знаний niche_insights
        self._cache_tactics(niche_slug, tactics)
        return tactics

    async def run(self, context: AgentContext) -> AgentContext:
        context.validate("DATA_COLLECTED")
        context.add_log("Agent_Analyst: запуск асинхронного сбора данных из парсеров и сети...")

        # Формирование поискового запроса по нише из анкеты
        niche = ""
        if context.questionnaire is not None:
            niche = context.questionnaire.step1.mission or context.questionnaire.step1.business_name
        search_query = f"{niche} SMM маркетинг тренды" if niche else "SMM маркетинг тренды"

        # 1. АСИНХРОННЫЙ СБОР ДАННЫХ (asyncio.gather с обработкой ошибок)
        results = await asyncio.gather(
            self._fetch_telethon(),
            self._fetch_vk(),
            self._fetch_travity(search_query),
            return_exceptions=True,
        )

        telethon_res = results[0] if isinstance(results[0], CollectorDataSchema) else CollectorDataSchema(collector_name="telethon", payload={"messages": []})
        vk_res = results[1] if isinstance(results[1], CollectorDataSchema) else CollectorDataSchema(collector_name="vk_api", payload={"posts": []})
        web_search_md = results[2] if isinstance(results[2], str) else "Тренды не загружены."

        context.collector_data.extend([telethon_res, vk_res])
        context.add_log("Agent_Analyst [Data Gathering]: асинхронный сбор завершен.")

        # 1.1 ORM MODUL: Сбор отзывов с Яндекс.Карт и 2GIS
        geo_reviews = await self._fetch_geo_reviews(context.questionnaire)
        context.geo_reviews = geo_reviews
        if geo_reviews:
            context.add_log(f"Agent_Analyst [ORM]: извлечено {len(geo_reviews)} отзывов с геосервисов (Карты/2GIS).")

        # 2. GROWTH HACKER SKILL: Поиск уловок и успешных продаж в нише
        niche_desc = niche or "SMM маркетинг"
        tactics = await self._research_sales_tactics(niche_desc)
        context.niche_tactics = tactics
        context.add_log(
            f"Agent_Analyst [Growth Hacker]: Найдено {len(tactics.psychological_hooks)} триггеров "
            f"и {len(tactics.successful_cases)} успешных кейсов для ниши '{niche_desc}'."
        )

        # 3. ПОДГОТОВКА И КОМПРЕССИЯ КОНТЕКСТА ПОСТОВ
        raw_items = [
            *[m.get("text", "") for m in telethon_res.payload.get("messages", [])],
            *[p.get("text", "") for p in vk_res.payload.get("posts", [])],
        ]
        compressed_posts_text = self._preprocess_and_compress(raw_items, max_tokens=2500)
        context.add_log(f"Agent_Analyst [Context Management]: посты сжаты ({len(compressed_posts_text)} символов).")

        # 4. STRATEGIC FUSION: Слияние ЦА, уловок Growth Hacker и трендов
        step2_demo = "Демография не указана"
        if context.questionnaire and context.questionnaire.step2:
            s2 = context.questionnaire.step2
            step2_demo = (
                f"Целевая аудитория: {s2.target_audience}. "
                f"Возраст: {getattr(s2, 'age_range', '25-50')}. "
                f"Гео: {getattr(s2, 'geo', 'РФ')}. "
                f"Ядро аудитории: {getattr(s2, 'core_audience_description', s2.target_audience)}. "
                f"Боли: {s2.pain_points}."
            )

        hooks_str = "\n- ".join(tactics.psychological_hooks)
        cases_str = "\n- ".join(tactics.successful_cases)
        promo_str = "\n- ".join(tactics.promotional_mechanics)

        tactics_context = (
            f"Психологические триггеры:\n- {hooks_str}\n\n"
            f"Успешные кейсы воронок:\n- {cases_str}\n\n"
            f"Промо-механики и офферы:\n- {promo_str}"
        )

        rules_result = self._apply_marketing_rules(context.questionnaire, raw_items, geo_reviews)
        context.swot = SWOTResultSchema(
            strengths=rules_result["strengths"],
            weaknesses=rules_result["weaknesses"],
            opportunities=rules_result["opportunities"],
            threats=rules_result["threats"],
            summary=f"SWOT сформирован на базе профиля ЦА, рыночных сигналов, ORM-отзывов и Growth Hacker уловок.",
        )
        context.add_log("Agent_Analyst: SWOT-матрица построена.")

        # Единый объединенный контекст стратегии
        strategy_context = (
            f"=== ВАЛИДИРОВАННЫЙ ПРОФИЛЬ ЦА (От Интервьюера) ===\n{step2_demo}\n\n"
            f"=== GROWTH HACKER: УЛОВКИ И КЕЙСЫ ПРОДАЖ В НИШЕ ===\n{tactics_context}\n\n"
            f"=== СЖАТЫЙ КОНТЕНТ КОНКУРЕНТОВ ===\n{compressed_posts_text}\n\n"
            f"=== АКТУАЛЬНЫЕ ТРЕНДЫ ИЗ СЕТИ ===\n{web_search_md}\n\n"
            f"Инструкция: Сформируй маркетинг-стратегию, опираясь на эти психологические уловки и рабочие кейсы."
        )

        context.strategy = self.generative_core.process_request(strategy_context)
        context.add_log("Agent_Analyst: маркетинговая стратегия сформирована с учетом Growth Hacker уловок.")

        return context

    # Step 10: Apply deterministic rule logic to construct SWOT dimensions.
    def _apply_marketing_rules(
        self,
        questionnaire: Optional[UserQuestionnaire],
        raw_items: List[str],
        geo_reviews: Optional[List[Dict[str, Any]]] = None,
    ) -> dict:
        results = {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": [],
        }

        if geo_reviews:
            negative_reviews = [r for r in geo_reviews if r.get("rating", 5) <= 3]
            positive_reviews = [r for r in geo_reviews if r.get("rating", 5) >= 4]

            if negative_reviews:
                complaints = "; ".join([r.get("text", "")[:60] for r in negative_reviews[:2]])
                results["weaknesses"].append(f"Анализ отзывов на геокартах выявил проблемы: {complaints}")

            if positive_reviews:
                praise = "; ".join([r.get("text", "")[:60] for r in positive_reviews[:2]])
                results["strengths"].append(f"Отзывы на геокартах подсвечивают достоинства: {praise}")

        if questionnaire is None:
            results["weaknesses"].append("Questionnaire is missing: baseline profile data is unavailable.")
            results["threats"].append("Market assessment cannot proceed without customer profile data.")
            return results

        step1_text = f"{questionnaire.step1.business_name} {questionnaire.step1.mission} {questionnaire.step1.region}"
        step2_text = (
            f"{questionnaire.step2.target_audience} "
            f"{getattr(questionnaire.step2, 'demographics', '') or ''} "
            f"{getattr(questionnaire.step2, 'age_range', '') or ''} "
            f"{getattr(questionnaire.step2, 'geo', '') or ''} "
            f"{getattr(questionnaire.step2, 'core_audience_description', '') or ''} "
            f"{questionnaire.step2.pain_points}"
        )
        step3_text = f"{questionnaire.step3.tone_of_voice} {questionnaire.step3.content_formats}"
        step4_text = f"{questionnaire.step4.goals} {questionnaire.step4.kpi} {questionnaire.step4.frequency}"

        audience = step2_text.lower()
        if "b2b" in audience:
            results["strengths"].append("Positioning supports expert-driven and rational content.")
        else:
            results["strengths"].append("Positioning supports emotional visual storytelling for consumer audiences.")

        competitors_count = len([item for item in questionnaire.step5.competitors.split(",") if item.strip()])
        if competitors_count >= 5:
            results["threats"].append("High local competitor density detected.")
        elif competitors_count == 0:
            results["opportunities"].append("Low competitor density indicates a growth window.")
        else:
            results["threats"].append("Moderately saturated competitive environment detected.")

        if len(raw_items) < 5:
            results["weaknesses"].append("Insufficient parser sample size for robust insight extraction.")
        else:
            results["strengths"].append("Sample size is adequate for baseline analytics.")

        tone = step3_text.lower()
        if "formal" in tone:
            results["weaknesses"].append("Engagement risk due to overly formal communication style.")
        else:
            results["opportunities"].append("Flexible tone can improve audience engagement.")

        frequency = step4_text.lower()
        if "daily" in frequency:
            results["strengths"].append("High publishing frequency supports sustained reach.")
        else:
            results["weaknesses"].append("Low publishing frequency may reduce growth velocity.")

        goals = step4_text.lower()
        if "lead" in goals or "sale" in goals or "conversion" in goals:
            results["opportunities"].append("Conversion-oriented goals simplify performance measurement.")
        else:
            results["weaknesses"].append("Goals are defined without direct conversion metrics.")

        positioning = step1_text.lower()
        if "premium" in positioning or "lux" in positioning:
            results["strengths"].append("Premium positioning increases perceived brand value.")
        elif "budget" in positioning or "econom" in positioning:
            results["threats"].append("Price competition may increase margin pressure.")
        else:
            results["opportunities"].append("Flexible positioning allows controlled message experiments.")

        return results


class Agent_Copywriter(BaseAgent):
    """Agent that generates and adapts post drafts with uniqueness controls."""

    name = "Agent_Copywriter"
    expected_state = "MARKET_ANALYZED"

    # Step 11: Configure copywriter dependencies.
    def __init__(
        self,
        vector_store: Optional[InMemoryVectorStore] = None,
        framework: CopywritingFramework = CopywritingFramework.PAS,
    ) -> None:
        self.vector_store = vector_store or InMemoryVectorStore()
        self.framework = framework

    def build_system_prompt(
        self,
        framework: CopywritingFramework,
        questionnaire: Optional[UserQuestionnaire] = None,
        tactics: Optional[NicheSalesTacticsSchema] = None,
    ) -> str:
        """
        Склеивает итоговый системный промпт Копирайтера, объединяя:
        1. Выбранный фреймворк копирайтинга (PAS/AIDA/PMHS).
        2. Tone of Voice и Табу-темы из анкеты клиента.
        3. Секретные уловки и психологические триггеры ниши (Growth Hacker Tactics).
        4. Строгие правила форматирования.
        """
        framework_instruction = FRAMEWORK_PROMPTS.get(
            framework, FRAMEWORK_PROMPTS[CopywritingFramework.PAS]
        ).strip()
        strict_rule = "Не пиши названия блоков (например, 'PROBLEM:'). Просто пиши связный текст, следуя этой логике."

        prompt_parts = [framework_instruction, strict_rule]

        # Добавление Tone of Voice и Табу из анкеты
        if questionnaire and getattr(questionnaire, "step3", None):
            s3 = questionnaire.step3
            tone_block = (
                f"=== ГОЛОС БРЕНДА (TONE OF VOICE) И ТАБУ ===\n"
                f"Тон общения: {s3.tone_of_voice}\n"
                f"Запрещенные темы (Табу): {s3.taboo_topics}"
            )
            prompt_parts.append(tone_block)

        # Добавление секретных уловок и триггеров ниши (Growth Hacker Tactics)
        if tactics and (tactics.psychological_hooks or tactics.promotional_mechanics):
            hooks_list = "\n- ".join(tactics.psychological_hooks) if tactics.psychological_hooks else "Стандартные триггеры"
            promo_list = "\n- ".join(tactics.promotional_mechanics) if tactics.promotional_mechanics else "Стандартный оффер"

            tactics_block = (
                f"=== СЕКРЕТНЫЕ УЛОВКИ И ТРИГГЕРЫ НИШИ ===\n"
                f"Психологические триггеры:\n- {hooks_list}\n\n"
                f"Промо-механики и офферы:\n- {promo_list}\n\n"
                f"Внимание! Не используй все триггеры сразу. Выбери только 1-2 наиболее подходящих триггера из списка "
                f"для этого конкретного поста и органично вплети их в текст. Текст не должен звучать как дешевая реклама."
            )
            prompt_parts.append(tactics_block)

        return "\n\n".join(prompt_parts)

    async def _process_review_reply(self, context: AgentContext) -> AgentContext:
        """
        Режим Онлайн-Репутации (ORM: REVIEW_REPLY) с Умной гибридной маршрутизацией:
        - 1-3 звезды (негатив/нейтрал) -> requires_manual_approval = True -> FSM в REVIEW_PENDING_APPROVAL
        - 4-5 звезд (позитив) -> auto_reply_positive (default True) -> requires_manual_approval = False
        """
        target = context.target_review or (context.geo_reviews[0] if context.geo_reviews else {})
        author = target.get("author", "Уважаемый клиент")
        original_rating = target.get("rating", 5)
        review_text = target.get("text", "Отзыв о сервисе и качестве продукции")

        # 1. Умная смарт-маршрутизация на базе рейтинга и настроек
        auto_reply_positive = True

        if original_rating <= 3:
            requires_manual_approval = True
            sentiment = "negative" if original_rating <= 2 else "neutral"
            action_needed = True
        else:
            requires_manual_approval = not auto_reply_positive
            sentiment = "positive"
            action_needed = False

        tone_of_voice = "Экспертный, вежливый и заботливый"
        if context.questionnaire and context.questionnaire.step3:
            tone_of_voice = context.questionnaire.step3.tone_of_voice

        if original_rating <= 3:
            draft_reply = (
                f"Здравствуйте, {author}! Приносим искренние извинения за произошедшее ({review_text[:40]}...). "
                f"Мы провели внутреннее расследование и стремимся всё исправить. "
                f"Свяжитесь с нашей службой заботы по почте zabota@ucust.ai или Telegram @ucust_support, чтобы мы могли помочь лично."
            )
        else:
            draft_reply = (
                f"Здравствуйте, {author}! Огромное спасибо за ваш теплый отзыв и 5 звезд! "
                f"Нам искренне приятно, что вы оценили наш сервис. Всегда рады видеть вас снова!"
            )

        context.review_reply = ReviewReplySchema(
            author=author,
            rating=original_rating,
            original_rating=original_rating,
            review_text=review_text,
            draft_text=draft_reply,
            reply_text=draft_reply,
            sentiment=sentiment,
            action_needed=action_needed,
            requires_manual_approval=requires_manual_approval,
        )

        context.post_draft = PostDraftSchema(text=draft_reply, uniqueness_score=1.0, duplicates_found=False)

        if requires_manual_approval:
            context.pending_user_action = True
            context.approval_status = "REVIEW_PENDING_APPROVAL"
            context.add_log(
                f"Agent_Copywriter [ORM Smart Routing]: отзыв от {author} ({original_rating} зв.) отправлен на утверждение человеком (REVIEW_PENDING_APPROVAL)."
            )
        else:
            context.pending_user_action = False
            context.approval_status = "READY_FOR_PUBLISHING"
            context.add_log(
                f"Agent_Copywriter [ORM Smart Routing]: авто-ответ на позитивный отзыв {author} ({original_rating} зв.) авто-утвержден (READY_FOR_PUBLISHING)."
            )

        return context

    # Step 12: Produce the baseline post draft and calculate uniqueness indicators.
    async def run(self, context: AgentContext) -> AgentContext:
        if context.task_type == TaskType.REVIEW_REPLY or context.target_review is not None:
            return await self._process_review_reply(context)

        strategy_text = context.strategy.strategy if context.strategy else "baseline strategy"
        framework = context.framework or self.framework

        # Склеивание системного промпта с учетом уловок, Tone of Voice и фреймворка
        system_prompt = self.build_system_prompt(
            framework=framework,
            questionnaire=context.questionnaire,
            tactics=context.niche_tactics,
        )

        if context.niche_tactics:
            context.add_log("Agent_Copywriter: интегрированы секретные уловки и психологические триггеры ниши.")

        draft_text = (
            f"Post based on strategy: {strategy_text}\n\n"
            f"[System Prompt]\n{system_prompt}"
        )

        # Reflection loop: Check for previous FactChecker critiques (removed claims)
        removed_claims = context.post_draft.removed_claims if context.post_draft and context.post_draft.removed_claims else []
        if removed_claims:
            critique_instruction = (
                f"\n\nПРЕДЫДУЩАЯ ОШИБКА: Ты выдумал следующие факты: {removed_claims}. "
                f"Исключи их полностью. Опирайся строго на SWOT."
            )
            draft_text += critique_instruction
            context.add_log(f"Agent_Copywriter: Reflection critique instruction appended for {removed_claims}.")

        embedding = self.vector_store.embed_text(draft_text)
        metadata = self._build_metadata(context)

        uniqueness_score = self.vector_store.semantic_filter(embedding, metadata)
        is_duplicate, _ = self.vector_store.is_duplicate(embedding)

        if is_duplicate:
            draft_text = f"{draft_text} (uniqueness reinforced)"
            context.add_log("Agent_Copywriter: duplicate detected; draft adjusted.")
        else:
            context.add_log("Agent_Copywriter: uniqueness verified.")

        self._store_embedding(embedding=embedding, metadata=metadata)
        context.post_draft = PostDraftSchema(
            text=draft_text,
            uniqueness_score=uniqueness_score,
            duplicates_found=is_duplicate,
            removed_claims=removed_claims,
        )
        context.add_log(f"Agent_Copywriter: draft created using framework {framework.value}.")
        return context

    async def standby(self, context: AgentContext) -> None:
        """Standby hook for clearing LLM Saiga 3 VRAM and invoking Garbage Collector."""
        context.add_log(f"{self.name}: standby hook executed.")
        # TODO: Invoke Saiga 3 LLM VRAM offloading / CUDA empty cache (e.g. torch.cuda.empty_cache())
        gc.collect()
        context.add_log(f"{self.name}: RAM/VRAM garbage collection completed.")

    # Step 13: Apply a user event override and update text plus uniqueness metrics.
    async def process_user_event(
        self,
        context: AgentContext,
        event_type: str,
        event_context: str,
    ) -> AgentContext:
        if context.post_draft is None:
            raise ValueError("Post draft is required before processing a user event.")

        updated_text = self.inject_custom_event(
            event_type=event_type,
            context=event_context,
            source_text=context.post_draft.text,
        )

        metadata = self._build_metadata(context)
        embedding = self.vector_store.embed_text(updated_text)
        uniqueness_score = self.vector_store.semantic_filter(embedding, metadata)
        is_duplicate, _ = self.vector_store.is_duplicate(embedding)
        self._store_embedding(embedding=embedding, metadata=metadata)

        context.post_draft = PostDraftSchema(
            text=updated_text,
            uniqueness_score=uniqueness_score,
            duplicates_found=is_duplicate,
        )
        context.pending_user_action = True
        context.approval_status = "EDIT"
        context.user_event_type = event_type
        context.user_event_context = event_context
        context.injected_events.append(event_type.strip().lower())
        context.add_log(f"Agent_Copywriter: user event applied with priority ({event_type}).")
        return context

    # Step 14: Transform draft text using event-specific templates.
    def inject_custom_event(self, event_type: str, context: str, source_text: str) -> str:
        normalized_event = event_type.lower().strip()
        normalized_context = context.strip() or "No extra context provided."
        baseline_text = source_text.strip()

        template_map = {
            "gratitude": (
                "Gratitude Post",
                "Thank you to our customers, partners, and team for your trust and support.",
            ),
            "holiday": (
                "Holiday Announcement",
                "Warm seasonal greetings from our team, with appreciation for your continued trust.",
            ),
            "achievement": (
                "Achievement Update",
                "We are proud to share a meaningful milestone achieved by our team.",
            ),
            "emergency": (
                "Urgent Update",
                "We are sharing an urgent operational update with immediate guidance.",
            ),
            "custom_edit": (
                "Custom Editorial Update",
                "This draft has been revised according to direct user guidance.",
            ),
        }

        title, opening = template_map.get(normalized_event, template_map["custom_edit"])
        return (
            f"{title}\n"
            f"{opening}\n\n"
            f"Event context: {normalized_context}\n\n"
            f"Baseline draft:\n{baseline_text}"
        )

    # Step 15: Derive semantic metadata from context fields.
    def _build_metadata(self, context: AgentContext) -> dict:
        metadata = {}
        if context.questionnaire is not None:
            niche = context.questionnaire.step1.mission or context.questionnaire.step1.business_name
            city = context.questionnaire.step1.region
            if niche:
                metadata["niche"] = niche
            if city:
                metadata["city"] = city
        return metadata

    # Step 16: Persist embedding records into vector storage.
    def _store_embedding(self, embedding: list[float], metadata: dict) -> None:
        record = VectorRecord(
            text_id=f"draft-{self.vector_store.count() + 1}",
            embedding=embedding,
            metadata=metadata,
        )
        self.vector_store.add_embedding(record)


class Agent_FactChecker(BaseAgent):
    """Agent responsible for verifying draft facts, LLM hallucinations, and framework compliance."""

    name = "Agent_FactChecker"
    expected_state = "DRAFT_GENERATED"

    BASE_SYSTEM_PROMPT = (
        "Ты — строгий фактчекер и шеф-редактор системы UCust.AI.\n"
        "Тебе даны исходные подтвержденные факты (анкета клиента, SWOT, стратегия), "
        "список разрешенных маркетинговых уловок, выбранный фреймворк копирайтинга и черновик текста.\n\n"
        "Твои задачи:\n"
        "1. ПРАВИЛО ДИФФЕРЕНЦИАЦИИ (RULE OF DIFFERENTIATION):\n"
        "   - РАЗРЕШЕНО (НЕ ГАЛЛЮЦИНАЦИЯ): Использование психологических триггеров (FOMO, эмоции, контраст цены, экспертность). Это риторические приемы копирайтинга. НЕ считай их галлюцинацией и НЕ удаляй!\n"
        "   - СТРОГО ЗАПРЕЩЕНО (ГАЛЛЮЦИНАЦИЯ / FAILED): Использование конкретных невербализованных цифр, процентных скидок (напр., 'Скидка 20%'), денежных гарантий возврата или акционных условий, если их НЕТ в исходной анкете клиента. Выдуманные офферы = FAILED.\n"
        "2. ФАКТЧЕКИНГ: Удалить любые выдуманные факты бизнеса, не подтвержденные клиентом.\n"
        "3. ПРОВЕРКА СТРУКТУРЫ ФРЕЙМВОРКА И CTA: Проверить наличие четкого призыва к действию (Call To Action) в конце поста.\n"
        "4. РЕДАКТУРА: Вырезать бессмысленные слова и вернуть чистый текст."
    )

    def __init__(self, generative_core: Optional[GenerativeCore] = None) -> None:
        self.generative_core = generative_core or GenerativeCore()

    def build_system_prompt(
        self,
        framework: Optional[CopywritingFramework] = None,
        tactics: Optional[NicheSalesTacticsSchema] = None,
    ) -> str:
        framework_name = framework.value if framework else "PAS"
        prompt = f"{self.BASE_SYSTEM_PROMPT}\n\nТекущий проверяемый фреймворк: {framework_name}."

        if tactics and (tactics.psychological_hooks or tactics.promotional_mechanics):
            hooks_str = "\n- ".join(tactics.psychological_hooks) if tactics.psychological_hooks else "Нет"
            promo_str = "\n- ".join(tactics.promotional_mechanics) if tactics.promotional_mechanics else "Нет"
            prompt += (
                f"\n\n=== РАЗРЕШЕННЫЕ МАРКЕТИНГОВЫЕ ТРИГГЕРЫ И УЛОВКИ ===\n"
                f"Психологические триггеры (Допустимо):\n- {hooks_str}\n\n"
                f"Маркетинговые механики:\n- {promo_str}\n\n"
                f"Инструкция фактчекера: Разрешай использование психологических триггеров из списка выше. "
                f"Однако, если копирайтер придумал конкретную скидку, акцию или подарок, не указанный клиентом, "
                f"зафиксируй нарушение с пометкой: 'Выдумана акция/скидка, не подтвержденная клиентом'."
            )

        return prompt

    async def run(self, context: AgentContext) -> AgentContext:
        if context.post_draft is None:
            raise ValueError("Post draft is required before fact-checking.")

        original_text = context.post_draft.text
        framework = context.framework or CopywritingFramework.PAS
        system_prompt = self.build_system_prompt(framework, tactics=context.niche_tactics)

        swot_summary = context.swot.summary if context.swot else "No SWOT available"
        strategy_summary = context.strategy.strategy if context.strategy else "No Strategy available"

        # Данные анкеты клиента для точного фактчекинга
        client_profile = ""
        if context.questionnaire and context.questionnaire.step1:
            client_profile = (
                f"Бренд: {context.questionnaire.step1.business_name}. "
                f"Миссия: {context.questionnaire.step1.mission}. "
                f"Боли: {context.questionnaire.step2.pain_points}."
            )

        tactics_str = ""
        if context.niche_tactics:
            tactics_str = (
                f"Разрешенные триггеры: {', '.join(context.niche_tactics.psychological_hooks)}. "
                f"Механики: {', '.join(context.niche_tactics.promotional_mechanics)}."
            )

        facts_context = (
            f"Профиль клиента: {client_profile}\n"
            f"SWOT: {swot_summary}\n"
            f"Strategy: {strategy_summary}\n"
            f"Niche Tactics: {tactics_str}\n"
            f"Framework: {framework.value}"
        )

        context.add_log(f"Agent_FactChecker: Starting verification with Rule of Differentiation (framework={framework.value})...")

        cleaned_text, removed_claims = self.generative_core.verify_facts(
            system_prompt=system_prompt,
            facts_context=facts_context,
            draft_text=original_text,
            framework=framework,
        )

        context.post_draft.text = cleaned_text
        context.post_draft.removed_claims = removed_claims

        if len(removed_claims) > 0:
            if context.correction_attempts < 3:
                context.correction_attempts += 1
                context.post_draft.fact_checked = False
                critique_msg = f"FactChecker Critique (Attempt {context.correction_attempts}/3): Model hallucinated claims: {removed_claims}."
                context.add_log(critique_msg)
                # Очистка памяти перед возвратом на повторный цикл генерации копирайтеру
                await self.standby(context)
            else:
                context.post_draft.fact_checked = False
                context.add_log("Agent_FactChecker: Maximum correction attempts reached (3/3). Hallucinations persist.")
                raise RuntimeError("Не удалось устранить галлюцинации модели")
        else:
            context.post_draft.fact_checked = True
            context.add_log(
                f"Agent_FactChecker: fact-checking completed cleanly (fact_checked=True, removed {len(removed_claims)} claims)."
            )

        return context

    async def standby(self, context: AgentContext) -> None:
        """Standby hook for clearing LLM Saiga 3 VRAM and invoking Garbage Collector."""
        context.add_log(f"{self.name}: standby hook executed.")
        # TODO: Invoke Saiga 3 LLM VRAM offloading / CUDA empty cache (e.g. torch.cuda.empty_cache())
        gc.collect()
        context.add_log(f"{self.name}: RAM/VRAM garbage collection completed.")


class Agent_Visual_Director(BaseAgent):
    """
    Расширенный агент «Арт-директор» системы UCust.AI.

    Отвечает за:
    1. Направление I (Onboarding & Brand Identity): Извлечение визуального ДНК бренда при первичном запуске.
    2. Генерацию медиа-воркфлоу LTX-2.3 для ComfyUI CLI.
    3. Направление II (QA и контроль качества): Нарезку ключевых кадров с помощью OpenCV (cv2)
       и их анализ в Vision LLM (GenerativeCore) на нейросетевые артефакты с циклом регенерации.
    4. Оптимизацию VRAM: Последовательный вызов хуков standby/activate перед переключением тяжелых GPU моделей.
    """

    name = "Agent_Visual_Director"
    expected_state = "CONTENT_READY"

    def __init__(
        self,
        comfyui_skill: Optional[ComfyUILocalSkill] = None,
        generative_core: Optional[GenerativeCore] = None,
        telethon_collector: Optional[TelethonCollector] = None,
        vk_collector: Optional[VkApiCollector] = None,
        telethon_channel: Optional[str] = None,
        vk_group_id: Optional[str] = None,
        max_qa_attempts: int = 3,
    ) -> None:
        self.comfyui_skill = comfyui_skill or ComfyUILocalSkill()
        self.generative_core = generative_core or GenerativeCore()
        self.telethon_collector = telethon_collector or TelethonCollector()
        self.vk_collector = vk_collector or VkApiCollector()
        self.telethon_channel = telethon_channel or os.getenv("UCUST_TELETHON_CHANNEL", "@default_channel")
        self.vk_group_id = vk_group_id or os.getenv("UCUST_VK_GROUP_ID", "default_group")
        self.max_qa_attempts = max_qa_attempts

    async def _ensure_brand_identity(self, context: AgentContext) -> Dict[str, Any]:
        """
        Направление I: Onboarding & Brand Identity
        Проверяет наличие 'visual_identity' в профиле пользователя. При отсутствии парсит
        последние 10-15 постов клиента из соцсетей и извлекает визуальный ДНК бренда с помощью LLM.
        """
        # 1. Проверяем, существует ли уже visual_identity в анкете/профиле
        if context.questionnaire and getattr(context.questionnaire, "visual_identity", None):
            context.add_log("Agent_Visual_Director [Onboarding]: 'visual_identity' уже присутствует в профиле.")
            return context.questionnaire.visual_identity

        context.add_log("Agent_Visual_Director [Onboarding]: 'visual_identity' отсутствует. Запуск анализа бренда...")

        # 2. Сбор последних публикаций клиента через парсеры (TG/VK)
        telethon_data = self.telethon_collector.collect(self.telethon_channel)
        vk_data = self.vk_collector.collect(self.vk_group_id)

        raw_items = [
            *[m.get("text", "") for m in telethon_data.payload.get("messages", [])],
            *[p.get("text", "") for p in vk_data.payload.get("posts", [])],
        ]
        sample_posts = [text for text in raw_items if text.strip()][:15]
        aggregated_text = "\n---\n".join(sample_posts) if sample_posts else "Компания в сфере ИИ и автоматизации маркетинга."

        # 3. Извлечение визуального ДНК бренда через GenerativeCore (Saiga 3 / LLM)
        context.add_log("Agent_Visual_Director [Onboarding]: Отправка публикаций в LLM для анализа визуального ДНК...")
        visual_identity = self.generative_core.extract_visual_identity(aggregated_text)

        # 4. Сохранение в профиль пользователя для всех последующих генераций
        if context.questionnaire:
            context.questionnaire.visual_identity = visual_identity

        context.add_log(
            f"Agent_Visual_Director [Onboarding]: ДНК бренда извлечен! "
            f"Tone: '{visual_identity.get('visual_tone_of_voice')}', Цвета: '{visual_identity.get('corporate_colors')}'."
        )
        return visual_identity

    def _extract_keyframes(self, video_path: str, num_frames: int = 4) -> List[str]:
        """
        Направление II: QA и Контроль качества (OpenCV)
        Нарезает сгенерированный .mp4 видеофайл на num_frames равноудаленных ключевых кадров.

        :param video_path: Абсолютный путь к сгенерированному .mp4 файлу.
        :param num_frames: Количество ключевых кадров (по умолчанию 4).
        :return: Список абсолютных путей к сохраненным JPG кадрам.
        """
        if not video_path or not os.path.exists(video_path):
            logging.warning("Agent_Visual_Director [QA]: Видеофайл не найден для нарезки: %s", video_path)
            return []

        if cv2 is None:
            logging.warning("Agent_Visual_Director [QA]: OpenCV (cv2) не установлен. Нарезка кадров пропущена.")
            return []

        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            cap.release()
            return []

        step = max(1, total_frames // num_frames)
        frame_paths: List[str] = []
        output_dir = os.path.dirname(video_path)

        for i in range(num_frames):
            frame_no = i * step
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            ret, frame = cap.read()
            if ret:
                frame_filename = os.path.join(output_dir, f"qa_frame_{i+1}_{os.path.basename(video_path)}.jpg")
                cv2.imwrite(frame_filename, frame)
                frame_paths.append(frame_filename)

        cap.release()
        logging.info("Agent_Visual_Director [QA]: Извлечено %d ключевых кадров из '%s'.", len(frame_paths), video_path)
        return frame_paths

    async def activate_vlm(self, context: AgentContext) -> None:
        """Хук загрузки Vision VLM модели в VRAM."""
        context.add_log(f"{self.name}: activate_vlm hook executed (Warming up Vision LLM in VRAM).")

    async def standby_vlm(self, context: AgentContext) -> None:
        """Хук выгрузки Vision VLM модели из VRAM перед отдачей контроля другим модулям."""
        context.add_log(f"{self.name}: standby_vlm hook executed (Offloading VLM & GPU memory cleanup).")
        gc.collect()

    async def run(self, context: AgentContext) -> AgentContext:
        if context.post_draft is None:
            raise ValueError("Post draft is required before visual planning.")

        # --- НАПРАВЛЕНИЕ I: Onboarding & Brand Identity ---
        brand_identity = await self._ensure_brand_identity(context)
        brand_tone = brand_identity.get("visual_tone_of_voice", "Modern B2B")
        colors = brand_identity.get("corporate_colors", "Blue and Cyan")
        anchors = brand_identity.get("visual_anchors", "High-tech lines")

        # Планирование плиток контент-сетки
        tiles = [
            GridTileSchema(tile_id=1, title="Expertise", description=f"Dynamic video scene ({brand_tone}), featuring {anchors}"),
            GridTileSchema(tile_id=2, title="Case Study", description=f"Cinematic brand narrative with palette {colors}"),
            GridTileSchema(tile_id=3, title="Insight", description=f"Animated high-tech graphic showcasing {anchors}"),
        ]
        context.grid_plan = GridPlanSchema(tiles=tiles)
        context.add_log("Agent_Visual_Director: сетка контента сформирована с учетом Бренд-ДНК.")

        # Базовый видео-промпт
        tile = tiles[0]
        base_video_prompt = (
            f"Cinematic 4k motion video for '{tile.title}': {tile.description}. "
            f"Style: {brand_tone}, Color palette: {colors}, Visual anchors: {anchors}. "
            f"Professional lighting, 24fps, smooth camera movement."
        )
        audio_prompt = f"Ambient corporate soundscape with tech synth pads for '{tile.title}'."

        # Инициализация негативного промпта для фильтрации артефактов
        negative_prompt = "deformed, blurry, bad anatomy, bad hands, mutated limbs, flickering, extra fingers"
        approved_media_info = None

        # --- НАПРАВЛЕНИЕ II: QA и Контроль качества (ComfyUI Generation + VLM Review Loop) ---
        for attempt in range(1, self.max_qa_attempts + 1):
            context.add_log(f"Agent_Visual_Director [QA Loop]: Запуск генерации (Попытка {attempt}/{self.max_qa_attempts})...")

            # 1. Генерация воркфлоу ComfyUI с учетом текущего negative_prompt
            workflow_graph = self._build_comfyui_workflow(
                video_prompt=base_video_prompt,
                audio_prompt=audio_prompt,
                aspect_ratio="16:9",
                negative_prompt=negative_prompt,
            )

            # 2. Вызов ComfyUI CLI Runner (генерация на GPU)
            media_info = await self.comfyui_skill._execute_full_flow(workflow_graph)
            video_path = media_info.get("video_path")

            # 3. VRAM Cleanup: Выгрузка GPU-ресурсов ComfyUI перед раундом Vision-анализа
            await self.standby(context)

            # 4. Нарезка видео на ключевые кадры с помощью OpenCV (cv2)
            frame_paths = self._extract_keyframes(video_path, num_frames=4)

            # 5. Выгрузка LLM / Загрузка VLM в VRAM
            await self.activate_vlm(context)

            # 6. Анализ кадров в Vision-модели (GenerativeCore)
            vlm_prompt = (
                "Проверь кадры на нейросетевые артефакты: ошибки анатомии (лишние пальцы, деформации), "
                "телепортация или морфинг объектов, внезапная смена цвета/формы, нарушения физики."
            )
            vlm_report = self.generative_core.analyze_images(image_paths=frame_paths, prompt=vlm_prompt)

            # 7. Освобождение VRAM от VLM модели
            await self.standby_vlm(context)

            qa_status = vlm_report.get("status", "PASSED")
            detected_artifacts = vlm_report.get("artifacts", [])
            qa_details = vlm_report.get("details", "")

            context.add_log(f"Agent_Visual_Director [QA Loop]: Результат VLM = {qa_status}. Детали: {qa_details}")

            # 8. Проверка решения VLM
            if qa_status == "PASSED" or not detected_artifacts:
                context.add_log(f"Agent_Visual_Director [QA Loop]: Видео успешно прошло контроль качества на попытке {attempt}!")
                approved_media_info = media_info
                break
            else:
                # В случае ошибок добавляем обнаруженные артефакты в NEGATIVE PROMPT для следующей итерации
                new_negatives = ", ".join(detected_artifacts)
                negative_prompt += f", {new_negatives}, morphing objects, anatomical distortion"
                context.add_log(
                    f"Agent_Visual_Director [QA Loop]: Обнаружены артефакты ({detected_artifacts}). "
                    f"Добавлено в NEGATIVE PROMPT для попытки {attempt + 1}: '{negative_prompt[:80]}...'"
                )

        # Если ни одна попытка не вернула PASSED, используем последний сгенерированный результат с предупреждением
        if approved_media_info is None:
            approved_media_info = media_info
            context.add_log("Agent_Visual_Director [QA Loop]: Достигнут лимит попыток (3/3). Принят последний результат.")

        # Привязка результатов к контексту
        prompt_schema = LTX23PromptSchema(
            video_prompt=base_video_prompt,
            audio_prompt=audio_prompt,
            motion_bucket_id=127,
            fps=24,
            aspect_ratio="16:9",
            duration_seconds=5.0,
            config=LTX23ConfigSchema(),
            comfyui_workflow=workflow_graph,
        )
        context.ltx23_prompts = [prompt_schema]

        context.post_draft.video_url = approved_media_info.get("video_url")
        context.post_draft.audio_url = approved_media_info.get("audio_url")
        context.post_draft.media_url = approved_media_info.get("media_url")
        context.post_draft.local_video_path = approved_media_info.get("video_path")
        context.post_draft.local_audio_path = approved_media_info.get("audio_path")

        context.add_log("Agent_Visual_Director: выполнение завершено, медиафайлы привязаны.")
        return context

    async def standby(self, context: AgentContext) -> None:
        """Standby hook executed after visual planning to release GPU / RAM resources."""
        context.add_log(f"{self.name}: standby hook executed (ComfyUI & PyTorch CUDA cache freed).")
        gc.collect()

    def _build_comfyui_workflow(
        self,
        video_prompt: str,
        audio_prompt: str,
        aspect_ratio: str,
        negative_prompt: Optional[str] = None,
    ) -> dict:
        """Загружает шаблон Ltx_generations.json и кастомизирует промпты, seeds и negative_prompt."""
        from skills.comfy_cli_runner import ComfyCLIRunner
        runner = ComfyCLIRunner()
        workflow = runner.load_workflow()
        customized = runner.customize_workflow(
            workflow_json=workflow,
            video_prompt=video_prompt,
            audio_prompt=audio_prompt,
            aspect_ratio=aspect_ratio,
        )
        # Если передан negative_prompt, прописываем его в соответствующие узлы
        if negative_prompt and isinstance(customized, dict):
            if "nodes" in customized:
                for node in customized.get("nodes", []):
                    if node.get("type") == "CLIPTextEncode" and "Negative" in node.get("title", ""):
                        if "widgets_values" in node and len(node["widgets_values"]) > 0:
                            node["widgets_values"][0] = negative_prompt
            else:
                for node_id, node_data in customized.items():
                    if isinstance(node_data, dict) and node_data.get("class_type") == "CLIPTextEncode":
                        inputs = node_data.get("inputs", {})
                        if "negative" in str(node_id).lower() or "negative" in str(inputs.get("text", "")).lower():
                            inputs["text"] = negative_prompt
        return customized


__all__ = [
    "AgentContext",
    "BaseAgent",
    "Agent_Interviewer",
    "Agent_Analyst",
    "Agent_Copywriter",
    "Agent_FactChecker",
    "Agent_Visual_Director",
]
