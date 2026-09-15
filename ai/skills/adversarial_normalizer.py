"""
Adversarial Text Normalizer for UCust AI Security Pipeline.
===========================================================
Detects and neutralizes obfuscation techniques used in Prompt Injections & Jailbreaks:
1. Keyboard layout swapping (QWERTY <-> ЙЦУКЕН).
2. Homoglyph substitution (Confusable Latin characters replacing Cyrillic).
3. Base64, Hex, and URL-encoding extraction.
4. Zero-width characters & punctuation splitting (Leetspeak / delimiter evasion).
5. Whitespace collapsing and canonical normalization.
"""

import base64
import re
import urllib.parse
from typing import List, Set


class AdversarialNormalizer:
    # QWERTY -> ЙЦУКЕН mapping
    EN_TO_RU_LAYOUT = str.maketrans(
        "qwertyuiop[]asdfghjkl;'zxcvbnm,./`QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?~",
        "йцукенгшщзхъфывапролджэячсмитьбю.ёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё"
    )

    # ЙЦУКЕН -> QWERTY mapping
    RU_TO_EN_LAYOUT = str.maketrans(
        "йцукенгшщзхъфывапролджэячсмитьбю.ёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё",
        "qwertyuiop[]asdfghjkl;'zxcvbnm,./`QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?~"
    )

    # Homoglyphs: Latin characters that visually mimic Cyrillic
    LATIN_TO_CYRILLIC_HOMOGLYPHS = str.maketrans({
        'a': 'а', 'A': 'А',
        'b': 'б', 'B': 'В',
        'c': 'с', 'C': 'С',
        'e': 'е', 'E': 'Е',
        'h': 'н', 'H': 'Н',
        'i': 'і', 'I': 'І',
        'j': 'ј', 'J': 'Ј',
        'k': 'к', 'K': 'К',
        'm': 'м', 'M': 'М',
        'o': 'о', 'O': 'О',
        'p': 'р', 'P': 'Р',
        's': 'с', 'S': 'С',
        't': 'т', 'T': 'Т',
        'x': 'х', 'X': 'Х',
        'y': 'у', 'Y': 'У'
    })

    # Cyrillic to Latin homoglyphs for English inspection
    CYRILLIC_TO_LATIN_HOMOGLYPHS = str.maketrans({
        'а': 'a', 'А': 'A',
        'В': 'B',
        'с': 'c', 'С': 'C',
        'е': 'e', 'E': 'E',
        'Н': 'H',
        'к': 'k', 'К': 'K',
        'М': 'M',
        'о': 'o', 'О': 'O',
        'р': 'p', 'Р': 'P',
        'с': 's', 'С': 'S',
        'Т': 'T',
        'х': 'x', 'Х': 'X',
        'у': 'y', 'У': 'Y'
    })

    ZERO_WIDTH_CHARS = re.compile(r'[\u200B-\u200D\u200E\u200F\uFEFF\u00AD\u2060]')

    @classmethod
    def decode_obfuscated_payloads(cls, text: str) -> List[str]:
        """Раскрывает скрытые закодированные фрагменты (URL-encode, Base64, Hex)."""
        decoded_tokens = []
        if not text:
            return decoded_tokens

        # 1. URL-decode
        try:
            url_unquoted = urllib.parse.unquote(text)
            if url_unquoted != text:
                decoded_tokens.append(url_unquoted)
        except Exception:
            pass

        # 2. Base64 detection & decode
        b64_matches = re.findall(r'[A-Za-z0-9+/]{6,}={0,2}', text)
        for chunk in b64_matches:
            try:
                decoded_bytes = base64.b64decode(chunk)
                decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
                if len(decoded_str.strip()) >= 3 and any(c.isalnum() for c in decoded_str):
                    decoded_tokens.append(decoded_str)
            except Exception:
                pass

        # 3. Hex detection & decode (e.g. 0x70 0x72 0x6f... or \x70\x72\x6f)
        hex_chunks = re.findall(r'(?:(?:0x|\\x|%)([0-9a-fA-F]{2}))+', text)
        if hex_chunks:
            try:
                clean_hex = re.sub(r'[^0-9a-fA-F]', '', text)
                if len(clean_hex) >= 6 and len(clean_hex) % 2 == 0:
                    hex_decoded = bytes.fromhex(clean_hex).decode('utf-8', errors='ignore')
                    if len(hex_decoded.strip()) >= 3:
                        decoded_tokens.append(hex_decoded)
            except Exception:
                pass

        return decoded_tokens

    @classmethod
    def remove_delimiter_spacing(cls, text: str) -> str:
        """
        Устраняет разделение букв спецсимволами и пробелами.
        Пример: 'п.р.о.т.е.с.т' -> 'протест', 'в_о_й_н_а' -> 'война', 'м и т и н г' -> 'митинг'.
        """
        # Склеиваем одиночные символы, разделенные разделителями
        collapsed = re.sub(r'(?<=[а-яёa-z0-9])[._\-\*\+\/\\|~#\s]+(?=[а-яёa-z0-9])', '', text, flags=re.IGNORECASE)
        return collapsed

    @classmethod
    def generate_normalized_projections(cls, text: str) -> List[str]:
        """
        Возвращает набор канонических проекций текста со снятыми слоями обфускации:
        1. Исходный очищенный текст.
        2. Текст со снятыми омоглифами (Латиница -> Кириллица).
        3. Текст со снятыми омоглифами (Кириллица -> Латиница).
        4. Текст в обратной раскладке (QWERTY -> ЙЦУКЕН).
        5. Текст в обратной раскладке (ЙЦУКЕН -> QWERTY).
        6. Раскодированные токены (Base64 / Hex / URL-decode).
        7. Текст со схлопнутыми разделителями (Leetspeak).
        """
        if not text:
            return []

        # 0. Удаляем Zero-Width символы
        base_clean = cls.ZERO_WIDTH_CHARS.sub('', text).strip()
        projections: Set[str] = set()

        # 1. Базовый
        projections.add(base_clean.lower())

        # 2. Схлопывание разделителей
        collapsed = cls.remove_delimiter_spacing(base_clean).lower()
        projections.add(collapsed)

        # 3. Омоглифы -> Кириллица (для базового и для схлопнутого)
        projections.add(base_clean.translate(cls.LATIN_TO_CYRILLIC_HOMOGLYPHS).lower())
        projections.add(collapsed.translate(cls.LATIN_TO_CYRILLIC_HOMOGLYPHS).lower())

        # 4. Омоглифы -> Латиница
        projections.add(base_clean.translate(cls.CYRILLIC_TO_LATIN_HOMOGLYPHS).lower())
        projections.add(collapsed.translate(cls.CYRILLIC_TO_LATIN_HOMOGLYPHS).lower())

        # 5. Раскладка QWERTY -> ЙЦУКЕН
        ru_layout = base_clean.translate(cls.EN_TO_RU_LAYOUT).lower()
        projections.add(ru_layout)
        projections.add(cls.remove_delimiter_spacing(ru_layout))
        projections.add(ru_layout.translate(cls.LATIN_TO_CYRILLIC_HOMOGLYPHS))

        # 6. Раскладка ЙЦУКЕН -> QWERTY
        en_layout = base_clean.translate(cls.RU_TO_EN_LAYOUT).lower()
        projections.add(en_layout)
        projections.add(cls.remove_delimiter_spacing(en_layout))

        # 7. Раскодированные полезные нагрузки
        for decoded in cls.decode_obfuscated_payloads(text):
            dec_clean = cls.ZERO_WIDTH_CHARS.sub('', decoded).strip().lower()
            projections.add(dec_clean)
            projections.add(cls.remove_delimiter_spacing(dec_clean))
            projections.add(dec_clean.translate(cls.LATIN_TO_CYRILLIC_HOMOGLYPHS))
            projections.add(dec_clean.translate(cls.EN_TO_RU_LAYOUT))

        return [p for p in projections if p]
