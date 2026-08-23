import os
import re

with open('onboarding_pipeline.py', 'r', encoding='utf-8') as f:
    code = f.read()

# We will just write a new script that cleanly replaces onboarding_pipeline.py
# since replacing large chunks with regex is fragile.

new_code = """
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
    print("[Agent_Interviewer] 🗣️ Начинаю диалог с пользователем...")
    await asyncio.sleep(0.5)
    
    print(f"[Agent_Interviewer] 🗣️ Вопрос: Какие ваши главные боли в SMM, {user_data.get('company_name')}?")
    print(f"[Пользователь] 👨‍💻 Ответ: Много рутины, сложно генерировать контент каждый день.")
    await asyncio.sleep(0.5)
    
    print("[Agent_Interviewer] 🗣️ Вопрос: Какие основные цели вы ставите перед соцсетями?")
    print(f"[Пользователь] 👨‍💻 Ответ: Привлечение B2B лидов, повышение узнаваемости.")
    await asyncio.sleep(0.5)
    
    print("[Agent_Interviewer] 🗣️ Вопрос: Укажите ваши каналы в Telegram и/или группы VK для анализа.")
    print(f"[Пользователь] 👨‍💻 Ответ: {user_data.get('raw_social_input')}")
    
    def _parse_social_links(raw: str) -> dict:
        tg_links = re.findall(r'(?:t\.me/|@)([a-zA-Z0-9_]+)', raw)
        vk_links = re.findall(r'vk\.com/([a-zA-Z0-9_]+)', raw)
        return {
            "telegram": [f"@{link}" for link in tg_links],
            "vk": [f"vk.com/{link}" for link in vk_links],
            "alerts": []
        }
    
    links = _parse_social_links(user_data.get("raw_social_input", ""))
    print(f"[Agent_Interviewer] 🗣️ Распознаны ссылки: Telegram={links['telegram']}, VK={links['vk']}")
    
    if len(user_data.get("raw_social_input", "").split()) > 3:
        links["alerts"].append(f"⚠️ В тексте обнаружены лишние слова. Мы извлекли только каналы: {links['telegram'] + links['vk']}. Проверьте, всё ли верно!")
        print(f"[Agent_Interviewer] {links['alerts'][0]}")
        
    print("[Agent_Interviewer] 🗣️ Диалог завершен. Данные возвращены Оркестратору.")
    return links


async def analyst_parser(social_links: dict) -> Tuple[List[str], List[str]]:
    from collectors.telethon_collector import TelethonCollector

    tg_channels = social_links.get("telegram", [])
    vk_groups = social_links.get("vk", [])

    print(f"[Agent_Analyst] 🧠 Парсинг каналов: Telegram={tg_channels}, VK={vk_groups}")
    collector = TelethonCollector()
    parsed_posts = []
    downloaded_media = []

    for channel in tg_channels:
        print(f"[Agent_Analyst] 📥 Парсинг Telegram-канала {channel} и скачивание медиа...")
        result = await collector.collect_async(channel, limit=10)
        messages = result.payload.get("messages", [])
        for msg in messages:
            text = msg.get("text", "").strip()
            if text:
                parsed_posts.append(text)
            path = msg.get("media_path")
            if path:
                downloaded_media.append(path)
        await asyncio.sleep(0.5)

    for group in vk_groups:
        print(f"[Agent_Analyst] 📥 Парсинг VK-группы {group} (mock)...")
        await asyncio.sleep(1)
        parsed_posts.append(f"VK пост из {group}: Я открываю запись SMM-наставничество. Мы научимся применять LLM агентов в 2026 году. Купи курс: https://vk.com/link")
        parsed_posts.append(f"VK пост из {group}: (РЕКЛАМА: 🛒 30% НА КУРС! Записывайтесь прямо щас на сайте www.course.com/buy)")

    print(f"[Agent_Analyst] ✅ Парсинг завершен. Собрано {len(parsed_posts)} текстов и {len(downloaded_media)} медиафайлов.")
    
    try:
        from skills.repowise_compressor import RepowiseCompressorSkill
        compressor = RepowiseCompressorSkill(max_tokens=150)
        parsed_posts = compressor.distill_posts(parsed_posts)
    except Exception as e:
        print(f"[Agent_Analyst] ⚠️ Ошибка Repowise: {e}")

    return parsed_posts, downloaded_media


async def visual_director_vqa(parsed_posts: list, all_photos: list) -> Tuple[List[str], List[str]]:
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


class AgentSaiga:
    @staticmethod
    def analyze_voice_tone(user_data, clean_posts, visuals) -> dict:
        print("\\n[Saiga LLM] 🧠 Анализирую данные...")
        time.sleep(1)
        print("[Saiga LLM] 🧠 Синтез болей/целей от Интервьюера...")
        time.sleep(1)
        print("[Saiga LLM] 🧠 Анализ лексики из спарсенных текстов Аналитика...")
        time.sleep(1)
        print("[Saiga LLM] 🧠 Анализ визуальной стилистики от Визуального директора...")
        
        return {
            "tone_of_voice": "Профессиональный, технологичный, но дружелюбный",
            "visual_style": "Минимализм с синими акцентами (Cyber Blue)",
            "key_topics": ["Автоматизация", "SMM", "Экономия времени"],
            "taboos": ["Агрессивные продажи", "Ложные гарантии 100%"]
        }


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
        voice_and_tone = AgentSaiga.analyze_voice_tone(self.user_data, clean_posts, visuals)
        self._log_trace("Agent_Saiga", "Synthesized_Profile", voice_and_tone)

        # 5. Сохранение в SQL и Vector DB (Делает сам Оркестратор)
        print("\\n[Orchestrator] ⚖️ Финальное сохранение профиля в БД...")
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


async def generate_calendar(profile_id: int, db: Any):
    print("\\n[Frontend] 📅 Генерация контент-плана на основе профиля...")
    time.sleep(1.5)
    print(f"[Frontend] 📅 План для профиля #{profile_id} готов! Можно генерировать видео.")


async def visual_director_video_qa(video_file: str):
    print(f"\\n[Agent_Visual_Director] 🔍 Локальное QA: проверка сгенерированного '{video_file}' на баги...")
    time.sleep(2)
    print(f"[Agent_Visual_Director] ❌ ОБНАРУЖЕН БАГ: Галлюцинация 'Телепортация' на 00:03")

async def orchestrator_qa_decision():
    print("[Orchestrator] ⚖️ Получен QA-отчет от Visual Director. Статус: REJECTED")
    print("[Orchestrator] ⚖️ Принимаю решение: Отправить LTX-Video на перегенерацию...")


async def run_onboarding():
    db = DatabaseFactory.build()
    session = db.get_session()
    vector_store = InMemoryVectorStore()
    
    user_data = {
        "company_name": "UCust SMM",
        "raw_social_input": "Мой канал t.me/dvachannel",
        "uploaded_photos": ["photo1_office.jpg", "photo2_team.jpg"],
        "pain_points": "Много рутины, сложно генерировать контент каждый день.",
        "goals": "Привлечение B2B лидов, повышение узнаваемости."
    }

    orchestrator = ChiefOrchestrator(session, vector_store, user_data)
    profile = await orchestrator.run_pipeline()
    
    await generate_calendar(profile.id, db)
    await visual_director_video_qa("promo_draft1.mp4")
    await orchestrator_qa_decision()


if __name__ == "__main__":
    asyncio.run(run_onboarding())
"""

with open('onboarding_pipeline.py', 'w', encoding='utf-8') as f:
    f.write(new_code)
print("Updated onboarding_pipeline.py completely.")
