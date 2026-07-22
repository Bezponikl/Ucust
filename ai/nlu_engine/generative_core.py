"""
Нейросетевой генеративный модуль (заглушка) для стратегии.
"""

from __future__ import annotations

from typing import List

from schemas.models import StrategyPlanSchema


class GenerativeCore:
    """
    Нейросетевой генеративный модуль для генерации стратегий.

    В реальной системе может использовать Saiga для генерации контента.
    """

    def process_request(self, context: str) -> StrategyPlanSchema:
        """
        Имитирует генерацию стратегии на основе входного контекста.

        :param context: агрегированный контекст.
        :return: стратегия, риски и рекомендации.
        """

        strategy = f"Стратегия сформирована для контекста: {context[:120]}..."
        risks: List[str] = ["Недостаточно данных о конкурентах", "Слабая уникальность контента"]
        recommendations: List[str] = ["Уточнить позиционирование", "Провести тестовый спринт публикаций"]
        technical_log = [
            "Нейросетевой генеративный модуль: старт",
            "Нейросетевой генеративный модуль: контекст обработан",
            "Нейросетевой генеративный модуль: стратегия сформирована",
        ]
        return StrategyPlanSchema(
            strategy=strategy,
            risks=risks,
            recommendations=recommendations,
            technical_log=technical_log,
        )

    def verify_facts(
        self,
        system_prompt: str,
        facts_context: str,
        draft_text: str,
    ) -> tuple[str, List[str]]:
        """
        Имитирует верификацию фактов нейросетью Saiga на основе системного промпта.

        :param system_prompt: Системный промпт фактчекера.
        :param facts_context: Совокупность исходных фактов (SWOT + стратегия).
        :param draft_text: Исходный черновик текста.
        :return: Кортеж (очищенный текст, список удаленных утверждений/галлюцинаций).
        """
        removed_claims: List[str] = []
        cleaned_text = draft_text

        # Пример очистки недоказанных утверждений или чисел
        if ("100%" in draft_text or "гарантия" in draft_text.lower() or "unverified_claim" in draft_text.lower()) and "ПРЕДЫДУЩАЯ ОШИБКА" not in draft_text:
            removed_claims.append("Удалены невалидированные метрики эффективности и суперлативы.")
            cleaned_text = draft_text.replace("100%", "").replace("гарантия", "").replace("unverified_claim", "")

        return cleaned_text, removed_claims
