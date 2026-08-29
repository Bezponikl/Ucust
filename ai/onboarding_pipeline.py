
import asyncio
import re
import json
import time
import hashlib
import uuid
from typing import List, Tuple, Dict, Any
from storage.db import DatabaseFactory
from storage.models import UserProfile, OrchestratorTrace
from storage.vector_store import VectorStore, InMemoryVectorStore, VectorRecord
from dotenv import load_dotenv

load_dotenv(override=True)

# -------------------------------------------------------------------
# 1. Агенты (Независимые микросервисы)
# -------------------------------------------------------------------

async def interviewer_chat(user_data: dict) -> Dict[str, Any]:
    """
    Агент-Интервьюер (Agent_Interviewer):
    Тактичный и лаконичный онбординг.
    Без уменьшительно-ласкательных суффиксов, без менторства и искусственного восторга.
    """
    print("[Agent_Interviewer] 🎙️ Тактичный диалог с пользователем (лаконичный UX)...")
    await asyncio.sleep(0.3)
    
    print(f"[Agent_Interviewer] 🎙️ Вопрос: Какие ваши главные задачи и сложности в SMM, {user_data.get('company_name')}?")
    print(f"[Пользователь] 👨‍💻 Ответ: Высокие трудозатраты на рутину, нехватка времени на ежедневный постинг.")
    await asyncio.sleep(0.3)
    
    print("[Agent_Interviewer] 🎙️ Вопрос: Какие ключевые цели вы ставите перед социальными сетями?")
    print(f"[Пользователь] 👨‍💻 Ответ: Привлечение целевых B2B клиентов, рост узнаваемости компании.")
    await asyncio.sleep(0.3)
    
    print("[Agent_Interviewer] 🎙️ Вопрос: Укажите ссылки на ваши каналы в Telegram, группы VK или карточки на картах.")
    print(f"[Пользователь] 👨‍💻 Ответ: {user_data.get('raw_social_input')}")
    
    def _parse_social_links(raw: str) -> dict:
        tg_links = re.findall(r'(?:t\.me/|@)([a-zA-Z0-9_]+)', raw)
        vk_links = re.findall(r'vk\.com/([a-zA-Z0-9_]+)', raw)
        ok_links = re.findall(r'(?:ok\.ru|odnoklassniki\.ru)/(?:group/|profile/)?([a-zA-Z0-9_.-]+)', raw)
        yandex_links = re.findall(r'yandex\.(?:ru|com)/maps/org/[a-zA-Z0-9_-]+/\d+', raw)
        twogis_links = re.findall(r'2gis\.(?:ru|kz)/[a-zA-Z]+/firm/\d+', raw)
        
        # Автоматическое распознавание веб-сайтов компании (любые домены кроме соцсетей и карт)
        raw_urls = re.findall(r'https?://[^\s,;]+|(?:www\.)?[a-zA-Z0-9-]+\.(?:ru|com|io|org|net|pro|ai|me|cc|by|kz|tech|online|store|shop|app|dev)(?:/[^\s,;]*)?', raw)
        websites = []
        for u in raw_urls:
            u_clean = u.strip()
            if not any(excluded in u_clean.lower() for excluded in ["t.me", "vk.com", "ok.ru", "odnoklassniki", "yandex.", "2gis."]):
                websites.append(u_clean)
        
        alerts = []
        valid_tg = []
        # Проверка на потенциальные опечатки (слишком короткие имена или спецсимволы)
        for link in tg_links:
            if len(link) < 4:
                alerts.append(f"В ссылке на Telegram-канал (@{link}) замечена опечатка (слишком короткий юзернейм). Мы продолжим онбординг, но для точной аналитики вы сможете обновить ее позже в профиле.")
            else:
                valid_tg.append(f"@{link}")
                
        return {
            "telegram": valid_tg if valid_tg else [f"@{link}" for link in tg_links],
            "vk": [f"vk.com/{link}" for link in vk_links],
            "ok": [f"ok.ru/{link}" for link in ok_links],
            "yandex_maps": yandex_links,
            "2gis": twogis_links,
            "websites": websites,
            "alerts": alerts
        }
    
    links = _parse_social_links(user_data.get("raw_social_input", ""))
    print(f"[Agent_Interviewer] 🎙️ Распознаны ресурсы: Telegram={links['telegram']}, VK={links['vk']}, OK={links.get('ok')}, Yandex={len(links['yandex_maps'])}, 2GIS={len(links['2gis'])}")
    
    if links["alerts"]:
        for alert in links["alerts"]:
            print(f"[Agent_Interviewer] ℹ️ {alert}")
    elif len(user_data.get("raw_social_input", "").split()) > 3:
        print(f"[Agent_Interviewer] ℹ️ Из текста успешно извлечены рабочие адреса: {links['telegram'] + links['vk']}.")
        
    print("[Agent_Interviewer] 🎙️ Данные верифицированы и переданы Оркестратору.")
    return links


