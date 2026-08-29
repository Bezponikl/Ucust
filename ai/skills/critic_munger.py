# File: skills/critic_munger.py
from __future__ import annotations
import re
from typing import Dict, Any, List

class CriticMungerSkill:
    STOP_CLICHES = [
        'динамично развивающаяся', 'команда профессионалов', 'индивидуальный подход',
        'лучшее качество', 'доступным ценам', 'широкий спектр', 'не упустите',
        'высокий уровень', 'лидеры рынка', 'уникальное предложение'
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
        fatal_flaws, cautions = [], []
        score = 1.0
        text_lower = text.lower()
        found_cliches = [c for c in self.STOP_CLICHES if c in text_lower]
        if found_cliches:
            score -= 0.15 * len(found_cliches)
            fatal_flaws.append(f'Обнаружены штампы: {found_cliches}')
        first_line = text.strip().split('\n')[0]
        if len(first_line) < 15:
            score -= 0.15
            cautions.append('Слабый заголовок/первая строка.')
        elif any(w in first_line.lower() for w in ['привет', 'здравствуйте', 'всем привет']):
            score -= 0.15
            fatal_flaws.append('Скучное приветствие вместо интригующего хука.')
        if not re.search(r'\d+', text):
            score -= 0.1
            cautions.append('Нет конкретных цифр, сроков или цен.')
        if not any(w in text_lower for w in ['напишите', 'переходите', 'ссылк', 'жмите', 'пишите', 'забирайте', 'промокод', 'оставляйте', 'звоните', 'заказывайте']):
            score -= 0.15
            fatal_flaws.append('Нет понятного Call to Action (призыва к действию).')
        paragraphs = [p for p in text.split('\n') if p.strip()]
        if len(paragraphs) <= 1 and len(text) > 200:
            score -= 0.15
            fatal_flaws.append('Сплошная простыня текста без разбивки на абзацы.')
        score = max(0.1, min(1.0, round(score, 2)))
        passed = score >= self.strictness
        if passed:
            verdict = 'APPROVED'
            criticism = 'Текст сфокусирован, без лишней воды и штампов. Сильный хук.'
            actionable_feedback = 'Готово к публикации.'
        else:
            verdict = 'REVISE_NEEDED'
            reasons = fatal_flaws + cautions
            criticism = f'Текст требует доработки: {reasons[:2]}'
            feedback_parts = []
            if any('штампы' in f for f in fatal_flaws): feedback_parts.append('Убери общие фразы, добавь факты.')
            if any('приветствие' in f for f in fatal_flaws): feedback_parts.append('Удали приветствие, начни сразу с инсайта.')
            if any('цифр' in c for c in cautions): feedback_parts.append('Добавь точные цифры или сроки.')
            if any('Action' in f for f in fatal_flaws): feedback_parts.append('Добавь четкий призыв к действию в конце.')
            if any('простыня' in f for f in fatal_flaws): feedback_parts.append('Разбей текст на короткие абзацы.')
            actionable_feedback = ' '.join(feedback_parts) or 'Усильте ценность оффера.'
        return {
            'passed': passed, 'score': score, 'verdict': verdict,
            'criticism': criticism, 'fatal_flaws': fatal_flaws, 'cautions': cautions,
            'actionable_feedback': actionable_feedback
        }
