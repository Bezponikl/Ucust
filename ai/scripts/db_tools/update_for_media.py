import re
import os

# 1. Update telethon_collector.py
with open('collectors/telethon_collector.py', 'r', encoding='utf-8') as f:
    tc_code = f.read()

new_media_logic = """
            media_type = None
            media_path = None
            if message.media:
                if isinstance(message.media, MessageMediaPhoto):
                    media_type = "photo"
                    try:
                        if not os.path.exists("temp_media"):
                            os.makedirs("temp_media")
                        filepath = await client.download_media(message, file="temp_media/")
                        media_path = filepath
                    except Exception as e:
                        print(f"Failed to download photo: {e}")
                elif isinstance(message.media, MessageMediaDocument):
                    media_type = "document"

            messages_data.append({
                "id": message.id,
                "text": message.text or "",
                "date": message.date.isoformat() if message.date else None,
                "views": getattr(message, "views", 0) or 0,
                "forwards": getattr(message, "forwards", 0) or 0,
                "media_type": media_type,
                "media_path": media_path,
                "is_forwarded": message.fwd_from is not None,
            })
"""

tc_code = re.sub(
    r'\s*media_type = None\s*if message\.media:.*?"is_forwarded": message\.fwd_from is not None,\s*\}\)',
    new_media_logic,
    tc_code,
    flags=re.DOTALL
)

with open('collectors/telethon_collector.py', 'w', encoding='utf-8') as f:
    f.write(tc_code)


# 2. Update onboarding_pipeline.py
with open('onboarding_pipeline.py', 'r', encoding='utf-8') as f:
    op_code = f.read()

# Update analyst_parser to return downloaded_media
new_analyst = """
    print(f"[Agent_Analyst] 🧠 Парсинг каналов: Telegram={tg_channels}, VK={vk_groups}")
    collector = TelethonCollector()
    parsed_posts = []
    downloaded_media = []

    # --- Telegram ---
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

    # --- VK (моки) ---
    for group in vk_groups:
        print(f"[Agent_Analyst] 📥 Парсинг VK-группы {group} (mock)...")
        await asyncio.sleep(1)
        parsed_posts.append(f"VK пост из {group}: Ребята, запускаем курс!")

    print(f"[Agent_Analyst] ✅ Парсинг завершен. Собрано {len(parsed_posts)} текстов и {len(downloaded_media)} медиафайлов.")
    
    # Сжатие
    from skills.repowise_compressor import RepowiseCompressorSkill
    compressor = RepowiseCompressorSkill()
    compressed_posts = compressor.compress_posts(parsed_posts)
    
    return compressed_posts, downloaded_media
"""

op_code = re.sub(
    r'\s*print\(f"\[Agent_Analyst\].*?return compressed_posts\n',
    new_analyst,
    op_code,
    flags=re.DOTALL
)

# Update run_onboarding background_analysis to accept 2 values
op_code = op_code.replace(
    'posts = await analyst_parser(user_data)',
    'posts, downloaded_media = await analyst_parser(user_data)'
)
op_code = op_code.replace(
    'clean_posts, visuals = await visual_director_vqa(posts, user_data["uploaded_photos"])',
    'clean_posts, visuals = await visual_director_vqa(posts, user_data["uploaded_photos"] + downloaded_media)'
)

with open('onboarding_pipeline.py', 'w', encoding='utf-8') as f:
    f.write(op_code)

print("Updated telethon_collector.py and onboarding_pipeline.py")
