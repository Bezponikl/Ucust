import json
import time

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

    def analyze_brand_profile(self, user_data: dict, clean_posts: list, visuals: list) -> dict:
        """
        Анализирует данные и возвращает профиль.
        """
        print(f"[SaigaSkill] ⚙️ Настройки генерации: Temp={self.temperature}, TopP={self.top_p}, RepPenalty={self.repetition_penalty}")
        print(f"[SaigaSkill] 🧠 Системный промпт загружен: {len(self.system_prompt)} символов.")
        
        # Формируем контекст для LLM
        prompt = f"""
        Боли: {user_data.get('pain_points')}
        Цели: {user_data.get('goals')}
        
        Анализ текстов (постов):
        {json.dumps(clean_posts[:3], ensure_ascii=False)}
        
        Визуальный стиль:
        {json.dumps(visuals, ensure_ascii=False)}
        
        Ответь только валидным JSON.
        """
        
        print("[SaigaSkill] 🧠 Идет инференс (имитация локальной генерации)...")
        time.sleep(2) # Имитация работы CPU
        
        # В будущем здесь будет вызов Llama(self.model_path)(prompt, temperature=self.temperature, ...)
        
        # Возвращаем "сгенерированный" JSON
        return {
            "tone_of_voice": "Профессиональный, технологичный, но с долей эмпатии и заботы",
            "visual_style": "Минимализм с синими акцентами (Cyber Blue)",
            "key_topics": ["Автоматизация рутины", "ИИ в SMM", "Экономия времени"],
            "taboos": ["Агрессивные продажи", "Сложные технические термины без объяснения"]
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
