# File: publishers/achievement_broadcaster.py
"""
Achievement Broadcaster for UCust AI Telegram Channel (@UcustAi / t.me/UcustAi).
Publishes major milestones, campaign breakthroughs, video generations, and brand analytics.
"""

from __future__ import annotations

import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    from telethon import TelegramClient
except ImportError:
    TelegramClient = None

class AchievementBroadcaster:
    DEFAULT_CHANNEL = "@UcustAi"

    def __init__(self, target_channel: Optional[str] = None):
        self.target_channel = target_channel or os.getenv("UCUST_ACHIEVEMENT_CHANNEL", self.DEFAULT_CHANNEL)
        self.api_id = os.getenv("TELETHON_API_ID") or os.getenv("TELEGRAM_API_ID", "37805806")
        self.api_hash = os.getenv("TELETHON_API_HASH") or os.getenv("TELEGRAM_API_HASH", "3edb95f2db1a5bf4d67608d79db10bbf")
        
        # Находим файл сессии
        self.session_name = self._resolve_session_name()

    def _resolve_session_name(self) -> str:
        session_base = os.getenv("TELETHON_SESSION", "ucust_session").strip()
        candidates = [
            session_base,
            os.path.join("ai", session_base),
            os.path.join(os.path.dirname(__file__), "..", session_base),
            os.path.join("/opt/ucust/ai", session_base)
        ]
        for c in candidates:
            if os.path.exists(f"{c}.session"):
                return c
        return session_base

    def format_milestone_post(
        self,
        title: str,
        description: str,
        metrics: Optional[List[str]] = None,
        category: str = "Релиз / Достижение",
        author_agent: str = "Команда ИИ-агентов UCust"
    ) -> str:
        """
        Форматирует красивый, презентабельный пост для канала @UcustAi.
        """
        now_str = datetime.now().strftime("%d.%m.%Y")
        
        lines = [
            f"🚀 <b>UCust AI: {title}</b>",
            f"📅 <i>{now_str}</i> | 🏷️ <code>#{category.replace(' ', '_')}</code>",
            "",
            f"🔥 <b>Ключевые изменения:</b>",
            f"{description.strip()}",
            ""
        ]

        if metrics:
            lines.append("📊 <b>Ключевые показатели:</b>")
            for m in metrics:
                lines.append(f" • {m}")
            lines.append("")

        lines.append(f"⚡ <i>Автономно подтверждено: {author_agent}</i>")
        lines.append("")
        lines.append("#UCust #Достижения")

        raw_post = "\n".join(lines)
        
        # Строгая защита коммерческой тайны: фильтрация любых внутренних моделей, нод и параметров
        try:
            from core.orchestrator import SecurityGuard
            return SecurityGuard.sanitize_public_text(raw_post)
        except Exception:
            return raw_post

    def _get_proxy_config(self) -> Optional[dict]:
        proxy_url = os.getenv("TELETHON_PROXY_URL", "").strip()
        proxy_type_env = os.getenv("TELETHON_PROXY_TYPE", "").strip().lower()
        proxy_host = os.getenv("TELETHON_PROXY_HOST", "").strip()
        proxy_port = os.getenv("TELETHON_PROXY_PORT", "").strip()
        proxy_user = os.getenv("TELETHON_PROXY_USER", "").strip() or None
        proxy_pass = os.getenv("TELETHON_PROXY_PASSWORD", "").strip() or None

        if proxy_url:
            import urllib.parse
            parsed = urllib.parse.urlparse(proxy_url)
            proxy_type_env = parsed.scheme.lower()
            proxy_host = parsed.hostname or ""
            proxy_port = str(parsed.port or 1080)
            proxy_user = parsed.username
            proxy_pass = parsed.password

        if not proxy_host or not proxy_port or not proxy_port.isdigit():
            return None

        ptype = 2 if "socks5" in proxy_type_env else (1 if "socks4" in proxy_type_env else 3)
        return {
            'proxy_type': ptype,
            'addr': proxy_host,
            'port': int(proxy_port),
            'username': proxy_user,
            'password': proxy_pass,
            'rdns': True
        }

    async def broadcast_milestone_async(
        self,
        title: str,
        description: str,
        metrics: Optional[List[str]] = None,
        media_path: Optional[str] = None,
        category: str = "Достижение",
        author_agent: str = "Команда ИИ-агентов UCust"
    ) -> Dict[str, Any]:
        """
        Асинхронная публикация достижения в Telegram-канал @UcustAi.
        """
        post_text = self.format_milestone_post(
            title=title,
            description=description,
            metrics=metrics,
            category=category,
            author_agent=author_agent
        )

        if not TelegramClient:
            return {
                "status": "warning",
                "message": "Telethon не установлен. Пост сформирован, но не отправлен.",
                "post_preview": post_text
            }

        try:
            api_id_int = int(self.api_id)
        except Exception:
            return {
                "status": "error",
                "message": f"Некорректный API_ID: {self.api_id}"
            }

        proxy = self._get_proxy_config()
        client = TelegramClient(
            self.session_name,
            api_id_int,
            self.api_hash,
            proxy=proxy,
            timeout=30.0,
            use_ipv6=False,
            connection_retries=5
        )
        
        try:
            await client.connect()
            if not await client.is_user_authorized():
                await client.disconnect()
                print(f"[AchievementBroadcaster] ⚠️ Сессия {self.session_name} не авторизована!")
                return {
                    "status": "error",
                    "message": "Сессия Telethon не авторизована. Требуется подтверждение номера.",
                    "post_preview": post_text
                }

            # Отправка медиа или текста
            if media_path and os.path.exists(media_path):
                print(f"[AchievementBroadcaster] Sending media '{media_path}' to {self.target_channel}...")
                await client.send_file(
                    self.target_channel,
                    media_path,
                    caption=post_text,
                    parse_mode="html"
                )
            else:
                print(f"[AchievementBroadcaster] Sending text post to {self.target_channel}...")
                await client.send_message(
                    self.target_channel,
                    post_text,
                    parse_mode="html"
                )

            await client.disconnect()
            print(f"[AchievementBroadcaster] Post published successfully to {self.target_channel}!")
            return {
                "status": "success",
                "channel": self.target_channel,
                "title": title,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as exc:
            try:
                await client.disconnect()
            except Exception:
                pass
            print(f"[AchievementBroadcaster] Error during publication: {exc}")
            return {
                "status": "error",
                "error": str(exc),
                "channel": self.target_channel,
                "post_preview": post_text
            }
