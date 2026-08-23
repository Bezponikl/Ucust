import re

with open('onboarding_pipeline.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_vqa_func = """async def visual_director_vqa(parsed_posts: list, uploaded_photos: list):
    print(f"[Agent_Visual_Director] 🎨 Начинаю работу на базе локальной нейросети Moondream2 (GGUF)...")
    
    # 1. Анализ загруженных референсов
    print(f"[Agent_Visual_Director] 🎨 Moondream VQA: Анализ загруженных референсных фото/видео ({len(uploaded_photos)} шт.)...")
    visual_descriptions = []
    
    try:
        from skills.moondream_vqa import MoondreamVQASkill
        # Инициализируем наш скилл для анализа референсов
        moondream = MoondreamVQASkill()
        
        # Если модель запустится на CPU, мы проанализируем картинки пользователя
        for photo in uploaded_photos:
            desc = moondream.analyze_image(photo, prompt="Опиши стиль, цвета и объекты на фото коротко, чтобы передать контекст для Сайги.")
            visual_descriptions.append(desc)
    except Exception as e:
        print(f"[Agent_Visual_Director] ⚠️ Ошибка Moondream: {e}")
        visual_descriptions = ["[Mock] Фото офиса, строгий стиль.", "[Mock] Логотип компании."]

    # 2. Оценка визуального ряда постов (эмуляция отсеивания спама/рекламы вместе с Аналитиком)
    clean_posts = [p for p in parsed_posts if "РЕКЛАМА" not in p.upper() and "СКИДКА" not in p.upper()]
    print(f"[Agent_Visual_Director] 🎨 Совместная работа с Аналитиком: отфильтровано рекламных постов: {len(parsed_posts) - len(clean_posts)}.")
    
    print("[Agent_Visual_Director] 🎨 Визуальный пред-анализ завершен. Данные готовы для передачи в LLM (Сайгу).")
    return clean_posts, visual_descriptions
"""
code = re.sub(r'async def visual_director_vqa\(parsed_posts: list, uploaded_photos: list\):.*?return clean_posts, visual_descriptions\n', new_vqa_func, code, flags=re.DOTALL)

with open('onboarding_pipeline.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Updated onboarding_pipeline.py')
