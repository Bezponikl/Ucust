import asyncio
import time
import json
from dotenv import load_dotenv
load_dotenv(override=True)

from onboarding_pipeline import (
    interviewer_chat,
    analyst_parser,
    visual_director_vqa,
    DummySaiga
)

async def measure_pipeline():
    print("=" * 80)
    print("🚀 СТАРТ ТЕСТОВОГО ПРОГОНА С ЗАМЕРАМИ ВРЕМЕНИ (t.me/dvachannel)")
    print("=" * 80)
    
    user_data = {
        "company_name": "UCust SMM",
        "raw_social_input": "Мой канал t.me/dvachannel",
        "uploaded_photos": ["photo1_office.jpg", "photo2_team.jpg"]
    }
    
    t_start = time.time()
    
    # 1. Интервьюер
    t_interviewer_start = time.time()
    await interviewer_chat(user_data)
    t_interviewer = time.time() - t_interviewer_start
    
    print("\n" + "-"*40)
    print(f"📦 [PAYLOAD] От Интервьюера к Аналитику:")
    print(json.dumps(user_data["social_links"], indent=2, ensure_ascii=False))
    print("-" * 40)
    
    # 2. Аналитик (Парсинг + Сжатие)
    t_analyst_start = time.time()
    parsed_posts, downloaded_media = await analyst_parser(user_data)
    t_analyst = time.time() - t_analyst_start
    
    print("\n" + "-"*40)
    print(f"📦 [PAYLOAD] От Аналитика к Визуальному Директору (первые 300 символов):")
    if parsed_posts:
        sample_post = parsed_posts[0][:300] + "..." if len(parsed_posts[0]) > 300 else parsed_posts[0]
        print(f"Постов: {len(parsed_posts)}\nСкачано медиа: {len(downloaded_media)} файлов\nПример: {sample_post}")
    else:
        print("Постов нет.")
    print("-" * 40)
    
    # 3. Визуальный директор (Moondream VQA)
    t_visual_start = time.time()
    clean_posts, visual_descriptions = await visual_director_vqa(parsed_posts, user_data["uploaded_photos"] + downloaded_media)
    t_visual = time.time() - t_visual_start
    
    print("\n" + "-"*40)
    print(f"📦 [PAYLOAD] От Визуального Директора к Сайге:")
    print(f"Описания стилей: {visual_descriptions}")
    print(f"Очищенных постов: {len(clean_posts)}")
    print("-" * 40)
    
    # 4. Сайга (Синтез)
    t_saiga_start = time.time()
    profile = DummySaiga.analyze_voice_tone(user_data, clean_posts, visual_descriptions)
    t_saiga = time.time() - t_saiga_start
    
    print("\n" + "-"*40)
    print(f"📦 [PAYLOAD] Финальный профиль от Сайги:")
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    print("-" * 40)
    
    t_total = time.time() - t_start
    
    print("\n" + "="*80)
    print("⏱️ ОТЧЕТ О ВРЕМЕНИ ВЫПОЛНЕНИЯ (Хронометраж)")
    print("=" * 80)
    print(f"1. Работа Интервьюера (regex + чистка): {t_interviewer:.2f} сек.")
    print(f"2. Работа Аналитика (Парсинг Телеграм + Repowise дистилляция): {t_analyst:.2f} сек.")
    print(f"3. Работа Визуального Директора (Moondream VQA на 2 фото): {t_visual:.2f} сек.")
    print(f"4. Работа Сайги (Синтез тональности): {t_saiga:.2f} сек.")
    print(f"-> Суммарное время коммуникации агентов: {t_interviewer + t_visual + t_saiga:.2f} сек.")
    print("-" * 40)
    print(f"Общее время (Парсинг + Общение + Синтез): {t_total:.2f} сек.")
    print("=" * 80)

if __name__ == '__main__':
    asyncio.run(measure_pipeline())