async def analyst_parser(social_links: dict) -> Tuple[List[str], List[str]]:
    from collectors.telethon_collector import TelethonCollector
    from collectors.yandex_collector import YandexMapsCollector
    from collectors.twogis_collector import TwoGisCollector
    from core.resource_manager import ResourceManager
    
    # Ресурсы под CPU для парсеров
    ResourceManager.enforce_cpu_for_parsers()

    tg_channels = social_links.get("telegram", [])
    vk_groups = social_links.get("vk", [])
    ok_groups = social_links.get("ok", [])
    yandex_urls = social_links.get("yandex_maps", [])
    twogis_urls = social_links.get("2gis", [])
    websites = social_links.get("websites", [])

    print(f"[Agent_Analyst] 🚀 Server Mode: Запуск сбора данных... TG={len(tg_channels)}, VK={len(vk_groups)}, OK={len(ok_groups)}, Web={len(websites)}, Yandex={len(yandex_urls)}, 2GIS={len(twogis_urls)}")
    
    parsed_posts = []
    downloaded_media = []

    # Функции-обертки для параллельного запуска
    async def fetch_tg(channel):
        texts, media = [], []
        print(f"[Agent_Analyst] ⏳ Парсинг TG {channel}...")
        collector = TelethonCollector()
        result = await collector.collect_async(channel, limit=10)
        for msg in result.payload.get("messages", []):
            text = msg.get("text", "").strip()
            if text: texts.append(text)
            if msg.get("media_path"): media.append(msg.get("media_path"))
        return texts, media

    async def fetch_website(url):
        print(f"[Agent_Analyst] 🌐 Глубокий парсинг веб-сайта {url}...")
        try:
            from collectors.website_collector import WebsiteCollector
            collector = WebsiteCollector()
            res = await collector.collect_website_async(url)
            if res.get("status") == "success":
                dossier = res.get("structured_dossier", "")
                media = []
                if res.get("og_image"):
                    media.append(res.get("og_image"))
                return [dossier], media
        except Exception as e:
            print(f"[Agent_Analyst] ⚠️ Ошибка парсинга сайта {url}: {e}")
        return [], []

    async def fetch_vk(group):
        print(f"[Agent_Analyst] ⏳ Парсинг VK {group}...")
        await asyncio.sleep(0.5)
        return [f"VK пост {group}: Успешный SMM.", f"VK {group}: Скидка 30%!"], []

    async def fetch_ok(group):
        print(f"[Agent_Analyst] ⏳ Парсинг Одноклассники (OK.ru) {group}...")
        await asyncio.sleep(0.5)
        return [f"OK.ru заметка {group}: Полезные советы и новинки.", f"OK.ru {group}: Отзывы покупателей."], []

    async def fetch_yandex(url):
        print(f"[Agent_Analyst] ⏳ Парсинг Yandex {url}...")
        texts = []
        collector = YandexMapsCollector()
        res = await collector.collect_reviews_async(url)
        for rev in res.get("reviews", []):
            texts.append(f"Отзыв Яндекс ({rev['rating']}★): {rev['text']}")
        return texts, []

    async def fetch_twogis(url):
        print(f"[Agent_Analyst] ⏳ Парсинг 2GIS {url}...")
        texts = []
        collector = TwoGisCollector()
        res = await collector.collect_reviews_async(url)
        for rev in res.get("reviews", []):
            texts.append(f"Отзыв 2GIS ({rev['rating']}★): {rev['text']}")
        return texts, []

    # Формируем пул задач
    tasks = []
    for c in tg_channels: tasks.append(fetch_tg(c))
    for w in websites: tasks.append(fetch_website(w))
    for g in vk_groups: tasks.append(fetch_vk(g))
    for ok in ok_groups: tasks.append(fetch_ok(ok))
    for u in yandex_urls: tasks.append(fetch_yandex(u))
    for u in twogis_urls: tasks.append(fetch_twogis(u))

    # Выполняем все сетевые запросы ОДНОВРЕМЕННО
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, tuple) and len(res) == 2:
                parsed_posts.extend(res[0])
                downloaded_media.extend(res[1])
            elif isinstance(res, Exception):
                print(f"[Agent_Analyst] ⚠️ Ошибка при параллельном парсинге: {res}")

    print(f"[Agent_Analyst] ✅ Параллельный сбор завершен. Собрано текстов: {len(parsed_posts)}, медиа: {len(downloaded_media)}")
    
    try:
        from skills.repowise_compressor import RepowiseCompressorSkill
        compressor = RepowiseCompressorSkill(max_tokens=150)
        parsed_posts = compressor.distill_posts(parsed_posts)
    except Exception as e:
        print(f"[Agent_Analyst] ⚠️ Ошибка Repowise: {e}")

    return parsed_posts, downloaded_media


