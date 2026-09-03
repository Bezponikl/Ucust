# File: skills/critic_munger.py
"""
Agent Critic Charlie Munger 2.0: 6-Level Professional Marketing & Editorial Audit Engine.
1. The One Thing (Единственная цель и одно понятное целевое действие).
2. Slippery Slope (Скользкая дорожка Шугермана: хук за 3 секунды, zero-fluff).
3. WIIFM / 'И чё?' (Свойства переведены в личную пользу и экономию клиента).
4. Tone of Voice & Brand Identity (Узнаваемый голос эксперта, ноль штампов).
5. Visual Rhythm & Scan (Скан глазами, короткие абзацы до 4 строк, ритмика).
6. Platform Nativity (Нативный формат для Telegram/VK без кричащей мишуры).
"""

from __future__ import annotations
import re
from typing import Dict, Any, List, Optional

class CriticMungerSkill:
    STOP_CLICHES = [
        'динамично развивающаяся', 'команда профессионалов', 'индивидуальный подход',
        'лучшее качество', 'доступным ценам', 'широкий спектр', 'не упустите',
        'высокий уровень', 'лидеры рынка', 'уникальное предложение', 'встречайте наше',
        'встречайте наш', 'это не просто', 'крушить барьеры', 'руинах обыденности',
        'сверхъестественн', 'выстрел в мир', 'держись крепче'
    ]

    def __init__(self, strictness: float = 0.85):
        self.strictness = strictness

    def review_content(self, text: str, topic: str = '', target_audience: str = '') -> Dict[str, Any]:
        if not text or len(text.strip()) < 20:
            return {
                'passed': False, 'score': 0.2, 'verdict': 'REJECT',
                'criticism': 'Текст пустой или слишком короткий.',
                'actionable_feedback': 'Напишите полноценный текст с хуком и оффером.',
                'fatal_flaws': ['Текст не несет пользы.']
            }

        fatal_flaws: List[str] = []
        cautions: List[str] = []
        audit_breakdown: Dict[str, bool] = {}
        score = 1.0
        text_clean = text.strip()
        text_lower = text_clean.lower()
        lines = [line.strip() for line in text_clean.splitlines() if line.strip()]

        # =========================================================================
        # 1. ТЕСТ НА «ГЛАВНУЮ ЗАДАЧУ» (THE ONE THING)
        # =========================================================================
        cta_keywords = ['напишите', 'переходите', 'ссылк', 'жмите', 'пишите', 'забирайте', 'промокод', 'оставляйте', 'заказывайте', 'делитесь', 'комментари', 'личные сообщения', 'лс']
        found_ctas = [k for k in cta_keywords if k in text_lower]
        if not found_ctas:
            score -= 0.15
            fatal_flaws.append('Нет понятного Call to Action (The One Thing не определен).')
            audit_breakdown['the_one_thing'] = False
        else:
            audit_breakdown['the_one_thing'] = True

        # =========================================================================
        # 2. ОЦЕНКА ПО ФОРМУЛЕ «СКОЛЬЗКОЙ ДОРОЖКИ» ДЖОЗЕФА ШУГЕРМАНА (SLIPPERY SLOPE)
        # =========================================================================
        first_line = lines[0] if lines else ""
        if len(first_line) < 12:
            score -= 0.10
            cautions.append('Слишком короткий заголовок (не успевает зацепить любопытство).')
            audit_breakdown['slippery_slope'] = False
        elif any(w in first_line.lower() for w in ['привет', 'здравствуйте', 'всем привет', 'встречайте']):
            score -= 0.15
            fatal_flaws.append('Скучный зачин («Привет»/«Встречайте») ломает скользкую дорожку на первых 3 секундах.')
            audit_breakdown['slippery_slope'] = False
        else:
            audit_breakdown['slippery_slope'] = True

        # =========================================================================
        # 3. ТЕСТ НА «И ЧЁ?» (WIIFM — WHAT'S IN IT FOR ME)
        # =========================================================================
        has_numbers_or_metrics = bool(re.search(r'\d+', text_clean))
        benefit_markers = ['эконом', 'гаранти', 'быстр', 'надежн', 'удобн', 'защит', 'легк', 'выгод', 'решени', 'помож', 'без ', 'сократ']
        has_benefit = any(b in text_lower for b in benefit_markers)
        if not has_numbers_or_metrics or not has_benefit:
            score -= 0.15
            cautions.append('Тест «И чё?»: мало оцифрованной пользы для клиента (добавьте цифры, экономию времени/денег).')
            audit_breakdown['wiifm_benefit'] = False
        else:
            audit_breakdown['wiifm_benefit'] = True

        # =========================================================================
        # 4. ТЕСТ НА «УЗНАВАЕМОСТЬ БРЕНДА» (TONE OF VOICE)
        # =========================================================================
        found_cliches = [c for c in self.STOP_CLICHES if c in text_lower]
        if found_cliches:
            score -= 0.15 * len(found_cliches)
            fatal_flaws.append(f'Нарушение Tone of Voice: обнаружены штампы {found_cliches}.')
            audit_breakdown['brand_voice'] = False
        else:
            audit_breakdown['brand_voice'] = True

        # =========================================================================
        # 5. ВИЗУАЛЬНЫЙ СКАН И РИТМ ТЕКСТА
        # =========================================================================
        paragraphs = [p.strip() for p in text_clean.split("\n\n") if p.strip()]
        has_good_paragraphs = len(paragraphs) >= 2 and all(len(p.splitlines()) <= 5 for p in paragraphs)
        if not has_good_paragraphs and len(text_clean) > 250:
            score -= 0.15
            fatal_flaws.append('Визуальный скан: слишком плотный текст, разбейте на абзацы по 3-4 строки.')
            audit_breakdown['visual_scan_rhythm'] = False
        else:
            audit_breakdown['visual_scan_rhythm'] = True

        # =========================================================================
        # 6. СООТВЕТСТВИЕ КОНТЕКСТУ ПЛОЩАДКИ (TELEGRAM-NATIVITY)
        # =========================================================================
        emoji_count = len(re.findall(r'[\U00010000-\U0010ffff]', text_clean))
        if emoji_count > 6:
            score -= 0.10
            cautions.append(f'Перебор с эмодзи ({emoji_count} шт.) — снижает доверие в Telegram, оставьте 2-3.')
            audit_breakdown['platform_nativity'] = False
        else:
            audit_breakdown['platform_nativity'] = True

        score = max(0.1, min(1.0, round(score, 2)))
        passed = score >= self.strictness

        if passed:
            verdict = 'APPROVED'
            criticism = 'Текст полностью прошел 6 тестов: сильный хук Шугермана, одна главная задача (The One Thing), четкая выгода WIIFM и идеальный ритм.'
            actionable_feedback = 'Готово к публикации.'
        else:
            verdict = 'REVISE_NEEDED'
            reasons = fatal_flaws + cautions
            criticism = f'Текст требует доработки: {reasons[:2]}'
            feedback_parts = []
            if any('штампы' in f for f in fatal_flaws): feedback_parts.append('Убери штампы и клише, говори на языке фактов.')
            if any('зачин' in f or 'хук' in f for f in fatal_flaws + cautions): feedback_parts.append('Удали приветствие/встречайте, начни сразу с инсайта или боли.')
            if any('И чё' in c for c in cautions): feedback_parts.append('Переведи характеристики в осязаемую выгоду для клиента (WIIFM).')
            if any('Action' in f for f in fatal_flaws): feedback_parts.append('Оставь один четкий призыв к действию (The One Thing).')
            if any('скан' in f for f in fatal_flaws): feedback_parts.append('Разбей простыню на короткие абзацы по 3-4 строки.')
            actionable_feedback = ' '.join(feedback_parts) or 'Усильте выгоду для клиента и ритмику текста.'

        return {
            'passed': passed,
            'score': score,
            'verdict': verdict,
            'criticism': criticism,
            'fatal_flaws': fatal_flaws,
            'cautions': cautions,
            'audit_breakdown': audit_breakdown,
            'actionable_feedback': actionable_feedback
        }
