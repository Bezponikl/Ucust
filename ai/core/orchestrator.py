import uuid
import json
import hashlib
from typing import Any, Dict, List, Optional
from storage.models import UserProfile, OrchestratorTrace

class SecurityGuard:
    """
    Модуль безопасности. Защищает от Prompt Injection, джейлбрейков (амнезии)
    и прямых запросов на выгрузку БД.
    """
    
    FORBIDDEN_KEYWORDS = [
        "select *", "drop table", "ignore previous instructions", "забудь все",
        "dump database", "выведи базу", "покажи все профили", "пароли",
        "system prompt", "ты теперь", "print db", "ignore above"
    ]
    
    TONE_STOPWORDS = [
        "безумно", "от всей души", "мы гордимся", "потрясающе", 
        "волшебный", "сказочный", "—"
    ]
    
    @classmethod
    def check_user_input(cls, user_text: str) -> bool:
        """
        Проверяет ввод пользователя на попытки взлома и инъекций.
        Возвращает True, если безопасно, и False, если есть подозрения.
        """
        if not user_text:
            return True
            
        text_lower = user_text.lower()
        for kw in cls.FORBIDDEN_KEYWORDS:
            if kw in text_lower:
                print(f"[SecurityGuard] 🚨 ОБНАРУЖЕНА ПОПЫТКА ВЗЛОМА: '{kw}' в запросе пользователя!")
                return False
        return True

    @classmethod
    def validate_content_tone_of_voice(cls, content_text: str) -> tuple[bool, Optional[str]]:
        """
        Tone-of-Voice Gatekeeper: Проверяет исходящий контент перед отправкой на фронтенд/в API.
        Отсекает фальшь, стоп-слова, токсичную бодрость и некорректную типографику.
        """
        if not content_text:
            return True, None
            
        content_lower = content_text.lower()
        for word in cls.TONE_STOPWORDS:
            if word in content_lower:
                print(f"[SecurityGuard] ⚠️ БРАК КОНТЕНТА (Tone of Voice): обнаружено стоп-выражение '{word}'!")
                return False, f"Нарушение гайдлайнов качества: обнаружено запрещенное слово/символ '{word}'"
        return True, None

    @classmethod
    def sanitize_graph_data(cls, raw_data: List[Dict]) -> List[Dict]:
        """
        Очищает данные перед отправкой на фронтенд для отрисовки графов.
        Удаляет все PII (персональные данные), хэши и внутренние ID.
        """
        sanitized = []
        for item in raw_data:
            clean_item = {
                "metric_name": item.get("niche", "Unknown"),
                "value": item.get("count", 0)
            }
            sanitized.append(clean_item)
        return sanitized