async def visual_director_vqa(parsed_posts: list, all_photos: list) -> Tuple[List[str], List[str]]:
    from core.resource_manager import ResourceManager
    
    # Возвращаем видимость видеокарты и повышаем приоритет для тяжелой ИИ-модели
    ResourceManager.enforce_gpu_priority_for_ai()
    
    print("[Agent_Visual_Director] 🎨 Начинаю работу на базе локальной нейросети Moondream2 (GGUF)...")
    print(f"[Agent_Visual_Director] 🎨 Moondream VQA: Анализ фото/видео ({len(all_photos)} шт.)...")
    
    try:
        from skills.moondream_vqa import MoondreamVQASkill
        vqa_skill = MoondreamVQASkill()
        
        visual_descriptions = []
        for photo in all_photos:
            try:
                res = vqa_skill.describe_image(photo, prompt="Опиши стиль, цвета и объекты на фото коротко, чтобы передать контекст для Сайги.")
                visual_descriptions.append(res)
            except Exception as e:
                visual_descriptions.append(f"Ошибка: {e}")
    except Exception as err:
        print(f"[Agent_Visual_Director] ⚠️ Moondream не загрузился: {err}")
        visual_descriptions = [f"Mock VQA для {p}" for p in all_photos]
        await asyncio.sleep(1)
        
    clean_posts = parsed_posts
    print(f"[Agent_Visual_Director] 🎨 Визуальный пред-анализ завершен. Данные возвращены Оркестратору.")
    return clean_posts, visual_descriptions


async def agent_saiga_analyze(user_data: dict, clean_posts: list, visuals: list) -> dict:
    from skills.saiga_llm import SaigaLLMSkill
    from core.resource_manager import ResourceManager
    
    # Максимальный приоритет для LLM Сайги на видеокарте
    ResourceManager.enforce_gpu_priority_for_ai()
    
    # === НАСТРОЙКИ САЙГИ ===
    saiga = SaigaLLMSkill(
        temperature=0.8,       # Делаем тексты чуть более креативными (было 0.7)
        top_p=0.95,            # Расширяем словарный запас
        repetition_penalty=1.15, # Строго штрафуем за повторения слов
        max_tokens=2048        # Разрешаем выдавать более длинные ответы
    )
    # =======================
    
    print("\n[Saiga LLM] 🧠 Анализирую данные через SaigaSkill...")
    result = saiga.analyze_brand_profile(user_data, clean_posts, visuals)
    return result


# -------------------------------------------------------------------
# 2. Chief Orchestrator (Hub-and-Spoke + Event Sourcing)
# -------------------------------------------------------------------

