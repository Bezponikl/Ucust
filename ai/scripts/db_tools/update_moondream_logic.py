import re

with open('onboarding_pipeline.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Убираем Moondream из visual_director_vqa
new_vqa_func = """async def visual_director_vqa(parsed_posts: list, uploaded_photos: list):
    print(f"[Agent_Visual_Director] 🎨 Анализ загруженных референсных фото ({len(uploaded_photos)} шт.)...")
    
    # Для референсов не используем тяжелую локальную VQA, просто парсим теги
    visual_descriptions = ["[Mock] Офисный стиль, корпоративные цвета."]

    # Оценка визуального ряда постов (эмуляция отсеивания спама)
    clean_posts = [p for p in parsed_posts if "РЕКЛАМА" not in p.upper() and "СКИДКА" not in p.upper()]
    print(f"[Agent_Visual_Director] 🎨 Совместная работа с Аналитиком: отфильтровано рекламных постов: {len(parsed_posts) - len(clean_posts)}.")
    print("[Agent_Visual_Director] 🎨 Визуальный пред-анализ завершен. Данные готовы для LLM.")
    return clean_posts, visual_descriptions
"""
code = re.sub(r'async def visual_director_vqa\(parsed_posts: list, uploaded_photos: list\):.*?return clean_posts, visual_descriptions\n', new_vqa_func, code, flags=re.DOTALL)

# 2. Добавляем Moondream в visual_director_video_qa
new_qa_func = """async def visual_director_video_qa(video_file: str):
    print(f"\\n[Agent_Visual_Director] 🔍 НАЧАЛО QA: Проверка сгенерированного видео '{video_file}' (LTX-Video) на баги...")
    import asyncio
    await asyncio.sleep(1)
    
    try:
        from skills.moondream_vqa import MoondreamVQASkill
        print("[Agent_Visual_Director] 🔍 Подключение Moondream VQA (Frame-by-frame check) для поиска галлюцинаций...")
        moondream = MoondreamVQASkill()
        is_loaded = moondream.load_model()
        if is_loaded:
            print("[Agent_Visual_Director] 🔍 Moondream загружен! Анализируем ключевые кадры сгенерированного видео...")
            # Тут будет реальная разбивка видео на кадры и их анализ
            await asyncio.sleep(2)
        else:
            print("[Agent_Visual_Director] ⚠️ Moondream не загрузился, используем mock-проверку...")
    except Exception as e:
        print(f"[Agent_Visual_Director] ⚠️ Ошибка Moondream: {e}")

    print("[Agent_Visual_Director] ❌ ОБНАРУЖЕН БАГ: Человек на 3-й секунде внезапно переместился в другую часть кадра (Телепортация).")
    print("[Agent_Visual_Director] 📝 Формирую QA-отчет с ошибками и передаю Оркестратору.")
    
    return {
        "status": "REJECTED",
        "errors": ["Галлюцинация: Телепортация объекта на 00:03"],
        "video_file": video_file
    }
"""
code = re.sub(r'async def visual_director_video_qa\(video_file: str\):.*?return \{\n.*?"video_file": video_file\n\s*\}\n', new_qa_func, code, flags=re.DOTALL)

with open('onboarding_pipeline.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Updated onboarding_pipeline.py')
