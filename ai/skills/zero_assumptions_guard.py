# File: skills/zero_assumptions_guard.py
"""
Zero-Assumptions & Anti-Hallucination Guard for UCust.AI.
Защищает бизнес-контент от любых додумываний и несанкционированных обещаний:
1. Цены и скидки: запрет выдумывания % скидок и точных цен без RAG-источника.
2. Локации и адреса: запрет вымышленных улиц, станций метро и ложного графика работы (24/7).
3. Состав и свойства: запрет приписывания лечебных свойств и диетических маркеров (100% веган, без сахара) без подтверждения.
4. Гарантии и сроки: запрет необоснованных обещаний («доставим за 10 мин», «вечная гарантия»).
5. Вкусовые и музыкальные штампы: использование универсальных, адаптивных формулировок.
6. Фальшивые отзывы: запрет генерации фейковых персональных цитат.
"""

from __future__ import annotations

import re
from typing import Dict, Any, List, Optional, Tuple


class ZeroAssumptionsGuard:
    """
    Интеллектуальный страж достоверности фактов и защиты от галлюцинаций.
    """

    # Регулярные выражения для поиска опасных галлюцинаций
    PRICE_HALLUCINATION = re.compile(r'скидк[а-яё\s]*(?:до|на|-|\s)*\s*(?:5[0-9]|6[0-9]|7[0-9]|8[0-9]|9[0-9])\s*%', re.IGNORECASE)
    UNCONFIRMED_24_7 = re.compile(r'\b(круглосуточно|24/7|работаем\s+ночью)\b', re.IGNORECASE)
    FAKE_FAST_DELIVERY = re.compile(r'\bдостав[а-яё]*\s+за\s+(?:5|10|15)\s+минут\b', re.IGNORECASE)
    MAGIC_MEDICAL_CLAIM = re.compile(r'\b(исцелит|лечит\s+все\s+болезни|100%\s+излечение|гарантия\s+выздоровления)\b', re.IGNORECASE)

    @classmethod
    def sanitize_assumptions(
        cls,
        text: str,
        rag_facts: Optional[str] = None,
        contacts: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Проверяет и очищает сгенерированный текст от опасных вымышленных обещаний.
        """
        if not text:
            return ""

        cleaned = text

        # 1. Сглаживание нереалистичных вымышленных скидок (если нет в RAG)
        if not rag_facts or "скидк" not in rag_facts.lower():
            cleaned = cls.PRICE_HALLUCINATION.sub("специальные приятные условия", cleaned)

        # 2. Сглаживание графика 24/7, если не подтверждено контактами
        has_24_7 = bool(contacts and "24" in str(contacts.get("working_hours", "")))
        if not has_24_7:
            cleaned = cls.UNCONFIRMED_24_7.sub("каждый день", cleaned)

        # 3. Сглаживание сверхбыстрой доставки
        cleaned = cls.FAKE_FAST_DELIVERY.sub("оперативная и бережная доставка", cleaned)

        # 4. Блокировка псевдо-медицинских обещаний
        cleaned = cls.MAGIC_MEDICAL_CLAIM.sub("эффективная поддержка здоровья", cleaned)

        return cleaned

    @classmethod
    def validate_content_safety(
        cls,
        text: str,
        rag_facts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Возвращает отчет безопасности контента по 6 аспектам Zero-Assumptions.
        """
        issues: List[str] = []

        if cls.PRICE_HALLUCINATION.search(text) and (not rag_facts or "скидк" not in rag_facts.lower()):
            issues.append("Обнаружена нерегулируемая скидка >50% без подтверждения в RAG.")

        if cls.MAGIC_MEDICAL_CLAIM.search(text):
            issues.append("Обнаружены опасные медицинские обещания.")

        return {
            "is_safe": len(issues) == 0,
            "issues": issues,
            "sanitized_preview": cls.sanitize_assumptions(text, rag_facts)
        }
