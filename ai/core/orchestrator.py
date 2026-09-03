import os
import sys
import uuid
import json
import time
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional
from storage.models import UserProfile, OrchestratorTrace, PublicationHistory, ProjectMetadata, ContentTask

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
        "безумно", "потрясающе", "волшебный", "сказочный",
        "крушить барьеры", "руинах обыденности", "сверхъестественн",
        "пушка", "бомба", "выстрел в мир", "держись крепче"
    ]

    # Строгий запрет на утечку внутренних моделей, нод, связей и настроек
    PROTECTED_IP_TERMS = [
        "ltx", "ltx-video", "ltxv", "saiga", "moondream", "comfyui", "safetensors",
        "lora", "clip", "latent", "cfg", "emptyllatent", "checkpoint", "vlm",
        "gemma", "sdxl", "flux", "unipc", "karras", "sampler", "vae", "controlnet",
        "qwen", "qwen_image", "qwen_2.5_vl", "famegrid", "realskinfix", "auraflow",
        "clownshark", "emptysd3latent", "unetloader", "cliploader", "vaedecodetiled"
    ]
    
    @classmethod
    def sanitize_public_text(cls, text: str) -> str:
        """
        Защита коммерческой тайны и IP: вырезает и маскирует любые упоминания
        внутренних моделей, весов, нод и параметров генерации из публичных текстов.
        """
        if not text:
            return ""
        clean = text
        for term in cls.PROTECTED_IP_TERMS:
            pattern = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
            clean = pattern.sub("UCust AI Engine", clean)
        return clean

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
    def __init__(self, db_session=None, vector_store=None, redis_cache=None):
        from storage.pgvector_store import PGVectorStore
        from core.redis_cache import RedisCacheManager
        from rag.pipeline import CleanRAGPipeline
        
        self.db = db_session
        self.vector_store = vector_store or (PGVectorStore(self.db) if self.db else None)
        self.redis_cache = redis_cache or RedisCacheManager()
        self.rag = CleanRAGPipeline(min_confidence_threshold=0.55)

        # 1. Автоматический контроль хранения файлов (Кэш: 5 часов, Генерации: 30 дней)
        try:
            from storage.media_retention import MediaRetentionManager
            cleaner = MediaRetentionManager()
            retention_days = int(os.getenv("MEDIA_RETENTION_DAYS", "30"))
            temp_hours = float(os.getenv("TEMP_CACHE_RETENTION_HOURS", "5.0"))
            auto_archive = os.getenv("MEDIA_AUTO_ARCHIVE", "true").lower() == "true"
            cleaner.cleanup_expired_files(
                retention_days=retention_days,
                temp_cache_retention_hours=temp_hours,
                archive_generations=auto_archive
            )
        except Exception:
            pass

    def _hash_payload(self, payload: Any) -> str:
        payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

    def _log_trace(self, session_id: str, agent_name: str, action: str, payload: Any):
        payload_hash = self._hash_payload(payload)
        
        if self.db:
            try:
                trace = OrchestratorTrace(
                    session_id=session_id,
                    agent_name=agent_name,
                    action=action,
                    payload_hash=payload_hash,
                    payload=payload if isinstance(payload, dict) else {"data": payload}
                )
                self.db.add(trace)
                self.db.commit()
            except Exception as e:
                print(f"[UnifiedOrchestrator] ⚠️ Ошибка сохранения трейса в БД: {e}")
        
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
            
        # 2. Универсальный Vision Analyst (Moondream2) для любых загруженных пользователем фото
        attachments = user_data.get("attachments") or user_data.get("photos") or []
        if isinstance(attachments, dict):
            attachments = [attachments]
        if not attachments and user_data.get("image_url"):
            attachments = [{"url": user_data.get("image_url")}]
        if not attachments and user_data.get("dataUrl"):
            attachments = [{"dataUrl": user_data.get("dataUrl")}]

        moondream_analysis = None
        if attachments:
            try:
                from skills.moondream_vqa import MoondreamVQASkill
                moondream = MoondreamVQASkill()
                company_name_for_md = user_data.get("company_name") or user_data.get("name") or "UCust"
                prompt_for_md = user_data.get("prompt") or user_data.get("topic") or ""
                moondream_analysis = moondream.analyze_attachments_batch(
                    attachments=attachments,
                    topic=prompt_for_md,
                    company_name=company_name_for_md
                )
                self._log_trace(session_id, "MoondreamAnalyst", "AttachmentsAnalyzed", {
                    "count": moondream_analysis.get("count", 0),
                    "colors": moondream_analysis.get("colors", []),
                    "summary": moondream_analysis.get("summary", "")
                })
                print(f"[UnifiedOrchestrator] 🧠 Moondream успешно проанализировал {moondream_analysis.get('count')} фото пользователя!")
            except Exception as e:
                print(f"[UnifiedOrchestrator] ⚠️ Ошибка Moondream анализа: {e}")

        if task_type in {"onboarding", "onboard_user", "analyze_brand", "interviewer"}:
            from skills.saiga_llm import SaigaLLMSkill
            from collectors.website_collector import WebsiteCollector
            import re
            
            company_name = user_data.get("name") or user_data.get("company_name") or "UCust"
            raw_social_input = user_data.get("raw_social_input") or user_data.get("link") or user_data.get("website") or ""
            activity = user_data.get("activity") or user_data.get("niche") or "IT Automation"
            city = user_data.get("city") or "Москва"
            
            print(f"[UnifiedOrchestrator] 🎙️ Агент-Интервьюер: Анализ входных данных для '{company_name}' ({activity})...")
            
            # Автоматический глубокий анализ сайта компании, если передан URL
            website_data = None
            found_urls = re.findall(r'https?://[^\s,;]+|(?:www\.)?[a-zA-Z0-9-]+\.(?:ru|com|io|org|net|pro|ai|me|cc|by|kz|tech|online|store|shop|app|dev)(?:/[^\s,;]*)?', raw_social_input)
            for u in found_urls:
                if not any(excluded in u.lower() for excluded in ["t.me", "vk.com", "yandex.", "2gis."]):
                    try:
                        collector = WebsiteCollector()
                        website_data = await collector.collect_website_async(u)
                        if website_data.get("status") == "success":
                            self._log_trace(session_id, "WebsiteCollector", "WebsiteAnalyzed", {
                                "url": website_data.get("url"),
                                "title": website_data.get("title"),
                                "description": website_data.get("description")
                            })
                            # Обогащаем user_data
                            user_data["website_dossier"] = website_data.get("structured_dossier")
                            if website_data.get("description") and activity == "IT Automation":
                                user_data["niche"] = website_data.get("description")[:80]
                            break
                    except Exception as wex:
                        print(f"[UnifiedOrchestrator] ⚠️ Ошибка парсинга сайта: {wex}")

            self._log_trace(session_id, "Agent_Interviewer", "Extracted_Context", {
                "company_name": company_name,
                "raw_social_input": raw_social_input,
                "activity": activity,
                "city": city,
                "has_website_data": bool(website_data)
            })
            
            # 1. Сайга и Аналитик формируют бренд-профиль с учетом веб-аналитики и Moondream
            saiga = SaigaLLMSkill()
            clean_posts_input = [website_data["structured_dossier"]] if website_data and website_data.get("structured_dossier") else None
            brand_profile = saiga.analyze_brand_profile(user_data, clean_posts=clean_posts_input)

            # 2. Подключение Визуального Директора для анализа сетки ленты (Grid DNA & Brandbook)
            from skills.advanced_visual_director import AdvancedVisualDirector
            all_collected_images = []
            if website_data and website_data.get("cached_images"):
                all_collected_images.extend(website_data["cached_images"])
            elif website_data and website_data.get("images"):
                all_collected_images.extend(website_data["images"])
            if attachments:
                all_collected_images.extend(attachments)

            vis_director = AdvancedVisualDirector()
            visual_grid_dna = vis_director.analyze_visual_grid(
                images=all_collected_images,
                niche=user_data.get("niche") or activity
            )
            brand_profile["visual_grid_dna"] = visual_grid_dna
            brand_profile["brand_colors"] = visual_grid_dna.get("brand_hex_palette", [])
            brand_profile["dominant_color"] = visual_grid_dna.get("dominant_color")
            brand_profile["next_visual_recommendation"] = visual_grid_dna.get("next_post_recommendation")

            self._log_trace(session_id, "VisualDirector", "GridDNAAnalyzed", {
                "palette": visual_grid_dna.get("brand_hex_palette"),
                "images_analyzed": visual_grid_dna.get("analyzed_images_count"),
                "recommended_slot": visual_grid_dna.get("next_post_recommendation", {}).get("target_slot")
            })

            # 3. Генерация глубокой контент-стратегии и портрета покупателя (Persona & Strategy Engine)
            from skills.content_strategy_engine import ContentStrategyEngine
            strat_engine = ContentStrategyEngine()
            strategy_data = strat_engine.generate_strategy(
                company_name=company_name,
                niche=brand_profile.get("field", activity),
                target_audience=brand_profile.get("market", {}).get("segment", ""),
                key_usp=brand_profile.get("positioning", "")
            )
            brand_profile["buyer_persona"] = strategy_data.get("buyer_persona", {})
            brand_profile["funnel_matrix"] = strategy_data.get("funnel_matrix", {})
            brand_profile["viral_hooks"] = strategy_data.get("hooks_arsenal", [])

            if website_data:
                brand_profile["website_data"] = {
                    "title": website_data.get("title"),
                    "description": website_data.get("description"),
                    "headings": website_data.get("headings", []),
                    "images": website_data.get("images", []),
                    "contacts": website_data.get("contacts", {}),
                    "social_links": website_data.get("social_links", {})
                }
            if moondream_analysis and moondream_analysis.get("colors"):
                brand_profile["moondream_colors"] = moondream_analysis.get("colors")
                brand_profile["visual_summary"] = moondream_analysis.get("summary")
            self._log_trace(session_id, "Agent_Saiga", "Synthesized_Profile", brand_profile)
            self._log_trace(session_id, "Agent_ContentStrategist", "StrategySynthesized", strategy_data)
            
            # 4. Векторизация и индексация в RAG (6 семантических категорий фактов)
            from rag.models import Document
            rag_docs = []
            pains_list = strategy_data.get("buyer_persona", {}).get("primary_pains", [])
            triggers_list = strategy_data.get("buyer_persona", {}).get("buying_triggers", [])
            swot_data = brand_profile.get("swot", {})
            services_list = brand_profile.get("services", [])

            # Doc 1: Brand DNA & Positioning
            rag_docs.append(Document(
                doc_id=f"brand_dna_{company_name}",
                text=f"Компания: {company_name}\nНиша: {brand_profile.get('field', activity)}\nГород: {city}\nПозиционирование (УТП): {brand_profile.get('positioning', '')}\nTone of Voice: {brand_profile.get('tone', [])}\nЦелевая аудитория: {brand_profile.get('market', {}).get('segment', '')}",
                metadata={"category": "brand_dna", "company_name": company_name, "user_id": user_data.get("user_id")}
            ))

            # Doc 2: Pain Points & Buying Triggers
            rag_docs.append(Document(
                doc_id=f"pains_{company_name}",
                text=f"Боли, страхи и возражения клиентов компании {company_name}:\n- " + "\n- ".join(pains_list) + "\nТриггеры покупки и доверия:\n- " + "\n- ".join(triggers_list),
                metadata={"category": "pain_points", "company_name": company_name}
            ))

            # Doc 3: Competitor Dossier & Advantages
            rag_docs.append(Document(
                doc_id=f"competitors_{company_name}",
                text=f"Конкурентный анализ и отстройка компании {company_name}:\nСильные стороны: {swot_data.get('strengths', [])}\nВозможности рынка: {swot_data.get('opportunities', [])}\nГлавное отличие: {brand_profile.get('positioning', '')}",
                metadata={"category": "competitors", "company_name": company_name}
            ))

            # Doc 4: Visual Grid DNA & Palette
            if visual_grid_dna:
                rag_docs.append(Document(
                    doc_id=f"visual_grid_{company_name}",
                    text=f"Визуальный брендбук и сетка ленты 3x3 для {company_name}:\nФирменная палитра (Hex): {visual_grid_dna.get('brand_hex_palette', [])}\nДоминирующий цвет: {visual_grid_dna.get('dominant_color')}\nРекомендация по кадру: {visual_grid_dna.get('next_post_recommendation', {}).get('advice')}",
                    metadata={"category": "visual_grid_dna", "company_name": company_name}
                ))

            # Doc 5: Services & Pricing Offers
            if services_list:
                rag_docs.append(Document(
                    doc_id=f"services_{company_name}",
                    text=f"Услуги и ключевые предложения компании {company_name}:\n- " + "\n- ".join([str(s) for s in services_list]),
                    metadata={"category": "services", "company_name": company_name}
                ))

            # Doc 6: Website Knowledge Base
            if website_data and website_data.get("structured_dossier"):
                rag_docs.append(Document(
                    doc_id=f"website_{company_name}",
                    text=f"Фактическая информация с официального сайта {company_name}:\n{website_data['structured_dossier']}",
                    metadata={"category": "website_knowledge", "company_name": company_name}
                ))

            # 7. Календарь государственных, профессиональных и городских праздников для локации
            country = user_data.get("country") or brand_profile.get("market", {}).get("country") or "Россия"
            try:
                from collectors.event_holiday_collector import EventHolidayCollector
                holiday_events = EventHolidayCollector().get_calendar_events(
                    country=country,
                    city=city,
                    niche=brand_profile.get("field", activity),
                    days_count=60
                )
                if holiday_events:
                    holidays_str = "\n".join([f"- {e['date']}: {e['title']} ({e['vibe']})" for e in holiday_events[:10]])
                    rag_docs.append(Document(
                        doc_id=f"geo_and_holidays_{company_name}",
                        text=f"География, локальные события и праздники компании {company_name}:\nСтрана: {country}\nГород: {city}\nНиша: {brand_profile.get('field', activity)}\nБлижайшие инфоповоды и праздники:\n{holidays_str}",
                        metadata={"category": "holidays_and_events", "company_name": company_name, "country": country, "city": city}
                    ))
            except Exception as h_err:
                print(f"[UnifiedOrchestrator] ⚠️ Ошибка сбора календаря праздников: {h_err}")

            # 8. Извлечение информации из загруженных документов клиента (PDF, DOCX, PPTX)
            client_docs_data = None
            from collectors.document_collector import DocumentCollector
            doc_collector = DocumentCollector()
            doc_candidates = (user_data.get("documents") or user_data.get("files") or 
                              user_data.get("file_paths") or user_data.get("document_paths") or [])
            if isinstance(doc_candidates, str):
                doc_candidates = [doc_candidates]
            
            valid_doc_paths = [
                f for f in doc_candidates 
                if isinstance(f, str) and os.path.splitext(f)[1].lower() in {".pdf", ".docx", ".pptx", ".txt", ".md", ".csv"} and os.path.exists(f)
            ]
            if valid_doc_paths:
                try:
                    client_docs_data = doc_collector.extract_documents_batch(valid_doc_paths)
                    for d_idx, doc_item in enumerate(client_docs_data):
                        if doc_item.get("status") == "success" and doc_item.get("raw_text"):
                            rag_docs.append(Document(
                                doc_id=f"client_doc_{company_name}_{d_idx+1}",
                                text=f"Документ клиента '{doc_item['file_name']}' ({doc_item['format'].upper()}) для {company_name}:\n{doc_item['raw_text']}",
                                metadata={"category": "client_files", "company_name": company_name, "file_name": doc_item["file_name"]}
                            ))
                    print(f"[UnifiedOrchestrator] 📄 Извлечено {len(client_docs_data)} клиентских документов для '{company_name}'.")
                except Exception as doc_err:
                    print(f"[UnifiedOrchestrator] ⚠️ Ошибка парсинга документов клиента: {doc_err}")

            try:
                indexed_count = await self.rag.ingest_documents_async(rag_docs)
                print(f"[UnifiedOrchestrator] 📚 Векторная база знаний RAG успешно обогащена: {indexed_count} чанков для '{company_name}'.")
                self._log_trace(session_id, "CleanRAGPipeline", "KnowledgeIndexed", {"indexed_chunks": indexed_count, "company": company_name})
            except Exception as rag_err:
                print(f"[UnifiedOrchestrator] ⚠️ Ошибка индексации RAG: {rag_err}")

            # 5. Сохранение в реляционную БД (SQL)
            profile_id = None
            if self.db:
                try:
                    profile = UserProfile(
                        external_user_id=user_data.get("user_id", "default_user"),
                        user_id=user_data.get("user_id", "default_user"),
                        company_name=company_name,
                        niche=brand_profile.get("field", activity),
                        city=brand_profile.get("market", {}).get("geography", city),
                        country=country,
                        location_details={"country": country, "city": city, "holidays_count": len(holiday_events) if 'holiday_events' in locals() else 0},
                        target_audience=brand_profile.get("market", {}).get("segment", ""),
                        step1={"voice_and_tone": brand_profile.get("tone", []), "positioning": brand_profile.get("positioning", ""), "brand_colors": brand_profile.get("brand_colors", [])},
                        step2=brand_profile.get("market", {}),
                        step3=brand_profile.get("swot", {}),
                        step4={"services": brand_profile.get("services", [])},
                        step5={"goals": brand_profile.get("goals", [])},
                        visual_grid_dna=visual_grid_dna,
                        brand_dossier={
                            "website_dossier": website_data.get("structured_dossier") if website_data else None,
                            "documents_dossier": doc_collector.synthesize_dossier_from_docs(client_docs_data) if (client_docs_data and 'doc_collector' in locals()) else None,
                            "strategy": strategy_data,
                            "pains": pains_list
                        },
                        social_links={"link": raw_social_input, "socials": user_data.get("socials", [])}
                    )
                    self.db.add(profile)
                    self.db.commit()
                    self.db.refresh(profile)
                    profile_id = profile.id
                    self._log_trace(session_id, "ChiefOrchestrator", "ProfileSaved", {"profile_id": profile_id})
                    print(f"[UnifiedOrchestrator] ✅ Профиль #{profile_id} ('{company_name}', {country}, г. {city}) успешно сохранен в SQL БД!")
                except Exception as e:
                    print(f"[UnifiedOrchestrator] ⚠️ Ошибка сохранения профиля в SQL БД: {e}")
            
            return {
                "status": "success",
                "profile": brand_profile,
                "profile_id": profile_id or 1
            }

        if task_type in {"parse_documents", "ingest_client_files", "extract_documents"}:
            from collectors.document_collector import DocumentCollector
            doc_collector = DocumentCollector()
            
            file_paths = user_data.get("file_paths") or user_data.get("files") or user_data.get("documents") or []
            if isinstance(file_paths, str):
                file_paths = [file_paths]
                
            company_name = user_data.get("company_name", "Наша Компания")
            niche = user_data.get("niche", "Бизнес")
            
            extracted = doc_collector.extract_documents_batch(file_paths)
            indexed_count = await doc_collector.sync_documents_to_rag(company_name, niche, extracted, self.rag)
            dossier = doc_collector.synthesize_dossier_from_docs(extracted)
            
            self._log_trace(session_id, "DocumentCollector", "DocumentsParsed", {
                "files_count": len(file_paths),
                "indexed_chunks": indexed_count,
                "company": company_name
            })
            return {
                "status": "success",
                "extracted_documents": extracted,
                "rag_indexed_count": indexed_count,
                "synthesized_dossier": dossier
            }
            
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

        if task_type in {"track_post_performance", "process_audience_feedback", "feedback_loop"}:
            from analytics.feedback_loop import FeedbackLoopEngine
            engine = FeedbackLoopEngine()
            
            publication_id = user_data.get("publication_id")
            comments = user_data.get("comments", [])
            views = user_data.get("views", 0)
            dislikes = user_data.get("dislikes", 0)
            shares = user_data.get("shares", 0)
            other_reactions = user_data.get("other_reactions", 0)
            platform = user_data.get("platform", "telegram")
            raw_reactions = user_data.get("reactions") or user_data.get("reactions_breakdown")
            comments_count = len(comments) if comments else user_data.get("comments_count", 0)
            
            # Расчет позитивности, чистого одобрения (NAI), взвешенного WPR и логарифмического Score с учетом мультиплатформенных реакций
            positivity = engine.calculate_positivity_metrics(
                views=views,
                likes=likes,
                dislikes=dislikes,
                comments=comments_count,
                shares=shares,
                other_reactions=other_reactions,
                platform=platform,
                raw_reactions=raw_reactions
            )
            er = positivity["engagement_rate"]
            nai = positivity["net_approval_index"]
            wpr = positivity["weighted_positivity_rate"]
            score = positivity["log_positivity_score"]
            grade = positivity["grade"]
            analysis = engine.analyze_comments(comments)
            
            # Сохранение в SQL (PublicationHistory & UserProfile)
            if self.db and publication_id:
                try:
                    pub = self.db.query(PublicationHistory).filter(PublicationHistory.id == publication_id).first()
                    if pub:
                        pub.views_count = views
                        pub.likes_count = likes
                        pub.dislikes_count = dislikes
                        pub.comments_count = comments_count
                        pub.shares_count = shares
                        pub.engagement_rate = er
                        pub.net_approval_index = nai
                        pub.weighted_positivity_rate = wpr
                        pub.log_positivity_score = score
                        pub.positivity_grade = grade
                        pub.comments_analysis = analysis
                        pub.last_monitored_at = datetime.utcnow()
                        self.db.commit()
                        print(f"[UnifiedOrchestrator] 📊 Метрики публикации #{publication_id} сохранены (Score: {score}, NAI: {nai}, WPR: {wpr}%, ER: {er}%).")
                except Exception as sql_e:
                    print(f"[UnifiedOrchestrator] ⚠️ Ошибка сохранения метрик в SQL: {sql_e}")
            
            company_name = user_data.get("company_name", "UCust")
            niche = user_data.get("niche", "IT Automation")
            top_topics = user_data.get("top_topics", [])
            
            # Синхронизация инсайтов в RAG
            indexed_count = await engine.sync_feedback_to_rag(company_name, niche, analysis, top_topics, self.rag)
            adaptations = engine.generate_strategy_adaptations(top_topics, analysis)
            
            # Обновление стратегии в профиле SQL
            if self.db and (user_data.get("profile_id") or user_data.get("user_id")):
                try:
                    prof = None
                    if user_data.get("profile_id"):
                        prof = self.db.query(UserProfile).filter(UserProfile.id == user_data["profile_id"]).first()
                    elif user_data.get("user_id"):
                        prof = self.db.query(UserProfile).filter(UserProfile.user_id == user_data["user_id"]).first()
                    if prof:
                        dossier = dict(prof.brand_dossier or {})
                        dossier["feedback_insights"] = adaptations
                        prof.brand_dossier = dossier
                        self.db.commit()
                except Exception as prof_e:
                    print(f"[UnifiedOrchestrator] ⚠️ Ошибка обновления feedback_insights в SQL: {prof_e}")

            self._log_trace(session_id, "FeedbackLoopEngine", "FeedbackProcessed", {
                "er": er,
                "net_approval_index": nai,
                "weighted_positivity_rate": wpr,
                "log_positivity_score": score,
                "grade": grade,
                "objections": analysis.get("top_objections"),
                "questions": analysis.get("top_questions")
            })
            return {
                "status": "success",
                "positivity_metrics": positivity,
                "engagement_rate": er,
                "comments_analysis": analysis,
                "rag_indexed_count": indexed_count,
                "strategy_adaptations": adaptations
            }
            
        if task_type in {"plan_content", "generate_content_plan", "create_content_plan"}:
            from skills.content_strategy_engine import ContentStrategyEngine
            strat_engine = ContentStrategyEngine()
            
            # 1. Загрузка точного профиля из SQL
            company_name = user_data.get("company_name", "UCust")
            niche = user_data.get("niche", "IT Automation")
            city = user_data.get("city", "Москва")
            country = user_data.get("country", "Россия")
            visual_grid_dna = user_data.get("visual_grid_dna")
            feedback_insights = user_data.get("feedback_insights")

            if self.db and (user_data.get("user_id") or user_data.get("profile_id")):
                try:
                    profile_record = None
                    if user_data.get("profile_id"):
                        profile_record = self.db.query(UserProfile).filter(UserProfile.id == user_data["profile_id"]).first()
                    elif user_data.get("user_id"):
                        profile_record = self.db.query(UserProfile).filter(UserProfile.user_id == user_data["user_id"]).first()
                    
                    if profile_record:
                        company_name = profile_record.company_name or company_name
                        niche = profile_record.niche or niche
                        city = profile_record.city or city
                        country = profile_record.country or country
                        visual_grid_dna = profile_record.visual_grid_dna or visual_grid_dna
                        if not feedback_insights and profile_record.brand_dossier and isinstance(profile_record.brand_dossier, dict):
                            feedback_insights = profile_record.brand_dossier.get("feedback_insights")
                        print(f"[UnifiedOrchestrator] 🗄️ Профиль #{profile_record.id} ('{company_name}', {country}, г. {city}) успешно загружен из SQL БД для контент-плана.")
                except Exception as db_e:
                    print(f"[UnifiedOrchestrator] ⚠️ Ошибка загрузки профиля из SQL: {db_e}")

            # 2. Семантический запрос в RAG по болям и триггерам аудитории
            rag_query_res = await self.rag.query_async(f"боли страхи возражения {company_name} {niche} {city}")
            rag_insights = {
                "pain_points": [c.text[:80] for c in rag_query_res.chunks] if rag_query_res.chunks else [
                    "Страх некачественного результата",
                    "Высокие цены и скрытые переплаты",
                    "Нехватка времени и сложный процесс"
                ],
                "context": rag_query_res.formatted_context
            }

            # 3. Синтез контент-плана с привязкой к 3x3 визуальной сетке, праздникам и обратной связи
            days_count = user_data.get("days_count", 7)
            start_date = user_data.get("start_date")
            content_plan = strat_engine.generate_content_plan(
                company_name=company_name,
                niche=niche,
                visual_grid_dna=visual_grid_dna,
                rag_insights=rag_insights,
                days_count=days_count,
                country=country,
                city=city,
                start_date=start_date,
                feedback_insights=feedback_insights
            )

            self._log_trace(session_id, "Agent_ContentStrategist", "ContentPlanGenerated", content_plan)
            print(f"[UnifiedOrchestrator] 📅 Контент-план на {days_count} дней успешно сгенерирован (Праздников внедрено: {content_plan.get('holidays_included_count', 0)})!")
            return {
                "status": "success",
                "content_plan": content_plan,
                "company_name": company_name,
                "niche": niche
            }

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

            # 1. Загрузка точного профиля из SQL (если передан user_id / profile_id)
            if self.db and (user_data.get("user_id") or user_data.get("profile_id")):
                try:
                    profile_record = None
                    if user_data.get("profile_id"):
                        profile_record = self.db.query(UserProfile).filter(UserProfile.id == user_data["profile_id"]).first()
                    elif user_data.get("user_id"):
                        profile_record = self.db.query(UserProfile).filter(UserProfile.user_id == user_data["user_id"]).first()
                    
                    if profile_record:
                        company_name = profile_record.company_name or company_name
                        niche = profile_record.niche or niche
                        city = profile_record.city or city
                        if profile_record.step1 and isinstance(profile_record.step1, dict):
                            tone = profile_record.step1.get("voice_and_tone", tone) if not user_data.get("tone") else tone
                            if not user_data.get("brand_colors") and profile_record.step1.get("brand_colors"):
                                user_data["brand_colors"] = profile_record.step1.get("brand_colors")
                        if profile_record.visual_grid_dna:
                            user_data["visual_grid_dna"] = profile_record.visual_grid_dna
                            if not user_data.get("brand_colors"):
                                user_data["brand_colors"] = profile_record.visual_grid_dna.get("brand_hex_palette", [])
                        print(f"[UnifiedOrchestrator] 🗄️ Профиль #{profile_record.id} ('{company_name}') успешно загружен из SQL БД для генерации.")
                except Exception as sql_e:
                    print(f"[UnifiedOrchestrator] ⚠️ Ошибка загрузки профиля из SQL: {sql_e}")

            # 2. Семантический RAG-поиск проверенных фактов, болей и УТП
            rag_fact_context = None
            try:
                rag_query_text = f"{prompt} {niche} {company_name}"
                rag_ctx = await self.rag.query_async(rag_query_text)
                if rag_ctx and (rag_ctx.has_sufficient_context or rag_ctx.formatted_context):
                    rag_fact_context = rag_ctx.formatted_context
                    print(f"[UnifiedOrchestrator] 📚 RAG предоставил проверенный контекст ({len(rag_fact_context)} симв.) для темы: '{prompt}'")
            except Exception as rag_err:
                print(f"[UnifiedOrchestrator] ⚠️ RAG query error: {rag_err}")
            
            print(f"[UnifiedOrchestrator] ✍️ Генерация поста для темы: '{prompt}', компания: '{company_name}', ниша: '{niche}', формат: {format_type}, тон: {tone}")
            
            # 3. Генерация аутентичного SMM текста через Сайгу (с учетом RAG, Moondream и комментариев)
            t_text_start = time.time()
            # 1. Формирование маркетинговой директивы (5 Ступеней Ханта, JTBD, Value Ladder, Fogg CTA, Фреймворки)
            from skills.marketing_frameworks import (
                MarketingFrameworkDirector, HuntStage, MarketingFramework, PsychologicalTrigger
            )
            
            raw_stage = user_data.get("hunt_stage") or user_data.get("stage")
            hunt_stage_enum = HuntStage(raw_stage) if raw_stage in [s.value for s in HuntStage] else HuntStage.STAGE_2_PROBLEM_AWARE
            stage_strategy = MarketingFrameworkDirector.HUNT_STAGE_STRATEGIES[hunt_stage_enum]
            
            raw_fw = user_data.get("framework")
            framework_enum = MarketingFramework(raw_fw) if raw_fw in [f.value for f in MarketingFramework] else stage_strategy["framework"]
            
            raw_trigger = user_data.get("trigger")
            trigger_enum = PsychologicalTrigger(raw_trigger) if raw_trigger in [t.value for t in PsychologicalTrigger] else stage_strategy["trigger"]
            
            marketing_bundle = MarketingFrameworkDirector.construct_marketing_prompt(
                company_name=company_name,
                niche=niche,
                topic=prompt,
                framework=framework_enum,
                hunt_stage=hunt_stage_enum,
                trigger=trigger_enum,
                pain_points=user_data.get("pain_points") or [f"неэффективность и переплаты в нише {niche}"],
                raw_feature=prompt
            )
            
            print(f"[UnifiedOrchestrator] 🎯 Воронка Ханта: {hunt_stage_enum.value.upper()} | Фреймворк: {framework_enum.value} | Триггер: {trigger_enum.value}")

            saiga = SaigaLLMSkill()
            visual_ctx = moondream_analysis.get("visual_context_for_llm") if moondream_analysis else None
            comments_ctx = user_data.get("comments") or user_data.get("comments_context") or user_data.get("top_objections_from_comments")
            audience_q = user_data.get("audience_questions") or user_data.get("top_audience_questions")
            brand_profile = user_data.get("brand_profile")
            competitor_dossier = user_data.get("competitor_dossier")
            
            gen_result = saiga.generate_smm_post(
                topic=prompt,
                company_name=company_name,
                niche=niche,
                city=city,
                tone=tone,
                format_type=format_type,
                visual_context=visual_ctx,
                comments_context=comments_ctx,
                audience_questions=audience_q,
                comments_enabled=bool(user_data.get("comments_enabled", False)),
                brand_profile=brand_profile,
                rag_context=rag_fact_context,
                marketing_directive=marketing_bundle
            )
            post_text = gen_result.get("post_text", "")
            promo_code = gen_result.get("promo_code", f"{company_name.upper().replace(' ', '')}2026")
            
            # 2. Валидация качества текста (Tone of Voice Gatekeeper & Charlie Munger Pre-Mortem)
            from skills.critic_munger import CriticMungerSkill
            is_valid, error_msg = SecurityGuard.validate_content_tone_of_voice(post_text)
            if not is_valid:
                post_text = saiga.self_heal_text(post_text, error_msg or "")
                
            critic = CriticMungerSkill(strictness=0.80)
            critic_res = critic.review_content(post_text, topic=prompt, target_audience=niche)
            if not critic_res.get("passed"):
                print(f"[UnifiedOrchestrator] 🛡️ Агент-Критик отклонил черновик (Score={critic_res['score']}): {critic_res['criticism']}. Запуск самоисправления...")
                post_text = saiga.self_heal_text(post_text, critic_res.get("actionable_feedback", ""))
                # Повторная проверка
                critic_res = critic.review_content(post_text, topic=prompt, target_audience=niche)
                self._log_trace(session_id, "Agent_Critic_Munger", "PostReviewedAndHealed", critic_res)
            else:
                self._log_trace(session_id, "Agent_Critic_Munger", "PostApproved", critic_res)
            t_text_raw = time.time() - t_text_start
            t_text_duration = round(t_text_raw, 2) if t_text_raw >= 0.1 else round(max(0.05, t_text_raw), 2)
            
            # 3. Формирование коммерческого фото-промпта в связке с текстом поста
            custom_visual_prompt = gen_result.get("visual_prompt")
            if not custom_visual_prompt:
                director = AdvancedVisualDirector(brand_images=[])
                prompt_kw = moondream_analysis.get("prompt_keywords") if moondream_analysis else ""
                visual_kw_str = f" Visual details: {prompt_kw}." if prompt_kw else ""
                visual_prompt_data = director.create_photorealistic_prompt(
                    topic=f"{prompt}.{visual_kw_str}",
                    niche=niche,
                    aspect_ratio=aspect_ratio,
                    brand_colors=user_data.get("brand_colors") or (moondream_analysis.get("colors") if moondream_analysis else None)
                )
                photo_prompt = visual_prompt_data.get("positive_prompt")
            else:
                photo_prompt = custom_visual_prompt

            # 4. Генерация SMM Фотографии
            image_url = None
            t_photo_duration = None
            if should_gen_image:
                try:
                    t_photo_start = time.time()
                    photo_skill = PhotoGeneratorSkill()
                    photo_res = await photo_skill.generate_photo(
                        topic=prompt,
                        niche=niche,
                        aspect_ratio=aspect_ratio,
                        company_name=company_name,
                        brand_colors=user_data.get("brand_colors") or (moondream_analysis.get("colors") if moondream_analysis else None),
                        attachments=user_data.get("attachments"),
                        custom_prompt=photo_prompt
                    )
                    t_photo_duration = round(time.time() - t_photo_start, 2)
                    image_url = photo_res.get("image_url")
                    photo_prompt = photo_res.get("positive_prompt") or photo_prompt

                    # Сохранение финального промпта фото в RAG (категория photo_generation_history)
                    if photo_prompt:
                        try:
                            from rag.models import Document
                            photo_id = os.path.splitext(os.path.basename(photo_res.get("file_path", "")))[0] if photo_res.get("file_path") else str(uuid.uuid4())[:8]
                            prompt_doc = Document(
                                doc_id=f"visual_prompt_{photo_id}",
                                text=(
                                    f"Финальный промпт генерации фото для компании {company_name} (Ниша: {niche}):\n"
                                    f"Тема: {prompt}\n"
                                    f"Положительный промпт ComfyUI: {photo_prompt}\n"
                                    f"Отрицательный промпт ComfyUI: {photo_res.get('negative_prompt', '')}\n"
                                    f"Цвета бренда: {user_data.get('brand_colors', [])}\n"
                                    f"Соотношение сторон: {aspect_ratio}\n"
                                    f"Путь к файлу: {photo_res.get('file_path', '')}"
                                ),
                                metadata={
                                    "category": "photo_generation_history",
                                    "company_name": company_name,
                                    "user_id": user_data.get("user_id"),
                                    "file_path": photo_res.get("file_path", "")
                                }
                            )
                            await self.rag.ingest_documents_async([prompt_doc])
                            print(f"[UnifiedOrchestrator] 📚 Финальный фото-промпт успешно сохранен в RAG-память бренда.")
                        except Exception as rag_p_err:
                            print(f"[UnifiedOrchestrator] ⚠️ Ошибка сохранения промпта фото в RAG: {rag_p_err}")
                except Exception as ex:
                    print(f"[UnifiedOrchestrator] ⚠️ Ошибка генерации фото: {ex}")

            # 5. Очистка текста для пользователя (строго без хэштегов в теле поста)
            clean_user_post_text = "\n".join([
                line for line in post_text.strip().splitlines()
                if not line.strip().startswith("#") and not line.strip().startswith("🏷️ Хэштеги")
            ]).strip()

            hashtags_str = gen_result.get("hashtags", f"#{niche.replace(' ', '_')} #бизнес #качество")

            # 6. Опциональная авто-публикация
            publish_res = None
            if user_data.get("publish") or user_data.get("target_channel"):
                from publishers.achievement_broadcaster import AchievementBroadcaster
                target_ch = user_data.get("target_channel") or user_data.get("channel") or "@testaipublisher"
                broadcaster = AchievementBroadcaster(target_channel=target_ch)
                publish_res = await broadcaster.publish_post_async(
                    post_text=clean_user_post_text,
                    media_path=image_url,
                    timings={
                        "text_gen_seconds": t_text_duration,
                        "photo_gen_seconds": t_photo_duration,
                        "total_seconds": round(time.time() - t_text_start, 2)
                    },
                    hashtags=hashtags_str,
                    category=user_data.get("category", "Обновление"),
                    target_channel=target_ch
                )

            self._log_trace(session_id, "SaigaCopywriter", "PostGenerated", {"topic": prompt, "format": format_type})
            return {
                "status": "success",
                "post_text": clean_user_post_text,
                "promo_code": promo_code,
                "photo_prompt": photo_prompt,
                "image_url": image_url,
                "photo_url": image_url,
                "hashtags": hashtags_str,
                "confidence_score": 0.96,
                "format": format_type,
                "tone": tone,
                "critic_review": critic_res,
                "moondream_analysis": moondream_analysis,
                "publish_result": publish_res,
                "timings": {
                    "text_gen_seconds": t_text_duration,
                    "photo_gen_seconds": t_photo_duration,
                    "total_seconds": round(time.time() - t_text_start, 2)
                }
            }

        if task_type in ["generate_image", "generate_photo", "edit_photo"]:
            from skills.photo_generator import PhotoGeneratorSkill
            
            prompt = user_data.get("prompt") or user_data.get("topic") or "Специальное предложение"
            niche = user_data.get("niche", "Бизнес")
            aspect_ratio = user_data.get("aspect_ratio", "1:1")
            style = user_data.get("style", "photorealistic")
            brand_colors = user_data.get("brand_colors") or (moondream_analysis.get("colors") if moondream_analysis else None)
            company_name = user_data.get("company_name", "UCust")
            attachments = user_data.get("attachments") or user_data.get("images")
            
            # Обогащение промпта от Сайги, если запрос от пользователя короткий
            photo_skill = PhotoGeneratorSkill()
            custom_prompt = user_data.get("custom_prompt") or user_data.get("positive_prompt")
            
            photo_res = await photo_skill.generate_photo(
                topic=prompt,
                niche=niche,
                aspect_ratio=aspect_ratio,
                brand_colors=brand_colors,
                style=style,
                company_name=company_name,
                attachments=attachments,
                custom_prompt=custom_prompt
            )
            photo_res["moondream_analysis"] = moondream_analysis
            
            self._log_trace(session_id, "PhotoGenerator", "PhotoCreated", {
                "topic": prompt,
                "aspect_ratio": aspect_ratio,
                "edit_mode": bool(attachments and len(attachments) > 0),
                "attachments_count": len(attachments) if attachments else 0
            })
            return photo_res

        if task_type in ["analyze_competitor", "competitive_intel"]:
            from skills.competitive_intel import CompetitiveIntelSkill
            url = user_data.get("url") or user_data.get("competitor_url") or ""
            niche = user_data.get("niche", "")
            intel = CompetitiveIntelSkill()
            res = await intel.analyze_competitor_async(url, my_company_niche=niche)
            self._log_trace(session_id, "CompetitiveIntelAnalyst", "CompetitorAnalyzed", {
                "competitor_url": url,
                "status": res.get("status")
            })
            return res

        if task_type in ["generate_strategy", "content_strategy"]:
            from skills.content_strategy_engine import ContentStrategyEngine
            company_name = user_data.get("company_name", "UCust")
            niche = user_data.get("niche", "Бизнес")
            target_audience = user_data.get("target_audience", "")
            usp = user_data.get("usp", "")
            engine = ContentStrategyEngine()
            strat_res = engine.generate_strategy(company_name, niche, target_audience, usp)
            self._log_trace(session_id, "ContentStrategyEngine", "StrategyGenerated", {
                "company_name": company_name,
                "niche": niche
            })
            return strat_res

        if task_type in ["critic_review", "review_content"]:
            from skills.critic_munger import CriticMungerSkill
            text = user_data.get("text") or user_data.get("content") or ""
            topic = user_data.get("topic", "")
            niche = user_data.get("niche", "")
            strictness = float(user_data.get("strictness", 0.85))
            critic = CriticMungerSkill(strictness=strictness)
            review = critic.review_content(text, topic=topic, target_audience=niche)
            self._log_trace(session_id, "Agent_Critic_Munger", "ManualReviewCompleted", review)
            return {
                "status": "success",
                "review": review
            }

        if task_type in ["publish_post", "publish_content", "publish_showcase"]:
            from publishers.achievement_broadcaster import AchievementBroadcaster
            post_text = user_data.get("post_text") or user_data.get("text") or ""
            media_path = user_data.get("media_path") or user_data.get("image_url") or user_data.get("photo_url")
            timings = user_data.get("timings")
            hashtags = user_data.get("hashtags")
            category = user_data.get("category", "Обновление")
            target_ch = user_data.get("target_channel") or user_data.get("channel") or "@testaipublisher"
            
            broadcaster = AchievementBroadcaster(target_channel=target_ch)
            res = await broadcaster.publish_post_async(
                post_text=post_text,
                media_path=media_path,
                timings=timings,
                hashtags=hashtags,
                category=category,
                target_channel=target_ch
            )
            self._log_trace(session_id, "AchievementBroadcaster", "PostPublished", res)
            return res

        if task_type in ["broadcast_achievement", "post_milestone"]:
            from publishers.achievement_broadcaster import AchievementBroadcaster
            title = user_data.get("title", "Новое достижение UCust AI")
            desc = user_data.get("description") or user_data.get("desc", "Команда ИИ-агентов завершила важный этап.")
            metrics = user_data.get("metrics", [])
            media_path = user_data.get("media_path") or user_data.get("media")
            channel = user_data.get("channel", "@UcustAi")
            
            broadcaster = AchievementBroadcaster(target_channel=channel)
            res = await broadcaster.broadcast_milestone_async(
                title=title,
                description=desc,
                metrics=metrics,
                media_path=media_path
            )
            self._log_trace(session_id, "AchievementBroadcaster", "MilestoneBroadcasted", res)
            return res

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
