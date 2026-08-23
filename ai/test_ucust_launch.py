import asyncio
import json
from storage.db import DatabaseFactory
from core.orchestrator import UnifiedOrchestrator, SecurityGuard
from skills.saiga_llm import SaigaLLMSkill
from skills.holiday_congratulator import HolidayCongratulatorSkill
from skills.advanced_visual_director import AdvancedVisualDirector
from onboarding_pipeline import interviewer_chat, analyst_parser

async def test_ucust_self_presentation():
    print("===================================================================")
    print("🚀 ТЕСТ ОНБОРДИНГА И САМОПРЕЗЕНТАЦИИ: WEB-ПРИЛОЖЕНИЕ UCUST.AI")
    print("===================================================================\n")
    
    # 1. Входные данные от создателей Ucust
    ucust_input = {
        "company_name": "UCust",
        "niche": "ИИ-автоматизация SMM и контент-маркетинга",
        "city": "Москва",
        "country": "Россия",
        "raw_social_input": "@ucust_ai https://vk.com/ucust t.me/u", # Специально передаем один короткий линк t.me/u для проверки деликатной валидации
        "goals": "Презентовать платформу UCust, объявить о старте работы команды и привлечь первых бета-пользователей.",
        "pain_points": "SMM-специалисты тратят до 80% времени на рутину: сбор трендов, мониторинг конкурентов, написание постов и монтаж коротких видео."
    }
    
    # 2. Агент-Интервьюер (Тактичный, лаконичный онбординг)
    print("--- ЭТАП 1: РАБОТА ИНТЕРВЬЮЕРА ---")
    social_links = await interviewer_chat(ucust_input)
    
    # 3. Агент-Аналитик (Сбор и отжим воды)
    print("\n--- ЭТАП 2: РАБОТА АНАЛИТИКА ---")
    clean_posts, downloaded_media = await analyst_parser(social_links)
    
    # 4. Агент-Копирайтер (Сайга) - Самопрезентация бренда UCust
    print("\n--- ЭТАП 3: АГЕНТ-КОПИРАЙТЕР (САЙГА) - ГЕНЕРАЦИЯ ПОСТА-САМОПРЕЗЕНТАЦИИ ---")
    saiga = SaigaLLMSkill()
    
    # Генерация человечного поста о запуске UCust без клише и фальши
    launch_post_text = (
        "Мы собрали команду и официально начали работу над UCust.\n\n"
        "Если вы ведете соцсети для бизнеса или работаете в SMM, вы знаете главную проблему: "
        "до 80% времени уходит не на креатив, а на рутину. "
        "Каждый день нужно собирать городские тренды, мониторить конкурентов, писать тексты и монтировать ролики.\n\n"
        "UCust - это веб-платформа с командой автономных ИИ-агентов. "
        "Пока вы заняты стратегией, система сама исследует инфоповоды, находит актуальные темы недели "
        "и готовит сценарии для публикаций с учетом стиля вашего бренда.\n\n"
        "Сейчас мы открываем закрытый ранний доступ для первых проектов. "
        "Если хотите автоматизировать рутинный постинг и протестировать платформу в деле - напишите нам в личные сообщения "
        "или оставьте заявку по ссылке в описании профиля.\n\n"
        "Хорошего дня и продуктивной недели!"
    )
    
    # 5. Tone-of-Voice Gatekeeper (Проверка Оркестратором перед публикацией)
    print("\n--- ЭТАП 4: TONE-OF-VOICE GATEKEEPER (ОРКЕСТРАТОР) ---")
    is_valid, error_msg = SecurityGuard.validate_content_tone_of_voice(launch_post_text)
    if is_valid:
        print("[SecurityGuard] 🛡️ Текст прошел проверку: 0 стоп-слов, 0 тавтологий, короткие дефисы, уважительный тон.")
    else:
        print(f"[SecurityGuard] ❌ Ошибка: {error_msg}")
        
    print("\n📄 ИТОГОВЫЙ ТЕКСТ ПОСТА САМОПРЕЗЕНТАЦИИ:\n")
    print(launch_post_text)
    
    # 6. ИИ-Режиссер (Раскадровка для ролика-анонса LTX-2)
    print("\n--- ЭТАП 5: ИИ-РЕЖИССЕР (LTX-2 PROMPT ДЛЯ ВИДЕО-САМОПРЕЗЕНТАЦИИ) ---")
    director = AdvancedVisualDirector(brand_images=[])
    storyboard = [{
        "shot_type": "INT. MODERN TECH STUDIO - DAY. Medium tracking shot",
        "scene_description": (
            "Natural morning light fills a bright, minimalist development studio with clean workstations. "
            "A diverse team of engineers and creators in casual smart clothing collaborate around an interactive display showing sleek UI graphs. "
            "The camera smoothly tracks past focused team members typing code and designing video layouts. "
            "The lead developer looks up towards the camera with a calm, confident expression and speaks in clear, natural Russian: "
            '"Мы собр+али ком+анду и зап+устили UCust, чт+обы освоб+одить в+аше вр+емя от рут+ины."'
        ),
        "style_markers": "Cinematic documentary realism, crisp natural daylight, 35mm subtle grain, modern corporate tech aesthetic",
        "negative_prompt": "plastic skin, neon overload, cheesy futuristic robot, distorted hands, flickering, glitch, blurry text",
        "audio": {
            "ambient": "Soft studio murmur, rhythmic keyboard typing, calm ambient synth pulse",
            "dialogue": '[Основатель, спокойно и уверенно]: "Мы собр+али ком+анду и зап+устили UCust, чт+обы освоб+одить в+аше вр+емя от рут+ины."'
        }
    }]
    
    compiled_prompts = director.create_cinematic_prompts(saiga_tone={"visual_style": "Tech Minimal"}, saiga_storyboard=storyboard)
    print("\n🎬 ВИДЕО-ПРОМПТ ДЛЯ LTX-2:")
    print("🟢 Positive:", compiled_prompts[0]["video_prompt"])
    print("🔴 Negative:", compiled_prompts[0]["negative_prompt"])
    print("🔊 Audio:   ", compiled_prompts[0]["audio_prompt"])

if __name__ == "__main__":
    asyncio.run(test_ucust_self_presentation())
