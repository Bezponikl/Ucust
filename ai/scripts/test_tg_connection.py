# File: scripts/test_tg_connection.py
"""
Diagnostic tool to test Telegram MTProto connection from server/local machine.
"""

import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from telethon import TelegramClient
from telethon.network import connection

API_ID = int(os.getenv("TELETHON_API_ID", "37805806"))
API_HASH = os.getenv("TELETHON_API_HASH", "3edb95f2db1a5bf4d67608d79db10bbf")
SESSION_PATHS = [
    "ucust_session",
    "ai/ucust_session",
    "/opt/ucust/ai/ucust_session"
]

async def test_conn():
    print("=" * 60)
    print("🔍 ДИАГНОСТИКА ПОДКЛЮЧЕНИЯ TELEGRAM TELETHON")
    print("=" * 60)

    # 1. Проверяем файл сессии
    found_session = None
    for p in SESSION_PATHS:
        if os.path.exists(f"{p}.session"):
            found_session = p
            size = os.path.getsize(f"{p}.session")
            print(f"✅ Файл сессии найден: {p}.session ({size} байт)")
            break

    if not found_session:
        print("❌ Файл ucust_session.session НЕ НАЙДЕН в папках:")
        for p in SESSION_PATHS:
            print(f"   • {os.path.abspath(p)}.session")
        return

    # 2. Пробуем разные протоколы подключения
    conn_modes = [
        ("ConnectionTcpAbridged (Стандартный Abridged)", connection.ConnectionTcpAbridged),
        ("ConnectionTcpIntermediate (Обход блокировок Intermediate)", connection.ConnectionTcpIntermediate),
        ("ConnectionTcpFull (Полный TCP)", connection.ConnectionTcpFull),
        ("ConnectionHttp (HTTP Transport)", connection.ConnectionHttp),
    ]

    for name, conn_class in conn_modes:
        print(f"\n⏳ Пробуем подключение через {name}...")
        client = TelegramClient(
            found_session,
            API_ID,
            API_HASH,
            connection=conn_class,
            timeout=10.0,
            use_ipv6=False,
            connection_retries=2
        )
        try:
            await asyncio.wait_for(client.connect(), timeout=12.0)
            is_auth = await client.is_user_authorized()
            if is_auth:
                me = await client.get_me()
                username = f"@{me.username}" if me.username else me.first_name
                print(f"🎉 УСПЕХ! Подключено через {name}!")
                print(f"👤 Авторизован как: {me.first_name} ({username})")
                await client.disconnect()
                return conn_class
            else:
                print(f"⚠️ Подключено, но требуется повторная авторизация.")
                await client.disconnect()
                return
        except Exception as e:
            print(f"❌ Ошибка ({name}): {type(e).__name__} - {e}")
            try:
                await client.disconnect()
            except Exception:
                pass

    print("\n" + "=" * 60)
    print("⚠️ ПРЯМОЙ MTPROTO ТРАФИК БЛОКИРУЕТСЯ ДАТАЦЕНТРОМ.")
    print("Рекомендуется добавить SOCKS5 / MTProto прокси в .env:")
    print("TELETHON_PROXY_HOST=... TELETHON_PROXY_PORT=...")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_conn())
