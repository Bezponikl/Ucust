"""
Заглушка модуля API-парсинга vk_api.
"""

from __future__ import annotations

from datetime import datetime

from schemas.models import CollectorDataSchema


class VkApiCollector:
    """
    Модуль асинхронного сбора данных из VK.

    Реализован как заглушка, имитирующая работу API-парсера vk_api.
    """

    def collect(self, group_id: str, limit: int = 10) -> CollectorDataSchema:
        """
        Имитирует сбор постов из сообщества VK.

        :param group_id: идентификатор сообщества.
        :param limit: количество постов.
        :return: результат парсинга.
        """

        mock_comments = [
            {"id": 201, "author": "Сергей", "text": "Где посмотреть примеры готовых постов?", "likes": 5},
            {"id": 202, "author": "Анна", "text": "Какая стоимость тарифа для малого бизнеса?", "likes": 8},
        ]

        payload = {
            "group_id": group_id,
            "limit": limit,
            "fetched_at": datetime.utcnow().isoformat(),
            "posts": [
                {
                    "id": i,
                    "text": f"Пост {i} из группы {group_id}. Практика ведения соцсетей с ИИ.",
                    "likes": 50 + i * 10,
                    "comments_count": len(mock_comments),
                    "comments": mock_comments,
                    "top_audience_questions": [
                        "Примеры готовых кейсов",
                        "Тарифы для малого бизнеса"
                    ]
                }
                for i in range(1, limit + 1)
            ],
        }
        return CollectorDataSchema(source="vk_api", payload=payload)