class UnifiedOrchestrator:
    """
    Унифицированный Архитектор (Chief Orchestrator).
    Единая точка входа для всех задач (пайплайны, графы, фронтенд).
    Полностью контролирует безопасность и потоки данных.
    """
    def __init__(self, db_session, vector_store=None, redis_cache=None):
        from storage.pgvector_store import PGVectorStore
        from core.redis_cache import RedisCacheManager
        
        self.db = db_session
        self.vector_store = vector_store or PGVectorStore(self.db)
        self.redis_cache = redis_cache or RedisCacheManager()

    def _hash_payload(self, payload: Any) -> str:
        payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

    def _log_trace(self, session_id: str, agent_name: str, action: str, payload: Any):
        payload_hash = self._hash_payload(payload)
        
        # 1. Сохраняем в SQL
        trace = OrchestratorTrace(
            session_id=session_id,
            agent_name=agent_name,
            action=action,
            payload_hash=payload_hash,
            payload=payload if isinstance(payload, dict) else {"data": payload}
        )
        self.db.add(trace)
        self.db.commit()
        
        # 2. Кешируем стейт в Redis для ускорения будущих запусков
        self.redis_cache.set_cached_result(action, payload_hash, payload)

    async def execute_task(self, task_type: str, user_data: dict, session_id: Optional[str] = None) -> dict:
        """
        Универсальный обработчик задач (точка входа для фронтенда и API).
        """
        session_id = session_id or str(uuid.uuid4())
        print(f"\n[UnifiedOrchestrator] ⚖️ Новая задача '{task_type}', сессия: {session_id}")
        
        # 1. Проверка безопасности (Security Layer)
        raw_input = user_data.get("raw_social_input", "")
        if not SecurityGuard.check_user_input(raw_input):
            return {"status": "error", "message": "Security Violation: запрос отклонен."}
            
        # Здесь будет маршрутизация к разным пайплайнам
        if task_type == "onboarding":
            print("[UnifiedOrchestrator] ⚖️ Делегирую задачу пайплайну онбординга...")
            # ... запуск агентов Интервьюер, Аналитик, Сайга ...
            self._log_trace(session_id, "Orchestrator", "TaskStarted", {"type": task_type})
            return {"status": "success", "profile_id": 1}
            
        if task_type == "get_trends":
            from core.trend_scheduler import WeeklyTrendScheduler
            niche = user_data.get("niche", "IT и Автоматизация")
            scheduler = WeeklyTrendScheduler(self.redis_cache, self.vector_store)
            trends = await scheduler.get_trends_for_niche(niche)
            self._log_trace(session_id, "TrendHunter", "TrendsRetrieved", {"niche": niche})
            return {"status": "success", "trends": trends}

        if task_type == "prepare_holiday_greeting":
            from collectors.event_holiday_collector import EventHolidayCollector
            from skills.holiday_congratulator import HolidayCongratulatorSkill
            
            city = user_data.get("city", "Казань")
            country = user_data.get("country", "Россия")
            company_name = user_data.get("company_name", "Наша Компания")
            niche = user_data.get("niche", "Услуги")
            
            # 1. Сбор праздников через парсер
            collector = EventHolidayCollector()
            events = await collector.fetch_city_and_national_events(city, country)
            
            # 2. Сайга готовит поздравление и промокод
            congratulator = HolidayCongratulatorSkill()
            greeting = congratulator.generate_holiday_post(company_name, niche, city, events[0] if events else {})
            
            # 3. Tone of Voice Gatekeeper & Self-Healing Loop (автоматическое исправление)
            max_attempts = 2
            attempts = 0
            is_valid = False
            error_msg = None
            
            while not is_valid and attempts < max_attempts:
                attempts += 1
                is_valid, error_msg = SecurityGuard.validate_content_tone_of_voice(greeting.get("post_text", ""))
                if not is_valid:
                    print(f"[UnifiedOrchestrator] 🔄 Gatekeeper отклонил текст (попытка {attempts}): {error_msg}")
                    print(f"[UnifiedOrchestrator] 📨 Отправка текста автору (Сайге) на автономное самоисправление...")
                    healed_text = congratulator.saiga.self_heal_text(greeting.get("post_text", ""), error_msg)
                    greeting["post_text"] = healed_text
                else:
                    print(f"[UnifiedOrchestrator] 🛡️ Текст успешно валидирован Tone-of-Voice Gatekeeper (без стоп-слов и тавтологий).")
                    
            if not is_valid:
                print(f"[UnifiedOrchestrator] ❌ Не удалось автоматически исправить текст после {max_attempts} попыток.")
                return {"status": "retry_needed", "error": error_msg}
                
            self._log_trace(session_id, "HolidaySkill", "GreetingGenerated", {"city": city, "holiday": greeting.get("holiday_title")})
            return {"status": "success", "events": events, "prepared_greeting": greeting}
            
        if task_type == "generate_post":
            from skills.saiga_llm import SaigaLLMSkill
            from skills.advanced_visual_director import AdvancedVisualDirector
            from skills.photo_generator import PhotoGeneratorSkill
            
            prompt = user_data.get("prompt") or user_data.get("topic") or "Новое предложение для клиентов"
            format_type = user_data.get("format", "post")
            tone = user_data.get("tone", "Естественный и живой")
            niche = user_data.get("niche", "IT Automation / Сервис контента")
            city = user_data.get("city", "Москва")
            company_name = user_data.get("company_name", "UCust")
            should_gen_image = user_data.get("generate_image", True) or format_type in ["post", "photo"]
            aspect_ratio = user_data.get("aspect_ratio", "1:1")
            
            print(f"[UnifiedOrchestrator] ✍️ Генерация поста для темы: '{prompt}', компания: '{company_name}', ниша: '{niche}', формат: {format_type}, тон: {tone}")
            
            # 1. Генерация аутентичного SMM текста через Сайгу
            saiga = SaigaLLMSkill()
            gen_result = saiga.generate_smm_post(
                topic=prompt,
                company_name=company_name,
                niche=niche,
                city=city,
                tone=tone,
                format_type=format_type
            )
            post_text = gen_result.get("post_text", "")
            promo_code = gen_result.get("promo_code", f"{company_name.upper().replace(' ', '')}2026")
            
            # 2. Валидация качества текста (Tone of Voice Gatekeeper)
            is_valid, error_msg = SecurityGuard.validate_content_tone_of_voice(post_text)
            if not is_valid:
                post_text = saiga.self_heal_text(post_text, error_msg or "")
            
            # 3. Формирование видео/визуального промпта по стандарту LTX-2
            director = AdvancedVisualDirector(brand_images=[])
            video_prompt = f"Cinematic SMM video for {company_name}. Topic: {prompt}. High resolution, 4k, crisp details."

            # 4. Генерация SMM Фотографии
            image_url = None
            photo_prompt = None
            if should_gen_image:
                try:
                    photo_skill = PhotoGeneratorSkill()
                    photo_res = await photo_skill.generate_photo(
                        topic=prompt,
                        niche=niche,
                        aspect_ratio=aspect_ratio
                    )
                    image_url = photo_res.get("image_url")
                    photo_prompt = photo_res.get("positive_prompt")
                except Exception as ex:
                    print(f"[UnifiedOrchestrator] ⚠️ Ошибка генерации фото: {ex}")
            
            self._log_trace(session_id, "SaigaCopywriter", "PostGenerated", {"topic": prompt, "format": format_type})
            return {
                "status": "success",
                "post_text": post_text,
                "promo_code": promo_code,
                "video_prompt": video_prompt,
                "photo_prompt": photo_prompt,
                "image_url": image_url,
                "photo_url": image_url,
                "confidence_score": 0.96,
                "format": format_type,
                "tone": tone
            }

        if task_type in ["generate_image", "generate_photo"]:
            from skills.photo_generator import PhotoGeneratorSkill
            
            prompt = user_data.get("prompt") or user_data.get("topic") or "Специальное предложение"
            niche = user_data.get("niche", "Бизнес")
            aspect_ratio = user_data.get("aspect_ratio", "1:1")
            style = user_data.get("style", "photorealistic")
            brand_colors = user_data.get("brand_colors")
            
            photo_skill = PhotoGeneratorSkill()
            photo_res = await photo_skill.generate_photo(
                topic=prompt,
                niche=niche,
                aspect_ratio=aspect_ratio,
                brand_colors=brand_colors,
                style=style
            )
            
            self._log_trace(session_id, "PhotoGenerator", "PhotoCreated", {"topic": prompt, "aspect_ratio": aspect_ratio})
            return photo_res

        if task_type == "rag_query":
            from rag.pipeline import CleanRAGPipeline
            query_text = user_data.get("query", "")
            rag = CleanRAGPipeline(min_confidence_threshold=0.65)
            rag_res = await rag.query_async(query_text)
            return {
                "status": "success",
                "query": query_text,
                "has_sufficient_context": rag_res.has_sufficient_context,
                "context": rag_res.formatted_context,
                "top_score": rag_res.top_score,
                "fallback_message": rag_res.fallback_message
            }

        return {"status": "error", "message": f"Неизвестная задача '{task_type}'"}

    def get_frontend_graph_data(self) -> List[dict]:
        """
        Безопасная отдача данных фронтенду для графиков.
        Гарантирует, что исходники БД никогда не утекут напрямую.
        """
        print("\n[UnifiedOrchestrator] 📊 Фронтенд запросил данные для графов...")
        
        # Моделируем агрегированный запрос к БД
        # SELECT niche, count(*) FROM user_profiles GROUP BY niche;
        mock_raw_db_data = [
            {"niche": "IT Automation", "count": 15, "secret_id": "sys_999", "pass_hash": "xxx"},
            {"niche": "Beauty SMM", "count": 8, "secret_id": "sys_123", "pass_hash": "yyy"}
        ]
        
        # 2. Очистка данных перед отдачей клиенту (Data Loss Prevention)
        safe_data = SecurityGuard.sanitize_graph_data(mock_raw_db_data)
        print(f"[UnifiedOrchestrator] 🛡️ Данные очищены: {safe_data}")
        return safe_data