class ChiefOrchestrator:
    def __init__(self, db_session, vector_store: VectorStore, user_data: dict):
        self.db = db_session
        self.vector_store = vector_store
        self.user_data = user_data
        self.session_id = str(uuid.uuid4())
        print(f"[Orchestrator] ⚖️ Инициализация сессии: {self.session_id}")

    def _hash_payload(self, payload: Any) -> str:
        payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

    def _log_trace(self, agent_name: str, action: str, payload: Any):
        payload_hash = self._hash_payload(payload)
        trace = OrchestratorTrace(
            session_id=self.session_id,
            agent_name=agent_name,
            action=action,
            payload_hash=payload_hash,
            payload=payload if isinstance(payload, dict) else {"data": payload}
        )
        self.db.add(trace)
        self.db.commit()
        print(f"[Orchestrator] ⚖️ State Saved | Agent: {agent_name} | Action: {action} | Hash: {payload_hash[:8]}...")

    async def run_pipeline(self):
        print("=" * 70)
        print("🔥 [ORCHESTRATOR] ЗАПУСК ЦЕНТРАЛИЗОВАННОГО ПАЙПЛАЙНА")
        print("=" * 70)

        # 1. Interviewer
        social_links = await interviewer_chat(self.user_data)
        self.user_data["social_links"] = social_links
        self._log_trace("Agent_Interviewer", "Extracted_Social_Links", social_links)

        # 2. Analyst
        parsed_posts, downloaded_media = await analyst_parser(social_links)
        self._log_trace("Agent_Analyst", "Parsed_Channels", {
            "posts_count": len(parsed_posts),
            "media_count": len(downloaded_media)
        })

        # 3. Visual Director
        all_photos = self.user_data.get("uploaded_photos", []) + downloaded_media
        clean_posts, visuals = await visual_director_vqa(parsed_posts, all_photos)
        self._log_trace("Agent_Visual_Director", "Image_Analysis", {
            "visuals_count": len(visuals),
            "descriptions": visuals
        })

        # 4. Saiga LLM
        voice_and_tone = await agent_saiga_analyze(self.user_data, clean_posts, visuals)
        self._log_trace("Agent_Saiga", "Synthesized_Profile", voice_and_tone)

        # 5. Сохранение в SQL и Vector DB (Делает сам Оркестратор)
        print("\n[Orchestrator] ⚖️ Финальное сохранение профиля в БД...")
        profile = UserProfile(
            external_user_id="user_123",
            niche="IT Automation",
            step1={"voice_and_tone": voice_and_tone},
            social_links=social_links
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)

        texts_to_embed = [
            json.dumps(voice_and_tone),
            f"Боли клиента: {self.user_data.get('pain_points', '')}",
            f"Цели клиента: {self.user_data.get('goals', '')}"
        ]
        for i, t in enumerate(texts_to_embed):
            emb = self.vector_store.embed_text(t)
            self.vector_store.add_embedding(VectorRecord(text_id=str(i), embedding=emb, metadata={"niche": "IT"}))
            
        print(f"[Orchestrator] ⚖️ Профиль id={profile.id} успешно создан. Векторов в базе: {self.vector_store.count()}")
        return profile


async def run_advanced_visual_director(user_data: dict, saiga_profile: dict):
    from skills.advanced_visual_director import AdvancedVisualDirector
    from skills.saiga_llm import SaigaLLMSkill
    
    # Запрашиваем у Сайги креативный сценарий (массовка, звук, окружение)
    saiga = SaigaLLMSkill()
    storyboard = saiga.generate_storyboard(saiga_profile, scenes_count=15)
    
    # Передаем сценарий Режиссеру для конвертации в технические промпты
    director = AdvancedVisualDirector(brand_images=user_data.get("uploaded_photos", []))
    prompts = director.create_cinematic_prompts(saiga_profile, storyboard)
    
    # 2. Рендеринг и QA
    final_video = "temp_media/final_promo.mp4"
    await director.generate_and_qa_video(prompts, final_video)


async def run_onboarding():
    from core.orchestrator import UnifiedOrchestrator
    from storage.db import DatabaseFactory
    from storage.vector_store import InMemoryVectorStore
    
    # Force SQLite for local testing to avoid Postgres auth error
    db = DatabaseFactory.build(dsn="sqlite:///./ai_smm_dev.db")
    db.create_all()
    session = db.get_session()
    vector_store = InMemoryVectorStore()
    
    user_data = {
        "company_name": "UCust SMM",
        "raw_social_input": "Мой канал t.me/dvachannel. Наш Яндекс: yandex.ru/maps/org/ucust/123456 и 2GIS: 2gis.ru/moscow/firm/7891011",
        "uploaded_photos": ["photo1_office.jpg", "photo2_team.jpg"],
        "pain_points": "Много рутины, сложно генерировать контент каждый день.",
        "goals": "Привлечение B2B лидов, повышение узнаваемости."
    }

    # Чтобы у MediaUtils был реальный файл для извлечения цвета (создадим dummy-картинку)
    try:
        from PIL import Image
        img = Image.new('RGB', (100, 100), color = '#1A2B3C')
        img.save('photo1_office.jpg')
    except:
        pass

    orchestrator = ChiefOrchestrator(session, vector_store, user_data)
    profile = await orchestrator.run_pipeline()
    
    # Запускаем продвинутого ИИ-Режиссера
    await run_advanced_visual_director(user_data, profile.step1.get("voice_and_tone", {}))


if __name__ == "__main__":
    asyncio.run(run_onboarding())
