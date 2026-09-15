"""
Political, Legal, and Compliance Security Guard for UCust AI.
=============================================================
Enforces 100% Zero-Politics & Legal Compliance (Russian Federation & International Safety):
1. Complete ban on political events, officials, military conflicts, and protests.
2. Ban on extremism, terrorism, hate speech, weapons, drugs, 18+ content, fraud.
3. Advanced Jailbreak / Prompt Injection mitigation (Role-shift, DAN, Base64/Hex).
4. Dual-pass inspection: Raw Input Inspection & Output Validation.
"""

import re
import logging
from typing import Tuple, List, Optional
from skills.adversarial_normalizer import AdversarialNormalizer

logger = logging.getLogger("security_guard")


class PoliticalAndLegalGuard:
    # 1. Политический контекст, органы власти, военные темы, протесты
    POLITICAL_AND_MILITARY_PATTERNS = [
        r"(?:путин|зеленск|байден|трамп|навальн|госдум|правительств|миноборон|росгварди|кремл|белый дом|политик)",
        r"(?:сво\b|спецопераци|войн[а-я]|всу\b|вс рф|оккупаци|аннекси|санкци[ия]|мобилизаци)",
        r"(?:митинг|протест|забастовк|пикет|оппозици|шестви[ея]|госпереворот|революци|бунт)",
        r"(?:дискредитац|фейк|выбор[ыа]|голосован|парти[яи]|депутат|политзаключен)"
    ]

    # 2. Экстремизм, насилие, терроризм, оружие, наркотики, криминал
    EXTREMISM_AND_CRIME_PATTERNS = [
        r"(?:террориз|экстремиз|диверси|теракт|игил|нацизм|фашизм|расизм|свастик|геноцид)",
        r"(?:взрывчатк|детонатор|автомат калашников|оружи[ея]|пистолет|патрон)",
        r"(?:наркотик|кокаин|героин|мефедрон|марихуан|закладк|даркнет|гидр[а-я])",
        r"(?:суицид|самоубийств|порно|инцест|педофил|убийств)",
        r"(?:казино|ставк[иа]|рулетк|1xbet|вулкан|пирамид|кардинг|взлом аккаунт)"
    ]

    # 3. Атаки на снятие ограничений (Jailbreak / Prompt Injection / System Disclosure)
    JAILBREAK_AND_INJECTION_PATTERNS = [
        r"(?:ignore (?:all |previous |above )?instructions|забудь (?:все |предыдущие )?инструкции)",
        r"(?:you are now|ты теперь|действуй как|act as (?:dan|jailbreak|unfiltered|evil))",
        r"(?:system prompt|системный промпт|выведи системный|show system prompt)",
        r"(?:dump database|выгрузи базу|покажи пароли|select \* from|drop table)",
        r"(?:bypass safety|отключи фильтры|без цензуры|uncensored mode)"
    ]

    SAFE_REJECTION_MESSAGE = (
        "⚠️ Запрос отклонен системой безопасности UCust: платформа предназначена "
        "исключительно для коммерческого маркетинга и продвижения легального бизнеса. "
        "Генерация политического, противоправного и нецелевого контента строго заблокирована."
    )

    @classmethod
    def validate_content(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        Проверяет входной или выходной текст на соответствие политикам безопасности.
        Использует многослойную деобфускацию (раскладка, омоглифы, Base64, разделители).
        
        Returns:
            (is_safe: bool, violation_reason: Optional[str])
        """
        if not text or not text.strip():
            return True, None

        # 1. Генерируем все проекции деобфускации
        projections = AdversarialNormalizer.generate_normalized_projections(text)

        all_rules = [
            ("Политический / Военный контекст", cls.POLITICAL_AND_MILITARY_PATTERNS),
            ("Экстремизм / Оружие / Запрещенные вещества", cls.EXTREMISM_AND_CRIME_PATTERNS),
            ("Попытка Prompt Injection / Jailbreak", cls.JAILBREAK_AND_INJECTION_PATTERNS),
        ]

        for category, patterns in all_rules:
            for pattern in patterns:
                regex = re.compile(pattern, re.IGNORECASE)
                for proj in projections:
                    if regex.search(proj):
                        logger.warning(
                            f"[SecurityGuard] 🚨 СРАБОТАЛА БЛОКИРОВКА [{category}]: "
                            f"Обнаружен паттерн '{pattern}' в проекции '{proj[:60]}...'"
                        )
                        return False, category

        return True, None

    @classmethod
    def sanitize_output(cls, generated_text: str) -> str:
        """
        Проверяет сгенерированный LLM текст.
        Если обнаружено нарушение — заменяет его на безопасный отказ.
        """
        is_safe, reason = cls.validate_content(generated_text)
        if not is_safe:
            logger.error(f"[SecurityGuard] 🛑 Блокировка на выходе LLM: {reason}")
            return cls.SAFE_REJECTION_MESSAGE
        return generated_text
