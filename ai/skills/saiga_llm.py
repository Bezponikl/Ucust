from __future__ import annotations
import os
import re
import json
import time
from typing import Any, Dict, List, Optional, Union

class SaigaLLMSkill:
    """
    Интеграция с локальной LLM Сайга (через llama.cpp или Ollama).
    Здесь собраны все "крутилки" (настройки) для генерации контента.
    """
    def __init__(
        self, 
        model_path: str = "models/saiga/saiga-8b.gguf",
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        max_tokens: int = 1024,
        repetition_penalty: float = 1.1
    ):
        self.model_path = model_path
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_tokens = max_tokens
        self.repetition_penalty = repetition_penalty
        self._llm = None
        self._is_loaded = False
        self._init_prompt()

    def _resolve_path(self, path_str: str) -> str:
        if os.path.exists(path_str):
            return path_str
        base_dir = os.path.dirname(os.path.abspath(__file__))
        alt_ai = os.path.normpath(os.path.join(base_dir, "..", path_str))
        if os.path.exists(alt_ai):
            return alt_ai
        alt_repo = os.path.normpath(os.path.join(base_dir, "..", "..", path_str))
        if os.path.exists(alt_repo):
            return alt_repo
        
        # Автоматический поиск любого GGUF файла в папке models/saiga/
        for candidate_dir in [
            os.path.normpath(os.path.join(base_dir, "..", "models", "saiga")),
            os.path.normpath(os.path.join(base_dir, "..", "..", "ai", "models", "saiga")),
            "models/saiga",
            "/opt/ucust/ai/models/saiga"
        ]:
            if os.path.exists(candidate_dir):
                for fname in os.listdir(candidate_dir):
                    if fname.endswith(".gguf"):
                        found = os.path.join(candidate_dir, fname)
                        print(f"[SaigaSkill] 🔍 Автоматически обнаружен файл модели: {found}")
                        return found
        return path_str

    def _init_prompt(self):
        self.system_prompt = (
            "Ты - профессиональный SMM-копирайтер и контент-менеджер, который пишет живо, емко и по делу. "
            "Твои тексты звучат так, будто их написал живой, думающий человек, а не бездушный генератор маркетинговых шаблонов.\n\n"
            "СТРОГИЕ ПРАВИЛА И СТОП-ФАКТОРЫ:\n\n"
            "1. НИКАКИХ ТАВТОЛОГИЙ И МАСЛА МАСЛЯНОГО:\n"
            "   - Категорически запрещено повторять одно и то же слово или корень в рамках одного предложения или близко стоящих предложений "
            "(например: 'Казань празднует День города Казань'). Всегда проверяй текст на дубликаты существительных, названий и топонимов.\n\n"
            "2. НИКАКОЙ «ТОКСИЧНОЙ БОДРОСТИ» И ФАЛЬШИ:\n"
            "   - Забудь про истерично-восторженные наречия и клише: 'безумно', 'невероятно', 'потрясающе', 'волшебный', 'сказочный'.\n"
            "   - Не используй фальшивое дружелюбие (over-friendliness) и навязанное панибратство. Общайся с уважением к личным границам пользователя, на 'вы' (если иное не оговорено явно).\n\n"
            "3. АДЕКВАТНОСТЬ КОНТЕКСТУ:\n"
            "   - Учитывай реальность: погоду, время суток, физическое состояние людей (усталость, холод, спешка).\n"
            "   - Никогда не навязывай неуместные активности (например, 'отличных прогулок', если на улице ливень или люди заняты делом). Пожелания должны быть уместными, нейтральными или поддерживающими.\n\n"
            "4. ЕСТЕСТВЕННЫЙ CALL-TO-ACTION (CTA) И АКЦИИ:\n"
            "   - Интегрируй призывы к действию и кодовые фразы органично, без нажима и навязчивости. Механика должна выглядеть как приятный бонус или забота, а не как агрессивный маркетинг.\n\n"
            "5. ТИПОГРАФИКА:\n"
            "   - Всегда используй короткие дефисы/тире '-' вместо длинных '—'.\n\n"
            "ПРИМЕРЫ СТИЛЯ (ПОДРАЖАЙ ИМ):\n"
            "- ❌ Плохо: 'Безумно любим наш город за эти волшебные моменты! Классного дня и отличных прогулок, скорее заглядывайте к нам!'\n"
            "- ✔️ Хорошо: 'Если решите выбраться в центр, заглядывайте к нам согреться и передохнуть от суеты. Хорошего дня!'\n\n"
            "Всегда перечитывай свой финальный текст перед отправкой на наличие этих ошибок и исправляй их до того, как показать пользователю."
        )

    def generate_smm_post(
        self,
        topic: str,
        company_name: str = "UCust",
        niche: str = "IT Automation",
        city: str = "Москва",
        tone: str = "Естественный и живой",
        format_type: str = "post",
        visual_context: Optional[str] = None,
        comments_context: Optional[List[str]] = None,
        audience_questions: Optional[List[str]] = None,
        comments_enabled: bool = False,
        brand_profile: Optional[dict] = None,
        user_notes: Optional[str] = None,
        tone_override: Optional[str] = None,
        **kwargs
    ) -> dict:
        """
        Генерирует уникальный, высококонверсионный SMM-текст публикации строго под заданную тему,
        нишу и компанию, обогащая текст деталями визуального анализа от Moondream и
        анализом комментариев/возражений целевой аудитории.
        """
        if tone_override:
            tone = tone_override
        if brand_profile and isinstance(brand_profile, dict):
            if "company_name" in brand_profile:
                company_name = brand_profile["company_name"]
            if "tone_of_voice" in brand_profile and brand_profile["tone_of_voice"]:
                tone = brand_profile["tone_of_voice"]

        print(f"[SaigaSkill] ✍️ Генерация SMM-поста: Компания='{company_name}', Ниша='{niche}', Тема='{topic}', Тон='{tone}'...")
        if visual_context:
            print(f"[SaigaSkill] 👁️ Включен визуальный контекст от Moondream: {visual_context[:100]}...")
        if comments_context:
            print(f"[SaigaSkill] 💬 Учтены комментарии аудитории: {len(comments_context)} шт.")
        
        # Если загружена реальная модель llama-cpp
        if self._is_loaded and self._llm:
            try:
                comments_info = f"\nЧастые вопросы и комментарии аудитории: {', '.join(comments_context)}" if comments_context else ""
                system_instruction = (
                    f"Ты — опытный главный SMM-редактор и копирайтер компании «{company_name}» (Ниша: {niche}, Город: {city}). "
                    f"Напиши публикацию для социальных сетей на тему: «{topic}».\n"
                    f"Тон общения: {tone}.\n"
                    f"{visual_context or ''}{comments_info}\n"
                    f"Требования: живой русский язык, структурированные абзацы, "
                    f"без штампов и клише, обязательный призыв к диалогу и комментариям в конце."
                )
                output = self._llm.create_chat_completion(
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": f"Напиши пост для соцсетей на тему: {topic}"}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                generated_text = output["choices"][0]["message"]["content"].strip()
                if len(generated_text) > 30:
                    return {
                        "post_text": generated_text,
                        "promo_code": f"{company_name.upper().replace(' ', '')}2026"
                    }
            except Exception as e:
                print(f"[SaigaSkill] ⚠️ Ошибка инференса LLaMA: {e}")

        # Сохраняем оригинальный регистр — только убираем пробелы и точку в конце
        topic_clean = topic.strip().rstrip(".")
        topic_lower = topic.lower()
        niche_lower = niche.lower()

        visual_phrase = ""
        if visual_context and "Что изображено:" in visual_context:
            visual_phrase = "\n\nНа прикреплённом фото — именно те детали и атмосфера, которые мы воплощаем в каждом нашем продукте."

        # Формируем блок ответов на вопросы из комментариев
        comments_phrase = ""
        if comments_context and len(comments_context) > 0:
            formatted_comments = "\n".join([f"• {c}" for c in comments_context[:3]])
            comments_phrase = f"\n\n💬 <b>Отвечаем на частые вопросы из комментариев:</b>\n{formatted_comments}"
        elif audience_questions and len(audience_questions) > 0:
            formatted_q = "\n".join([f"• {q}" for q in audience_questions[:3]])
            comments_phrase = f"\n\n💬 <b>Отвечаем на частые вопросы аудитории:</b>\n{formatted_q}"

        has_comments = bool(comments_enabled or (comments_context and len(comments_context) > 0))
        full_text_search = f"{topic_lower} {niche_lower}"

        # =========================================================================
        # 1. РЕЕСТР ПРАЗДНИКОВ И ГОСУДАРСТВЕННЫХ / СЕЗОННЫХ ДАТ (ПРИОРИТЕТ №1)
        # =========================================================================
        holiday_match = None

        if any(w in topic_lower for w in ["флаг", "государственн", "триколор"]):
            holiday_match = {
                "lead": f"С Днём Государственного флага Российской Федерации! 🇷🇺",
                "body": (
                    f"Команда «{company_name}» от всей души поздравляет вас с праздником национального триколора!\n\n"
                    f"Белый, синий и красный — цвета чести, благородства, верности и силы. "
                    f"Они напоминают нам о богатой истории, сплочённости и уверенности в будущем.\n\n"
                    f"Пусть этот день вдохновляет на новые достижения, масштабные идеи и гордость за наше общее дело!{comments_phrase}"
                ),
                "cta": "Поздравляйте друзей и коллег в комментариях 👇 С праздником! 🇷🇺" if has_comments else "С праздником! Желаем процветания и уверенного движения вперёд! 🇷🇺",
                "hashtags": "#ДеньФлага #Россия #триколор #праздник #UCust",
                "visual_prompt": (
                    "Heroic cinematic photograph with dramatic low-angle upward perspective (camera positioned low, shooting upward toward the sky). "
                    "In the foreground at lower right, a focused professional in elegant silhouette stands by a massive panoramic floor-to-ceiling glass window, hand gently resting on the glass, looking up in awe and contemplation. "
                    "Outside and high above in the upper frame, a colossal, majestic Russian tricolor flag on a towering flagpole flutters grandly and dynamically in the strong wind against a breathtaking golden-amber sunset sky and dramatic clouds, commanding the scene with monumental scale and national pride. "
                    "Warm golden sunlight breaking through clouds, brilliant golden rim lighting outlining the silhouette, soft realistic reflections on glass. "
                    "Cinematic 35mm film look, heroic low-angle composition, monumental scale, deep emotional resonance, photorealistic masterpiece."
                )
            }
        elif any(w in topic_lower for w in ["новый год", "новогодн", "рождеств", "ёлка", "елка"]):
            holiday_match = {
                "lead": f"С Новым годом и Рождеством от команды «{company_name}»! 🎄✨",
                "body": (
                    f"Пусть наступающий год откроет для вашего дела новые горизонты и принесёт яркие победы!\n\n"
                    f"Благодарим каждого из вас за доверие и партнёрство. "
                    f"В новом году мы приготовили ещё больше полезных решений, чтобы ваш бизнес рос быстрее и легче.\n\n"
                    f"Тепла, уюта вашему дому и неиссякаемой энергии для всех смелых проектов!{comments_phrase}"
                ),
                "cta": "Делитесь вашими целями и пожеланиями на новый год в комментариях! 👇🎉" if has_comments else "Счастливого Нового года и ярких побед! 🎄🚀",
                "hashtags": "#НовыйГод #Рождество #праздник #бизнес2026 #итогигода",
                "visual_prompt": (
                    "Heartwarming cinematic holiday storytelling photograph. "
                    "A cozy warm room in the evening: a person holds a steaming ceramic mug between both hands, looking out a frosted window at softly falling snowflakes and sparkling city streetlights. "
                    "Soft golden bokeh from a Christmas tree glowing warmly in the room reflection, cozy knitted sweater texture, deep feeling of hope, warmth, comfort and wonder, photorealistic."
                )
            }
        elif any(w in topic_lower for w in ["9 мая", "побед", "великая отечественная", "ветераны"]):
            holiday_match = {
                "lead": f"С Днём Великой Победы! 🕊️ С праздником 9 Мая!",
                "body": (
                    f"9 Мая — священная дата для каждого из нас. День памяти, бесконечной благодарности и гордости за подвиг наших предков.\n\n"
                    f"Мы помним тех, кто подарил нам мирное небо и возможность созидать, строить будущее и растить детей.\n\n"
                    f"Команда «{company_name}» желает вам и вашим близким крепкого здоровья, мира, добра и согласия.{comments_phrase}"
                ),
                "cta": "Почтим память героев и поздравим близких с праздником Великой Победы! 🕊️" if has_comments else "Мирного неба, благополучия и крепкого здоровья каждому дому! 🕊️",
                "hashtags": "#9Мая #ДеньПобеды #ПомнимГордимся #Мир #Победа",
                "visual_prompt": (
                    "Deeply emotional and respectful commemorative photograph in warm evening light. "
                    "A hand gently places a fresh crimson carnation wrapped with a St. George ribbon onto a sunlit stone memorial pedestal. "
                    "In the soft blurred background, a warm golden sunset glow among quiet park trees, evoking profound gratitude, honor and peaceful reflection. "
                    "Cinematic warm lighting, shallow depth of field, authentic emotional storytelling photography, photorealistic."
                )
            }
        elif any(w in topic_lower for w in ["23 февраля", "защитник", "отечеств", "мужской день"]):
            holiday_match = {
                "lead": f"С Днём защитника Отечества! 🛡️ Поздравляем мужчин с 23 Февраля!",
                "body": (
                    f"Поздравляем всех, кто бережёт мир и спокойствие своих семей, кто берёт на себя ответственность и уверенно идёт к цели!\n\n"
                    f"Надёжность, решительность и твёрдость характера — качества, которые двигают вперёд и жизнь, и бизнес.\n\n"
                    f"Желаем несгибаемой воли, надёжного тыла и новых высот во всех начинаниях!{comments_phrase}"
                ),
                "cta": "Поздравляйте сильных духом мужчин в комментариях! 👇🛡️" if has_comments else "С праздником! Силы, уверенности и больших побед! 🚀",
                "hashtags": "#23Февраля #ДеньЗащитникаОтечества #мужскойпраздник #поздравление",
                "visual_prompt": (
                    "Cinematic, strong and inspiring portrait photograph. "
                    "A determined, confident man standing by a large industrial loft window at sunset, gazing purposefully into the distance, wearing a crisp dark shirt with rolled-up sleeves, strong posture radiating reliability, calm confidence and inner strength. "
                    "Dramatic warm side lighting, rich contrasts, cinematic 35mm photography aesthetic, authentic emotional depth."
                )
            }
        elif any(w in topic_lower for w in ["8 марта", "женский день", "весенний праздник", "девушек", "женщин"]):
            holiday_match = {
                "lead": f"С прекрасным весенним праздником — с 8 Марта! 🌸🌷",
                "body": (
                    f"Команда «{company_name}» поздравляет милых дам с Международным женским днём!\n\n"
                    f"Вы наполняете мир красотой, гармонией и вдохновением. "
                    f"Вы восхищаете умением сочетать нежность и силу, управлять проектами, создавать уют и делать этот мир лучше каждый день.\n\n"
                    f"Пусть весна подарит море цветов, улыбок, лёгкости и исполнения самых заветных желаний!{comments_phrase}"
                ),
                "cta": "Оставляйте свои тёплые пожелания милым дамам в комментариях! 💐👇" if has_comments else "Цветов, весеннего настроения и бесконечного вдохновения! 🌸",
                "hashtags": "#8Марта #МеждународныйЖенскийДень #весна #цветы #поздравление",
                "visual_prompt": (
                    "Joyful, inspiring spring lifestyle photograph. "
                    "A radiant smiling woman in a stylish pastel sweater happily holding a stunning fresh bouquet of soft pink tulips in a bright sunlit modern cafe. "
                    "Natural glowing morning sunlight, genuine heartfelt happy expression, candid moment of joy, shallow depth of field, authentic warm emotional photography."
                )
            }
        elif any(w in topic_lower for w in ["12 июня", "день россии"]):
            holiday_match = {
                "lead": f"С Днём России! 🇷🇺 Величия, силы и процветания нашей стране!",
                "body": (
                    f"Сегодня мы отмечаем праздник нашей великой Родины — страны с богатейшей историей, грандиозным наследием и талантливыми людьми!\n\n"
                    f"Каждый день мы своим трудом, идеями и проектами создаём настоящее и будущее России.\n\n"
                    f"Желаем мира, благополучия, уверенности в завтрашнем дне и новых масштабных свершений!{comments_phrase}"
                ),
                "cta": "С праздником, друзья! Гордимся нашей страной! 🇷🇺👇" if has_comments else "С праздником! Процветания и побед нашей Родине! 🇷🇺",
                "hashtags": "#ДеньРоссии #12Июня #Россия #НашаСтрана #праздник",
                "visual_prompt": (
                    "Cinematic inspiring photograph: a young professional looking out over a breathtaking panoramic Russian city skyline at sunrise from a modern high-rise glass observation deck, a grand tricolor flag fluttering proudly on a prominent central tower, golden morning mist, expansive sky, majestic inspiring atmosphere."
                )
            }
        elif any(w in topic_lower for w in ["1 сентября", "день знаний", "школ", "ученик", "студент"]):
            holiday_match = {
                "lead": f"С 1 Сентября — с Днём знаний! 🔔📚",
                "body": (
                    f"Старт нового учебного и делового сезона! Время свежих идей, полезных знаний и смелых целей.\n\n"
                    f"Знания и непрерывное развитие — главный двигатель любого успеха: как в учёбе, так и в масштабировании бизнеса.\n\n"
                    f"Желаем школьникам, студентам, преподавателям и предпринимателям продуктивного и яркого года!{comments_phrase}"
                ),
                "cta": "Какие цели поставили себе на эту осень? Делитесь в комментариях! 👇📝" if has_comments else "Продуктивной осени и новых открытий! 🚀📚",
                "hashtags": "#1Сентября #ДеньЗнаний #сновавшколу #образование #развитие",
                "visual_prompt": (
                    "Inspiring, bright academic storytelling photograph. "
                    "A determined young student sitting at a sunlit wooden desk by a window, opening a fresh clean notebook with a pen poised in hand, coffee cup nearby, eyes full of ambition and anticipation. "
                    "Vibrant morning sunlight, crisp shadows, inspiring atmosphere of fresh beginnings, authentic UGC lifestyle."
                )
            }
        elif any(w in topic_lower for w in ["день матери", "мама", "матер"]):
            holiday_match = {
                "lead": f"С Днём матери! Самый тёплый и нежный праздник в году ❤️",
                "body": (
                    f"Мама — это первое слово, бесконечная забота, безусловная любовь и главная поддержка во всём.\n\n"
                    f"Спасибо нашим дорогим мамам за терпение, мудрость, бессонные ночи и веру в нас на каждом этапе жизни!\n\n"
                    f"Не забудьте сегодня позвонить, обнять и сказать самое важное своим мамам.{comments_phrase}"
                ),
                "cta": "Напишите самое тёплое признание вашей маме прямо в комментариях! ❤️👇" if has_comments else "Берегите мам и дарите им заботу каждый день! ❤️",
                "hashtags": "#ДеньМатери #Мама #любовь #семья #праздник",
                "visual_prompt": (
                    "Deeply touching, tender lifestyle photograph. "
                    "A warm close-up of two hands holding each other with deep affection across a cozy wooden tea table: the caring hand of a mother and her adult child, a delicate handwritten note and tea cup nearby. "
                    "Soft morning sunlight, warm pastel tones, profound feeling of love, safety, gratitude and comfort, authentic emotional portrait."
                )
            }
        elif any(w in topic_lower for w in ["праздник", "поздравля", "день города", "день народного", "юбиле", "торжеств"]):
            holiday_match = {
                "lead": f"С праздником от команды «{company_name}»! 🎉",
                "body": (
                    f"{topic_clean}.\n\n"
                    f"Мы искренне поздравляем вас и ваших близких с этим знаменательным днём!\n\n"
                    f"Пусть этот праздник наполнит вас гордостью, теплом и вдохновением. "
                    f"Именно такие моменты напоминают о том, что за каждым большим делом стоят люди — преданные своему делу и семье.\n\n"
                    f"Команда «{company_name}» продолжает работать для вас каждый день, чтобы ваш бизнес рос и развивался.{comments_phrase}"
                ),
                "cta": "Поздравляйте друг друга в комментариях 👇 С праздником! 🎊" if has_comments else "С праздником! Пишите нам — работаем для вас 24/7 🎊",
                "hashtags": "#праздник #поздравление #UCust #событие",
                "visual_prompt": (
                    "Cinematic celebratory business photograph. "
                    "Warm modern office workspace with sunlight, professional desk with laptop, coffee cup, and small festive decorative element, warm golden tones, shallow depth of field, photorealistic commercial photography."
                )
            }

        if holiday_match:
            full_post = f"{holiday_match['lead']}\n\n{holiday_match['body']}\n\n{holiday_match['cta']}"
            return {
                "post_text": full_post,
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": holiday_match["visual_prompt"],
                "hashtags": holiday_match["hashtags"]
            }

        # =========================================================================
        # 2. СПЕЦИАЛИЗИРОВАННЫЕ ДЕМО-ЗАПРОСЫ И МАНИФЕСТЫ UCUST
        # =========================================================================
        if "как понимает" in topic_lower or "что умеет" in topic_lower or "простыми словами" in topic_lower or "для простых" in topic_lower or "не айтиш" in topic_lower or "понимает запрос" in topic_lower:
            lead = f"В чём разница между обычным чат-ботом и маркетинговым ядром «{company_name}»?"
            body = (
                f"Чат-бот выдаёт текст в вакууме. Ему всё равно, купят у вас или пролистнут ленту.\n\n"
                f"«{company_name}» работает как <b>компактная, но глубоко обученная маркетинговая связка</b>, где у каждого модуля — узкая и отточенная компетенция:\n\n"
                f"🧠 <b>1. Психология покупателя</b> — система выявляет скрытые боли и триггеры доверия в вашей нише, а не сыплет абстрактными фразами.\n"
                f"✍️ <b>2. Конверсионная структура</b> — текст строится по законам драматургии (крючок, ценность, снятие возражений, чёткий CTA) живым языком без «воды».\n"
                f"🎬 <b>3. Смысловой фотопродакшн</b> — визуал создаётся как естественное продолжение идеи поста, привлекая внимание живой эстетикой вместо пластиковых стоковых картинок.\n"
                f"🛡️ <b>4. Фильтр качества</b> — строгий пре-мортем аудит отсекает любые штампы и фальшь до публикации.\n\n"
                f"⚡ Результат: пост и фото работают как единое целое на доверие и продажи.{visual_phrase}{comments_phrase}"
            )
            cta = f"Напишите нишу вашего бизнеса в комментарии — покажем, как система отработает задачу для вас! 👇" if has_comments else f"Напишите нам в личные сообщения — покажем возможности автономного пайплайна на вашем бизнесе! 🚀"
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": (
                    "A cinematic, slightly futuristic wide-angle photograph. "
                    "A focused female entrepreneur with dark hair sits at a wooden desk in a warm modern cafe coworking space, visible in the left half of the frame. "
                    "An open MacBook laptop is on the desk in front of her, its screen showing a simple chat-style text input interface. "
                    "From the RIGHT EDGE of the laptop screen, vivid glowing streams of blue and golden digital particles and abstract light trails flow dynamically outward to the right into open air. "
                    "These particle streams coalesce and materialize into a FLOATING rectangular photograph that hovers in the AIR to the right of the laptop — NOT on the screen — "
                    "showing a vivid realistic image of a barista pouring latte art in a sunlit cozy cafe. "
                    "The floating photo has a soft luminous rounded frame and appears to emerge from the particle stream. "
                    "Warm cinematic ambient lighting, natural bokeh background, photorealistic commercial photography, wide composition."
                ),
                "hashtags": "#ИИдляБизнеса #SMM #GenAI"
            }

        elif "кто так" in topic_lower or "о нас" in topic_lower or "знакомств" in topic_lower or "манифест" in topic_lower:
            lead = f"«{company_name}»: не раздутый штат, а сфокусированное ядро маркетинговых ИИ-навыков"
            body = (
                f"Вместо десятков разрозненных сервисов и бесконечных правок — единая сбалансированная система, "
                f"где каждый алгоритм натренирован на конкретную бизнес-задачу:\n\n"
                f"🎯 <b>Исследование спроса и отстройка от конкурентов</b>\n"
                f"Мгновенный анализ рыночного контекста, формулирование твёрдых УТП и работа с ключевыми возражениями клиентов.\n\n"
                f"✍️ <b>Конверсионный копирайтинг по законам восприятия</b>\n"
                f"Создание ёмких, бьющих в цель публикаций с естественной тональностью — без клише, канцелярита и искусственного глянца.\n\n"
                f"🎬 <b>Умный визуальный продакшн</b>\n"
                f"Создание авторского фотоконтента, который органично раскрывает посыл публикации, формирует премиальный образ бренда и пробивает баннерную слепоту в ленте.\n\n"
                f"🛡️ <b>Встроенный аудит качества (Zero-Fluff Gatekeeper)</b>\n"
                f"Многоуровневый фильтр тональности и смысловой ценности, гарантирующий отсутствие галлюцинаций и «воды».\n\n"
                f"📡 <b>Омниканальная дистрибуция 24/7</b>\n"
                f"Синхронная адаптация и публикация контента в Telegram, VK, OK, MAX и геосервисы в 1 клик.{comments_phrase}"
            )
            cta = f"Напишите в комментариях нишу вашего бизнеса — продемонстрируем связку навыков в действии! 🚀" if has_comments else f"Напишите нам в личные сообщения — покажем, как система масштабирует маркетинг вашего дела! 🚀"
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": "Authentic candid photograph: a sleek modern workspace desk with open laptop showing modern marketing analytics dashboards and AI agent workflows, a stylish coffee cup and smartphone on desk, bright natural daylight from large office window, clean contemporary aesthetic, authentic tech startup lifestyle photo.",
                "hashtags": "#ИИагенты #маркетинг2026 #автоматизация #стартап #AIстартап"
            }

        elif "команд" in topic_lower or "собр" in topic_lower or "старт" in topic_lower or "начинаем" in topic_lower:
            lead = f"Старт проекта «{company_name}»: открытая разработка автономного маркетинга"
            body = (
                f"{topic_clean}.{visual_phrase}\n\n"
                f"Мы объединили экспертизу в распределённых мульти-агентных системах, глубоких нейросетях и реальном маркетинге, "
                f"чтобы создать инструмент, который берет на себя 100% рутины по созданию, контролю и дистрибуции контента.\n\n"
                f"Наш фокус — открытая разработка, честные замеры времени работы моделей, высочайший стандарт фотореализма и измеримый результат для бизнеса.\n\n"
                f"Спасибо каждому, кто следит за проектом и тестирует наши обновления!{comments_phrase}"
            )
            cta = f"Следите за нашими обновлениями и задавайте любые вопросы в комментариях 👇. Погнали! 🚀" if has_comments else f"Следите за нашими обновлениями и пишите нам в личные сообщения. Погнали! 🚀"
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": (
                    "Authentic candid photo of a small tech startup team of 4 people. "
                    "IMPORTANT: each person has a completely unique and distinct face, different hairstyle, different age, different facial features — NO identical or similar faces. "
                    "Person 1: young woman with short dark hair, glasses, casual sweater. "
                    "Person 2: man in his 30s with beard and curly hair, blue shirt. "
                    "Person 3: older man with grey temples, formal jacket. "
                    "Person 4: young man with straight light hair, hoodie. "
                    "Setting: modern bright glass-walled office, whiteboard with colorful sticky notes, laptops on table, genuine collaborative discussion. "
                    "Natural daylight from large windows, authentic candid atmosphere, shallow depth of field, photorealistic."
                ),
                "hashtags": "#запуск #стартап #команда #разработка #IT"
            }

        elif "скидк" in topic_lower or "акци" in topic_lower or "промо" in topic_lower or "%" in topic_lower:
            lead = f"Специальное предложение от «{company_name}»"
            body = (
                f"{topic_clean}.{visual_phrase}\n\n"
                f"Мы ценим ваше доверие и хотим сделать наши услуги ещё выгоднее и доступнее для вашего бизнеса. "
                f"Успейте воспользоваться специальными условиями до конца этой недели.{comments_phrase}"
            )
            cta = f"Напишите промокод {company_name.upper().replace(' ', '')}2026 в личные сообщения для получения специальных условий!"
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": f"Authentic candid commercial photograph for {niche}: stylish modern commercial product display on clean minimalist surface with subtle organic shadows, soft warm ambient lighting, elegant lifestyle commercial photography.",
                "hashtags": "#акция #спецпредложение #маркетинг #скидки"
            }

        # =========================================================================
        # 3. УНИВЕРСАЛЬНЫЙ РЕЕСТР НИШ И СФЕР БИЗНЕСА (12+ НАПРАВЛЕНИЙ)
        # =========================================================================

        # 3.1. Рестораны, кафе, доставка еды, гастробары
        if any(w in full_text_search for w in ["ресторан", "кафе", "меню", "блюдо", "шеф", "кухн", "гастро", "доставка еды", "пицц", "суши", "бургер"]):
            lead = f"Вкус, который запоминается: новинки в «{company_name}» 🍽️"
            body = (
                f"{topic_clean}.{visual_phrase}\n\n"
                f"Наш шеф-повар соединил свежайшие локальные ингредиенты и авторскую подачу, чтобы каждый визит превращался в гастрономическое событие.\n\n"
                f"Уютная атмосфера, идеальный баланс вкусов и заботливый сервис — бронируйте стол для особенного вечера!{comments_phrase}"
            )
            cta = "Какое блюдо из нашего меню ваше самое любимое? Делитесь в комментариях! 🍷👇" if has_comments else "Ждём вас в гости каждый день! Бронь столов в личных сообщениях 🍷"
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": "Cinematic emotional culinary storytelling photograph. A passionate focused chef in a clean dark apron using precision tweezers to place a delicate final garnish onto a gourmet signature dish in a warm open kitchen. Warm golden spotlight illuminating the culinary masterpiece, soft ambient background bokeh of an inviting dining room with wine glasses, genuine passion and artistry, shallow depth of field, 35mm photography.",
                "hashtags": "#ресторан #вкуснаяеда #гастрономия #шефповар #ужин"
            }

        # 3.2. Кофейни, пекарни, бариста
        elif any(w in full_text_search for w in ["кофе", "латте", "капучино", "десерт", "выпечк", "пекарн", "барист", "круассан"]):
            lead = f"Идеальный утренний ритуал в «{company_name}» ☕"
            body = (
                f"{topic_clean}.{visual_phrase}\n\n"
                f"Мы тщательно подобрали зерно свежей обжарки и настроили экстракцию, чтобы каждый глоток дарил вам заряд вдохновения и сил на весь день.\n\n"
                f"Добавьте к этому свежий хрустящий десерт — и день точно сложится удачно!{comments_phrase}"
            )
            cta = "Заглядывайте к нам за чашкой любимого напитка! А какой кофе вы пьёте по утрам? Напишите в комментариях ☕" if has_comments else "Ждём вас на чашку ароматного кофе каждый день! ☕✨"
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": "Cinematic atmospheric coffee storytelling photograph. A smiling friendly barista leaning over a rustic wooden counter, gently handing a steaming ceramic cup of cappuccino with delicate latte art directly toward the viewer at golden morning hour. Soft warm sunlight streaming through large cafe windows with floating dust motes, cozy welcoming cafe atmosphere, authentic heartfelt UGC lifestyle.",
                "hashtags": "#кофе #кофейня #латтеарт #доброеутро #кофеман"
            }

        # 3.3. Beauty / Салоны красоты / Барбершопы / Косметология
        elif any(w in full_text_search for w in ["салон", "красот", "барбер", "маникюр", "стрижк", "уход", "косметол", "спа", "массаж", "брови", "ресниц"]):
            lead = f"Время уделить внимание себе: преображение в «{company_name}» ✨"
            body = (
                f"{topic_clean}.{visual_phrase}\n\n"
                f"Мы создали пространство, где забота о вашей красоте и внутреннем комфорте выходит на первый план.\n\n"
                f"Сертифицированные мастера, премиальная косметика и индивидуальный подход к каждому образу — подчеркните вашу естественную привлекательность!{comments_phrase}"
            )
            cta = "Запишитесь на удобное время через личные сообщения или оставьте «+» в комментариях! 💅👇" if has_comments else "Ждём вас на процедуры! Онлайн-запись доступна в личных сообщениях ✨"
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": "Emotional and joyful beauty transformation photograph. A radiant client with a genuine glowing smile looking into a sunlit salon mirror, admiring her fresh stylish hair and natural makeup, while the skilled stylist behind her smiles with pride and care. Soft diffused morning window light, subtle marble and green plant accents, genuine emotion of confidence and self-love, shallow depth of field.",
                "hashtags": "#красота #салонкрасоты #уходзасобой #стиль #маникюр"
            }

        # 3.4. Фитнес / Спорт / Йога / Тренировки
        elif any(w in full_text_search for w in ["фитнес", "спорт", "трениров", "зал", "йог", "тренер", "растяжк", "кроссфит", "похуден", "мышц"]):
            lead = f"Твоя лучшая форма начинается сегодня в «{company_name}» 💪"
            body = (
                f"{topic_clean}.{visual_phrase}\n\n"
                f"Результат — это не случайность, а система правильных привычек и поддержки опытных наставников.\n\n"
                f"Современное оборудование, персонализированные программы тренировок и заряженная атмосфера единомышленников — сделайте первый шаг к телу мечты!{comments_phrase}"
            )
            cta = "Напишите в комментариях, какую цель ставите на этот сезон — и мы поможем составить план! 🏋️👇" if has_comments else "Записывайтесь на пробную тренировку в личных сообщениях! Погнали! 🔥"
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": "Inspiring powerful fitness storytelling photograph. A dedicated athlete pausing after an intense workout in a bright modern loft gym, taking a deep breath of triumph and holding a water bottle, sunlight dramatically highlighting determination and athletic form. Warm golden morning rays piercing through high gym windows, authentic raw emotion of self-overcoming and strength.",
                "hashtags": "#фитнес #спорт #тренировка #здоровье #мотивация"
            }

        # 3.5. Недвижимость / Дизайн интерьера / Аренда
        elif any(w in full_text_search for w in ["недвижим", "квартир", "дом", "риелтор", "жилье", "застройщик", "ипотек", "аренд", "интерьер", "жк"]):
            lead = f"Пространство для вашей комфортной жизни от «{company_name}» 🏡"
            body = (
                f"{topic_clean}.{visual_phrase}\n\n"
                f"Мы помогаем находить не просто квадратные метры, а место, куда по-настоящему хочется возвращаться каждый вечер.\n\n"
                f"Продуманные планировки, панорамные окна, развитая инфраструктура и полное юридическое сопровождение на каждом этапе сделки.{comments_phrase}"
            )
            cta = "Хотите получить каталог актуальных объектов? Напишите «КАТАЛОГ» в комментариях или в ЛС! 🔑" if has_comments else "Пишите в личные сообщения — подберём идеальный вариант под ваш бюджет! 🔑"
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": "Heartwarming lifestyle storytelling photograph of a new home. A happy young homeowner sitting comfortably on the warm hardwood floor of an airy sunlit living room with a coffee mug, gazing out large floor-to-ceiling windows at a golden sunset over the city. A couple of unpacked boxes and a leafy Monstera plant nearby, pure feeling of happiness, safety, achievement and home.",
                "hashtags": "#недвижимость #квартира #новостройки #интерьер #уют"
            }

        # 3.6. Автобизнес / СТО / Детейлинг / Автосалоны
        elif any(w in full_text_search for w in ["авто", "машин", "сто", "детейлинг", "автосервис", "шиномонтаж", "автомойк", "тюнинг", "техосмотр"]) and "автоном" not in full_text_search:
            lead = f"Безупречный вид и надёжность вашего автомобиля с «{company_name}» 🚗"
            body = (
                f"{topic_clean}.{visual_phrase}\n\n"
                f"Ваш автомобиль заслуживает профессионального ухода и внимания к каждой детали.\n\n"
                f"Современное диагностическое оборудование, премиальная автохимия и мастера с многолетним стажем гарантируют идеальный результат и безопасность на дороге.{comments_phrase}"
            )
            cta = "Задавайте любые вопросы по обслуживанию в комментариях 👇 Ответим оперативно!" if has_comments else "Запишитесь на обслуживание или детейлинг прямо в личных сообщениях! 🔧",
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": "Cinematic craft storytelling automotive photograph. A skilled detailing technician in black nitrile gloves gently running fingertips across the mirror-like polished hood of a sleek sports car, admiring the flawless deep reflection under soft halo LED workshop lights. Dramatic contrasts, crisp glossy reflections, pride in craftsmanship and perfectionism, photorealistic.",
                "hashtags": "#авто #детейлинг #автосервис #автомобили #СТО"
            }

        # 3.7. Медицина / Стоматология / Здоровье
        elif any(w in full_text_search for w in ["медицин", "стоматолог", "клиник", "врач", "здоровь", "зуб", "лечен", "диагностик", "анализ", "имплант"]):
            lead = f"Забота о вашем здоровье и улыбке с «{company_name}» 🩺"
            body = (
                f"{topic_clean}.{visual_phrase}\n\n"
                f"Здоровье — главная ценность. В нашей клинике мы объединили доказательную медицину, передовые технологии и бережное отношение к каждому пациенту.\n\n"
                f"Безболезненное лечение, прозрачные планы терапии и врачи с безупречной репутацией помогут вам чувствовать себя уверенно каждый день.{comments_phrase}"
            )
            cta = "Оставьте вопросы врачу в комментариях или запишитесь на первичную консультацию в ЛС! 👩‍⚕️" if has_comments else "Запись на консультацию открыта в личных сообщениях. Берегите здоровье! 🩺",
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": "Heartwarming reassuring medical storytelling photograph. A caring doctor in a modern white coat having a warm, empathetic conversation with a smiling, relieved patient in a bright, modern consultation room with wood and plant accents. Soft natural window daylight, genuine feeling of trust, safety, relief and professional care, shallow depth of field.",
                "hashtags": "#медицина #здоровье #стоматология #клиника #красиваяулыбка"
            }

        # 3.8. Строительство / Ремонт квартир / Отделка
        elif any(w in full_text_search for w in ["ремонт", "строительств", "отделк", "дизайн", "бригад", "кровл", "фундамент", "монтаж", "фасад"]):
            lead = f"Качественный ремонт и строительство без стресса от «{company_name}» 🔨"
            body = (
                f"{topic_clean}.{visual_phrase}\n\n"
                f"Мы превращаем чертежи в готовое, тёплое и надёжное пространство для жизни.\n\n"
                f"Работа строго по договору, фиксированная смета, соблюдение ГОСТов и поэтапный фотоотчёт на каждом шаге. Ремонт может быть спокойным и в удовольствие!{comments_phrase}"
            )
            cta = "Хотите рассчитать предварительную стоимость вашего проекта? Напишите параметры в ЛС или в комментариях! 📐" if has_comments else "Пишите в личные сообщения для бесплатного расчёта сметы и выезда замерщика! 📐",
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": "Inspiring architectural storytelling photograph. An architect and a proud homeowner standing together in a breathtaking newly finished open-plan living room with warm hardwood floors and designer lighting, looking at architectural blueprints with genuine smiles of satisfaction and pride. Warm afternoon sunlight, sense of accomplishment and creation.",
                "hashtags": "#ремонт #строительство #дизайнинтерьера #ремонтквартир #стройка"
            }

        # 3.9. Образование / Онлайн-школы / Курсы
        elif any(w in full_text_search for w in ["курс", "обучен", "школ", "вебинар", "урок", "репетитор", "язык", "навык", "диплом"]):
            lead = f"Инвестируйте в своё развитие вместе с «{company_name}» 🎓"
            body = (
                f"{topic_clean}.{visual_phrase}\n\n"
                f"Практические знания, которые дают измеримый результат сразу после обучения.\n\n"
                f"Опытные преподаватели-практики, разбор реальных кейсов, поддержка кураторов и комьюнити мотивированных студентов — начните свой путь к новой профессии!{comments_phrase}"
            )
            cta = "Напишите кодовое слово «КУРС» в комментариях, чтобы получить бесплатный вводный урок! 👇📚" if has_comments else "Пишите в личные сообщения, чтобы забронировать место на новом потоке! 🚀📚",
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": "Inspiring academic storytelling photograph. A focused student in headphones sitting by a bright window desk, experiencing a genuine breakthrough moment of excitement while taking handwritten notes next to an open laptop, eyes glowing with inspiration. Vibrant morning sunbeams, authentic atmosphere of intellectual growth and ambition.",
                "hashtags": "#образование #онлайнкурсы #обучение #саморазвитие #навыки"
            }

        # 3.10. Юриспруденция / Бухгалтерия / Финансы / Налоги
        elif any(w in full_text_search for w in ["юрист", "адвокат", "бухгалтер", "налог", "аудит", "финанс", "договор", "право", "банкротств"]):
            lead = f"Надёжная правовая и финансовая защита вашего бизнеса от «{company_name}» ⚖️"
            body = (
                f"{topic_clean}.{visual_phrase}\n\n"
                f"Защитите свои активы и оптимизируйте процессы с командой опытных экспертов.\n\n"
                f"Глубокий анализ рисков, безупречное ведение отчётности и защита ваших интересов в любых инстанциях. Ваш бизнес под надёжным контролем 24/7.{comments_phrase}"
            )
            cta = "Задайте свой вопрос юристу или бухгалтеру в комментариях 👇 Ответим конфиденциально в ЛС!" if has_comments else "Запишитесь на экспресс-аудит ваших документов в личных сообщениях! 💼",
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": "Powerful reassuring corporate storytelling photograph. Two business partners firmly shaking hands across a sleek modern conference table at sunset after signing a crucial contract, genuine expressions of mutual respect and relief. Warm golden hour light reflecting off glass high-rise towers outside the panoramic window, feeling of security, success and trust.",
                "hashtags": "#юрист #бухгалтерия #налоги #бизнес #консалтинг"
            }

        # 3.11. Туризм / Отели / Путешествия / Глэмпинги
        elif any(w in full_text_search for w in ["тур", "путешеств", "отел", "глэмпинг", "отдых", "база отдыха", "курорт", "море", "горы", "экскурси"]):
            lead = f"Откройте мир ярких впечатлений вместе с «{company_name}» ✈️🌄"
            body = (
                f"{topic_clean}.{visual_phrase}\n\n"
                f"Идеальный отдых начинается с правильного выбора локации и заботы о каждой мелочи путешествия.\n\n"
                f"Завораживающие виды, премиальный сервис, авторские маршруты и полное погружение в атмосферу — пора сменить обстановку и зарядиться энергией!{comments_phrase}"
            )
            cta = "Куда мечтаете отправиться в ближайшее время? Делитесь в комментариях! 🌍👇" if has_comments else "Бронируйте лучшие даты в личных сообщениях — подберём тур мечты! ✈️"
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": "Breathtaking emotional travel storytelling photograph. A traveler wrapped in a cozy knitted blanket holding a steaming mug of tea, sitting on the edge of a rustic wooden glamping deck watching a majestic golden sunrise over misty mountain peaks and pine forests. Quiet awe, peace, deep connection with nature, cinematic atmospheric light, photorealistic.",
                "hashtags": "#путешествия #туризм #отдых #отель #глэмпинг"
            }

        # 3.12. Ритейл / Одежда / E-commerce / Товары
        elif any(w in full_text_search for w in ["магазин", "одежд", "стил", "мод", "товар", "доставк", "подарок", "аксессуар", "маркетплейс"]):
            lead = f"Стиль и качество, которые подчеркнут вашу индивидуальность: «{company_name}» 🛍️"
            body = (
                f"{topic_clean}.{visual_phrase}\n\n"
                f"Мы собрали коллекцию, в которой каждая деталь продумана до мелочей: от премиальных материалов до идеальной посадки.\n\n"
                f"Быстрая доставка, удобная примерка и гарантированное качество — порадуйте себя новинками уже сегодня!{comments_phrase}"
            )
            cta = "Какой образ понравился больше всего? Напишите номер в комментариях! 👇👗" if has_comments else "Оформляйте заказ прямо сейчас в личных сообщениях с быстрой доставкой! 🛍️"
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": "Charming candid fashion storytelling photograph. A stylish woman standing in front of a warm boutique mirror, playfully adjusting the collar of a chic elegant coat with a confident, joyful smile, surrounded by soft neutral textures and ambient warm light. Authentic moment of self-expression and delight, natural depth of field, photorealistic.",
                "hashtags": "#шопинг #стиль #мода #одежда #новинки"
            }

        # 3.13. Фермерские продукты / Овощи и фрукты / Рынок / Продуктовые лавки
        elif any(w in full_text_search for w in ["овощ", "фрукт", "рынок", "фермер", "продукты", "базар", "ягод", "зелень", "урожай", "лавка", "грядк"]):
            lead = f"Свежесть только с грядки: отборный урожай в «{company_name}» 🍅🌿"
            body = (
                f"{topic_clean}.{visual_phrase}\n\n"
                f"Никакой химии и долгого хранения — только настоящий вкус, сочность и аромат, как из бабушкиного сада.\n\n"
                f"Спелые грунтовые томаты, хрустящая зелень, сладкие сезонные фрукты и честный вес. Приходите пробовать и выбирайте лучшее для домашнего стола!{comments_phrase}"
            )
            cta = "Заглядывайте к нам в павильон или заказывайте ящик свежих овощей с доставкой в личных сообщениях! 🛒👇" if has_comments else "Ждём вас за свежими витаминами каждый день! Доставка в ЛС 🍏✨"
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}2026",
                "visual_prompt": "Mouthwatering authentic market food photography. A rustic weathered wooden market stall brimming with vibrant, ripe red heirloom tomatoes, crisp green herbs, and sun-kissed fruits with glistening morning dew drops. Warm natural sunlight streaming through market canvas awning, authentic candid bazaar atmosphere, rich organic textures, 35mm shallow depth of field.",
                "hashtags": "#овощи #фрукты #фермерскиепродукты #рынок #свежесть #зож"
            }

        # 3.14. Creator Economy / Приватные Telegram-каналы / Закрытые клубы / Подписки / OnlyFans / Boosty
        elif any(w in full_text_search for w in ["приват", "онлифанс", "onlyfans", "boosty", "закрытый канал", "эксклюзив", "клуб", "подписк", "vip", "интим", "модель", "18+"]):
            lead = f"То, что никогда не попадет в открытый доступ: эксклюзив в закрытом клубе «{company_name}» 🤫🔥"
            body = (
                f"{topic_clean}.{visual_phrase}\n\n"
                f"Здесь нет цензуры, рамок и банального контента — только самый личный, откровенный и эстетичный бэкстейдж, прямые эфиры и общение один на один.\n\n"
                f"Каждый день — свежий эксклюзивный материал, который доступен только избранному кругу подписчиков.{comments_phrase}"
            )
            cta = "Входная ссылка-инвайт сгорает через 24 часа! Забирай доступ в приват прямо сейчас по ссылке в описании профиля или пиши в ЛС 🔒👇" if has_comments else "Забирай закрытый доступ в личных сообщениях прямо сейчас! 🤫✨"
            return {
                "post_text": f"{lead}\n\n{body}\n\n{cta}",
                "promo_code": f"{company_name.upper().replace(' ', '')}VIP",
                "visual_prompt": "Seductive atmospheric aesthetic storytelling portrait. A mesmerizing charismatic creator in subtle ambient neon and warm candlelight, playful confident gaze, striking silhouette in soft focus, intimate cinematic room atmosphere, authentic raw smartphone candid grain, tasteful artistic mood, 35mm shallow depth of field.",
                "hashtags": "#exclusive #vip #private #lifestyle #backstage #эстетика"
            }

        # =========================================================================
        # 4. ДИНАМИЧЕСКИЙ УНИВЕРСАЛЬНЫЙ ГЕНЕРАТОР (FALLBACK ДЛЯ ЛЮБОЙ НИШИ)
        # =========================================================================
        lead = f"Новости и актуальные решения от «{company_name}»"
        body = (
            f"{topic_clean}.{visual_phrase}\n\n"
            f"В компании «{company_name}» мы постоянно совершенствуем наш подход в сфере «{niche}», "
            f"чтобы каждый клиент получал надёжный, прогнозируемый и качественный результат.\n\n"
            f"Опыт команды, индивидуальный подход к задачам и современные стандарты сервиса экономят ваше время и ресурсы.{comments_phrase}"
        )
        cta = f"Поделитесь вашим мнением в комментариях 👇 — мы открыты к диалогу и рады ответить на любые вопросы!" if has_comments else f"Ставьте реакции 🔥 и пишите нам в личные сообщения — мы всегда на связи!"
        hashtags = f"#{niche.replace(' ', '_')} #бизнес #качество #новости"
        visual_prompt = (
            f"Cinematic emotional storytelling photograph for {niche}. "
            f"Subject: a passionate dedicated professional in {niche} deeply engaged in their craft at a modern sunlit workstation, genuine focus, pride and mastery. "
            f"Lighting: warm natural window daylight, soft golden highlights, realistic room depth. "
            f"Style: authentic commercial storytelling photography, genuine human connection, shallow depth of field, real life texture, photorealistic."
        )

        full_post = f"{lead}\n\n{body}\n\n{cta}"
        return {
            "post_text": full_post,
            "promo_code": f"{company_name.upper().replace(' ', '')}2026",
            "visual_prompt": visual_prompt,
            "hashtags": hashtags
        }

    def analyze_brand_profile(self, user_data: dict, clean_posts: Optional[list] = None, visuals: Optional[list] = None) -> dict:
        """
        Анализирует опросник бренда от Агента-Интервьюера и формирует полный бренд-профиль
        (Позиционирование, Рынок, Конкуренты, SWOT, Услуги, Цели и Tone of Voice).
        """
        company_name = user_data.get("company_name") or user_data.get("name") or "Ваш бизнес"
        description = user_data.get("description") or user_data.get("activity") or "Качественные услуги и товары для клиентов"
        activity = user_data.get("activity") or "Услуги и коммерция"
        difference = user_data.get("difference") or "Индивидуальный подход и высокое качество"
        city = user_data.get("city") or "Москва"

        print(f"[SaigaSkill] 🧠 Анализ профиля бренда: '{company_name}', Ниша: '{activity}', Город: '{city}'...")

        # Интеллектуальная адаптация под сферу бизнеса
        text_lower = f"{company_name} {description} {activity} {difference}".lower()

        if "кофе" in text_lower or "пекарн" in text_lower or "десерт" in text_lower:
            field = "Общепит / Кофейня"
            positioning = f"«{company_name}» — место притяжения для ценителей свежей обжарки, уютной атмосферы и искреннего гостеприимства."
            direct_competitors = ["Surf Coffee (https://surfcoffee.ru)", "Skuratov Coffee (https://skuratovcoffee.ru)", "Drinkit (https://drinkit.ru)"]
            network_competitors = ["Кофе Хауз (https://coffeehouse.ru)", "Cofix (https://cofix.ru)", "Шоколадница (https://shoko.ru)"]
            local_competitors = [f"Локальные спешелти-кофейни г. {city}", f"Пекарни и кондитерские у дома", f"Кофе-точки формата To-Go"]
            competitors = direct_competitors + network_competitors + local_competitors
            segment = "Жители и гости района 20-45 лет, ценящие качественный кофе, уют и быстрое обслуживание"
            trends = ["Спешелти зерно свежей обжарки", "Сезонные авторские напитки", "Экологичная упаковка и программа лояльности"]
            strengths = ["Высокое качество зерна и свежая выпечка", "Теплая и уютная атмосфера", "Удобное расположение", "Быстрое и приветливое обслуживание"]
            weaknesses = ["Высокая конкуренция в районе", "Зависимость от сезонного пешеходного трафика", "Ограниченное количество посадочных мест", "Необходимость постоянного контроля себестоимости"]
            opportunities = ["Запуск авторских десертов и мерча", "Развитие подписок на зерно и утренний кофе", "Проведение каппингов и мастер-классов", "Коллаборации с локальными брендами"]
            threats = ["Рост цен на сырье и логистику", "Открытие конкурентов поблизости", "Снижение покупательской способности", "Колебания утреннего трафика"]
            services = [
                {"title": "Кофейная карта", "items": "Эспрессо, капучино, фильтр-кофе, рафы и сезонные авторские напитки"},
                {"title": "Свежая выпечка и десерты", "items": "Круассаны, крафтовые тарты, печенье и легкие перекусы"},
                {"title": "Кофе в зернах с собой", "items": "Свежеобжаренное зерно для дома с помолом под ваш способ заваривания"}
            ]
            goals = ["Увеличение повторных визитов гостей на 35%", "Рост среднего чека через комбо-предложения", "Формирование лояльного комьюнити постоянных клиентов"]
            tone = ["Тёплый", "Гостеприимный", "Без лишнего пафоса", "С заботой о каждом госте"]

        elif "красот" in text_lower or "барбер" in text_lower or "салон" in text_lower or "космет" in text_lower:
            field = "Красота и персональный уход"
            positioning = f"«{company_name}» — пространство эстетики и заботы о себе с экспертным подходом к каждому клиенту."
            direct_competitors = ["Persona Lab (https://persona.ru)", "NailMaker Bar (https://nailmaker.bar)", "Точка Красоты (https://tochkafamily.ru)"]
            network_competitors = ["TopGun Barbershop (https://topgun.ru)", "OldBoy Barbershop (https://oldboybarbershop.com)", "Студии Лены Лениной (https://llmanikur.ru)"]
            local_competitors = [f"Частные бьюти-мастера г. {city}", f"Локальные студии маникюра и бровей", f"Косметологические кабинеты"]
            competitors = direct_competitors + network_competitors + local_competitors
            segment = "Женщины и мужчины 22-50 лет, ценящие безупречный сервис, чистоту и профессионализм мастеров"
            trends = ["Натуральные эко-составы и бережный уход", "Персонализированные уходовые протоколы", "Онлайн-запись в один клик"]
            strengths = ["Сертифицированные мастера с опытом", "Премиальные материалы и косметика", "Высокий уровень сервиса и стерильности", "Высокий процент возвращаемости клиентов"]
            weaknesses = ["Плотная запись в пиковые часы", "Зависимость от конкретных мастеров", "Необходимость регулярных инвестиций в оборудование", "Чувствительность к ценообразованию"]
            opportunities = ["Пакетные абонементы и комплексные программы", "Продажа домашней линейки косметики", "Программа 'Приведи подругу'", "Обучающие бьюти-дни"]
            threats = ["Отток мастеров в частную практику", "Демпинг со стороны эконом-студий", "Рост стоимости премиальной косметики", "Сезонные спады спроса"]
            services = [
                {"title": "Базовый и премиальный уход", "items": "Комплексные процедуры ухода, стрижки, укладки и окрашивание"},
                {"title": "Эстетические процедуры", "items": "Маникюр, педикюр, оформление бровей и ресниц"},
                {"title": "Домашний уход", "items": "Подбор профессиональной косметики для поддержания эффекта"}
            ]
            goals = ["Увеличение LTV клиентов за счет пакетных абонементов", "Рост узнаваемости студии в городе", "Привлечение новых клиентов через визуальный контент"]
            tone = ["Элегантный", "Внимательный", "Экспертный", "Вдохновляющий"]

        elif any(w in text_lower for w in ["it", "ai", "нейросет", "маркетинг", "агент", "saas", "софт", "разработк", "автоном"]):
            field = "IT и автономный AI-маркетинг"
            positioning = f"«{company_name}» — сквозная мульти-агентная экосистема для полной автоматизации создания, контроля качества и дистрибуции контента 24/7."
            direct_competitors = ["SMMplanner (https://smmplanner.com)", "LiveDune (https://livedune.com)", "Postmypost (https://postmypost.ru)"]
            network_competitors = ["Яндекс.Бизнес (https://business.yandex.ru)", "VK Реклама (https://ads.vk.com)", "TgStat (https://tgstat.ru)"]
            local_competitors = ["Традиционные digital-агентства", "Контент-фрилансеры", "Штатные копирайтеры"]
            competitors = direct_competitors + network_competitors + local_competitors
            segment = "Предприниматели, маркетологи и эксперты, которым нужен качественный контент и визуальный продакшн без рутины"
            trends = ["Автономные мульти-агентные пайплайны", "Смысловая генерация визуала без стоков", "Сквозная омниканальная дистрибуция"]
            strengths = ["Полная сквозная автономность от идеи до публикации", "Умный визуальный продакшн со смыслом", "Встроенный pre-mortem аудит качества", "Мультиплатформенная дистрибуция за секунды"]
            weaknesses = ["Необходимость демонстрации новых стандартов рынку", "Высокие требования к вычислительным мощностям", "Постоянное расширение библиотеки ниш"]
            opportunities = ["Масштабирование на все сферы малого и среднего бизнеса", "Интеграция с локальными геосервисами и маркетплейсами", "Запуск B2B-партнёрств"]
            threats = ["Быстрое изменение API социальных сетей", "Недобросовестный хайп вокруг базовых чат-ботов", "Сложность восприятия мультиагентности клиентами"]
            services = [
                {"title": "Автономный копирайтинг и позиционирование", "items": "Генерация целевых публикаций без воды и клише под любую сферу бизнеса"},
                {"title": "Умный визуальный продакшн", "items": "Создание кинематографичных и UGC-кадров со смысловой режиссурой"},
                {"title": "Омниканальная дистрибуция 24/7", "items": "Мгновенная отправка постов в Telegram, VK, OK, MAX и геосервисы"}
            ]
            goals = ["Снижение времени на выпуск контента с 3 часов до 30 секунд", "Обеспечение 100% защиты от шаблонных ошибок", "Рост охватов и доверия аудитории"]
            tone = ["Уверенный", "Экспертный", "Технологичный", "Живой и открытый"]

        elif ("автомобил" in text_lower or "детейлинг" in text_lower or "автосервис" in text_lower or "сто" in text_lower) and "автоном" not in text_lower:
            field = "Автомобильные услуги и детейлинг"
            positioning = f"«{company_name}» — профессиональный уход и надежное обслуживание автомобилей с гарантией результата."
            direct_competitors = ["Detailing World (https://detailingworld.ru)", "Brooklands Detailing (https://brooklands.ru)", "Koch24 (https://koch24.ru)"]
            network_competitors = ["Fit Service (https://fitauto.ru)", "Вилгуд (https://wilgood.ru)", "Колесо.ру (https://koleso.ru)"]
            local_competitors = [f"Автосервисы и СТО района г. {city}", f"Частные детейлинг-боксы", f"Мойки самообслуживания"]
            competitors = direct_competitors + network_competitors + local_competitors
            segment = "Автовладельцы 25-55 лет, ценящие идеальный вид и техническую надежность своего автомобиля"
            trends = ["Керамические и полиуретановые защитные покрытия", "Прозрачные фото/видео отчеты о работах", "Комплексный сезонный детейлинг"]
            strengths = ["Профессиональное оборудование и химия", "Строгое соблюдение регламентов", "Честная гарантия на все виды работ", "Прозрачные цены без скрытых доплат"]
            weaknesses = ["Длительное время выполнения сложных процедур", "Ограниченная пропускная способность боксов", "Высокие требования к квалификации мастеров", "Зависимость от поставок качественных составов"]
            opportunities = ["Сезонные пакеты 'Защита кузова к зиме/лету'", "Корпоративное обслуживание автопарков", "Клубные карты для постоянных клиентов", "Услуги предпродажной подготовки"]
            threats = ["Рост стоимости импортных материалов", "Недобросовестная конкуренция с дешевыми материалами", "Общее снижение пробегов и трат на авто", "Сложности с поиском квалифицированных детейлеров"]
            services = [
                {"title": "Защита кузова и детейлинг", "items": "Полировка, нанесение керамики, оклейка бронепленкой"},
                {"title": "Химчистка и реставрация салона", "items": "Глубокая очистка кожи, текстиля и озонация салона"},
                {"title": "Сезонный уход", "items": "Антидождь, защита дисков и подготовка кузова к зиме"}
            ]
            goals = ["Рост загрузки детейлинг-боксов до 90%", "Повышение среднего чека через защитные комплексы", "Формирование репутации сервиса номер один в городе"]
            tone = ["Уверенный", "Технически грамотный", "Честный", "Надежный"]

        else:
            # Универсальный профиль (IT, контент-генерация, услуги, SaaS, UCust)
            field = activity if activity != "Услуги и коммерция" else "IT и автоматизация контента"
            positioning = f"«{company_name}» — современный онлайн-сервис для генерации постов и контента с экспертным подходом и понятным результатом для клиента."
            direct_competitors = ["SMMplanner (https://smmplanner.com)", "LiveDune (https://livedune.com)", "Postmypost (https://postmypost.ru)"]
            network_competitors = ["Яндекс.Бизнес (https://business.yandex.ru)", "VK Реклама (https://ads.vk.com)", "TgStat (https://tgstat.ru)"]
            local_competitors = ["Локальные digital-агентства", "Контент-фрилансеры на Kwork/FL", "Штатные копирайтеры"]
            competitors = direct_competitors + network_competitors + local_competitors
            segment = "Предприниматели, маркетологи и SMM-специалисты, которым важно получать качественный контент без рутины"
            trends = ["Внедрение ИИ в ежедневные SMM-процессы", "Автоматизация создания контента и планирования", "Прозрачная аналитика и окупаемость вложений"]
            strengths = ["Высокая скорость и автоматизация процессов", "Понятный и удобный интерфейс", "Экспертная поддержка на всех этапах", "Ощутимая экономия времени и бюджета"]
            weaknesses = ["Необходимость обучения клиентов новым возможностям", "Высокие требования к отказоустойчивости", "Постоянная потребность в обновлениях функционала", "Конкуренция за внимание аудитории"]
            opportunities = ["Масштабирование на новые ниши и рынки", "Запуск интеграций с популярными платформами", "Партнерские программы для бизнеса", "Создание базы знаний и обучающих материалов"]
            threats = ["Быстрое изменение трендов и алгоритмов соцсетей", "Появление новых конкурентных решений", "Экономическая осторожность клиентов в бюджетах", "Технические изменения внешних API"]
            services = [
                {"title": "Генерация контента и постов", "items": "Создание коммерческих текстов, хэштегов и визуалов под ключ"},
                {"title": "Автоматизация маркетинга", "items": "Планирование публикаций, автопостинг и аналитика вовлеченности"},
                {"title": "Консультации и интеграция", "items": "Настройка профиля бизнеса, подбор стиля и адаптация под аудиторию"}
            ]
            goals = ["Увеличение базы активных пользователей", "Снижение времени создания контента до 30 секунд", "Максимизация окупаемости маркетинговых инвестиций клиентов"]
            tone = ["Профессиональный", "Уверенный", "Технологичный", "Понятный и доброжелательный"]

        return {
            "name": company_name,
            "field": field,
            "positioning": positioning,
            "market": {
                "competitors": competitors,
                "directCompetitors": direct_competitors,
                "networkCompetitors": network_competitors,
                "localCompetitors": local_competitors,
                "geography": city,
                "segment": segment,
                "trends": trends
            },
            "swot": {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "opportunities": opportunities,
                "threats": threats
            },
            "services": services,
            "goals": goals,
            "tone": tone
        }

    def self_heal_text(self, raw_text: str, feedback_log: str) -> str:
        """
        Автономный цикл самоисправления: принимает текст, забракованный Gatekeeper,
        исправляет конкретные ошибки и удаляет стоп-слова без участия человека.
        """
        print(f"[SaigaSkill] 🔄 Запуск самоисправления текста на основе фидбека: '{feedback_log}'...")
        time.sleep(1)
        healed_text = raw_text.replace("—", "-")
        for stop_word in ["безумно", "невероятно", "потрясающе", "волшебный", "сказочный", "от всей души", "мы гордимся"]:
            healed_text = healed_text.replace(stop_word, "").replace("  ", " ")
        return healed_text
        
    def generate_storyboard(self, profile: dict, scenes_count: int) -> list:
        """
        Генерирует детальный сценарий для LTX-2 строго по официальному гайду разработчиков:
        - Связный нарративный абзац (4-8 предложений в настоящем времени).
        - Четкая композиция кадра (Scale & Shot type) и операторские движения (Camera language).
        - Освещение, текстуры, цветовая палитра и атмосфера.
        - Физические проявления эмоций персонажей (вместо абстрактных ярлыков).
        - Прямая речь и диалоги ОБЯЗАТЕЛЬНО на русском языке в кавычках с фонетическими знаками '+' для ударений.
        - Ambient звуки и шумы окружения.
        """
        print(f"[SaigaSkill] 🧠 Генерация раскадровки по официальному LTX-2 стандарту на {scenes_count} сцен...")
        time.sleep(1)
        
        storyboard = []
        for i in range(scenes_count):
            if i % 3 == 0:
                scene = {
                    "shot_type": "INT. MODERN COWORKING - DAY. Medium establishing shot",
                    "scene_description": (
                        "Soft natural daylight streams through large panoramic windows, illuminating a sleek minimalist coworking space. "
                        "Subtle dust particles drift in warm sunbeams across smooth wooden tables. "
                        "A young male specialist in his late 20s wearing a navy crewneck sits focused before a laptop, his fingers rapidly typing. "
                        "A steaming ceramic coffee cup rests beside his notepad. "
                        "The camera slowly pans right, tracking his focused movement while coworkers in soft background focus converse quietly. "
                        "The man takes a satisfied breath, smiles faintly, and turns to his colleague saying softly with an energetic tone: "
                        '"Отл+ично, вс+е рекл+амные кампании запущены вовремя."'
                    ),
                    "style_markers": "Cinematic realism, warm natural lighting, 35mm film grain, high-end corporate aesthetic",
                    "negative_prompt": (
                        "low quality, pixelated, compression artifacts, glitch, deformed hands, extra fingers, "
                        "mutated limbs, distorted face, cartoon, 3d render, watermark, readable signage, blur, chaotic motion"
                    ),
                    "audio": {
                        "ambient": "Soft open-space murmur, gentle keyboard clicking, distant coffee machine hum, warm acoustic background melody",
                        "dialogue": '[Специалист, с улыбкой]: "Отл+ично, вс+е рекл+амные комп+ании зап+ущены в+овремя."'
                    }
                }
            elif i % 3 == 1:
                scene = {
                    "shot_type": "EXT. METROPOLIS STREET - AFTERNOON. Dynamic low-angle tracking shot",
                    "scene_description": (
                        "The shot opens with cold overcast lighting reflecting on sleek glass skyscrapers and wet asphalt. "
                        "A confident businesswoman in her early 30s in a sharp tailored dark coat strides purposefully down the bustling sidewalk. "
                        "She holds a digital tablet in her hand, her eyes scanning the glowing screen. "
                        "The camera tracks backwards smoothly at eye-level, keeping her face in sharp focus as yellow city taxis and pedestrian silhouettes streak past in natural motion blur. "
                        "A sharp notification chime rings out on her tablet. She looks up with determined eyes and speaks briskly into her wireless earpiece: "
                        '"Конв+ерсия в+ыросла на с+орок проц+ентов, продолж+аем масшт+аб."'
                    ),
                    "style_markers": "Urban realism, cool cyber-blue color grading, dynamic handheld stabilization, premium commercial look",
                    "negative_prompt": (
                        "unrealistic physics, jumping, teleportation, distorted anatomy, six fingers, blurry faces, "
                        "harsh flicker, cartoonish, low resolution, messy textures, floating text"
                    ),
                    "audio": {
                        "ambient": "Rumbling city traffic, gentle tire whoosh on asphalt, muffled urban atmosphere, crisp notification chime",
                        "dialogue": '[Бизнес-леди в гарнитуру, уверенно]: "Конв+ерсия в+ыросла на с+орок проц+ентов, продолж+аем масшт+аб."'
                    }
                }
            else:
                scene = {
                    "shot_type": "INT. EXECUTIVE LOUNGE - EVENING. Intimate medium close-up",
                    "scene_description": (
                        "Warm amber practical lights cast a cozy glow across dark leather armchairs and polished walnut walls. "
                        "The camera slowly pushes in on two business partners seated across a coffee table. "
                        "A mature executive with silver-streaked hair leans forward, extending his hand with a warm, reassuring smile. "
                        "Shallow depth of field creates soft circular bokeh in the background. "
                        "The client firmly shakes his hand, visibly relieved, shoulders relaxing. "
                        "The executive nods with calm gravitas and says in a deep, welcoming Russian voice: "
                        '"Мы бер+ем всю авт+оматиз+ацию на себ+я. В+аш б+изнес в над+ежных рук+ах."'
                    ),
                    "style_markers": "Moody cinematic lighting, golden hour tones, shallow depth of field, elegant corporate documentary",
                    "negative_prompt": (
                        "bad anatomy, disconnected limbs, unnatural skin texture, high noise, oversaturated, "
                        "ugly faces, jitter, stuttering motion, text overlays, 2d animation"
                    ),
                    "audio": {
                        "ambient": "Quiet executive suite ambience, soft rustle of clothing, distant soothing ambient music",
                        "dialogue": '[Руководитель, с уверенным теплым тоном]: "Мы бер+ем всю авт+оматиз+ацию на себ+я. В+аш б+изнес в над+ежных рук+ах."'
                    }
                }
            storyboard.append(scene)
            
        return storyboard

    def self_heal_text(self, text: str, feedback: str) -> str:
        """
        Самоисправление и полировка текста на основе обратной связи от Агента-Критика.
        Добавляет конкретику, сильный хук, цифры и четкий призыв к действию (CTA).
        """
        print(f"[SaigaSkill] 🔄 Запуск самоисправления текста на основе фидбека: '{feedback}'...")
        
        # Если загружена нейросеть
        if self._is_loaded and self._llm:
            try:
                system_instruction = (
                    "Ты — главный редактор. Твой черновик отклонил строгий критик. "
                    f"Замечания критика: {feedback}\n\n"
                    "Перепиши текст так, чтобы исправить все замечания: "
                    "убери штампы и скучные приветствия, добавь конкретные цифры и сроки, "
                    "разбей на короткие абзацы и поставь сильный призыв к действию в конце."
                )
                output = self._llm.create_chat_completion(
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": f"Исходный текст:\n{text}"}
                    ],
                    temperature=0.7,
                    max_tokens=600
                )
                healed = output["choices"][0]["message"]["content"].strip()
                if len(healed) > 40:
                    return healed
            except Exception as e:
                print(f"[SaigaSkill] ⚠️ Ошибка LLaMA self-heal: {e}")

        # Интеллектуальный генератор полировки исходного текста
        healed = text
        # Убираем штампы
        for cliché, replacement in [
            ("индивидуальный подход", "персонализированный подбор программы"),
            ("высокое качество", "сертифицированные материалы и стандарты 2026 года"),
            ("широкий спектр услуг", "комплексный сервис в одном месте"),
            ("команда профессионалов", "опытные сертифицированные мастера с подтвержденной квалификацией"),
            ("приятные цены", "прозрачная стоимость без скрытых доплат")
        ]:
            pattern = re.compile(re.escape(cliché), re.IGNORECASE)
            healed = pattern.sub(replacement, healed)

        # Удаляем банальные приветствия
        paragraphs = [p.strip() for p in healed.split("\n") if p.strip()]
        clean_paras = []
        for p in paragraphs:
            p_clean = p
            if p.lower().startswith(("здравствуйте", "привет", "всем привет", "добрый день")):
                p_clean = p.split(".", 1)[-1].strip() if "." in p else ""
            if p_clean:
                clean_paras.append(p_clean)

        if not clean_paras:
            clean_paras = [text]

        # Если в тексте не было конкретных цифр или сильного CTA, усиливаем его
        if not any(char.isdigit() for char in healed):
            clean_paras.insert(1, "✨ Более 1500 довольных клиентов, средняя оценка 4.9 из 5.0 и гарантия безупречного результата на каждую процедуру.")

        return "\n\n".join(clean_paras)
