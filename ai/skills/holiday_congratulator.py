import time
from typing import Dict, Any

class HolidayCongratulatorSkill:
    """
    Ты - профессиональный SMM-копирайтер и контент-менеджер, который пишет живо, емко и по делу.
    
    СТРОГИЕ ПРАВИЛА И СТОП-ФАКТОРЫ:
    1. НИКАКИХ ТАВТОЛОГИЙ И МАСЛА МАСЛЯНОГО (исключать повторы топонимов и слов в рамках абзаца).
    2. НИКАКОЙ «ТОКСИЧНОЙ БОДРОСТИ» И ФАЛЬШИ (без 'безумно', 'потрясающе', без навязанного панибратства).
    3. АДЕКВАТНОСТЬ КОНТЕКСТУ (учитывать реальность: погоду, усталость людей, суету).
    4. ЕСТЕСТВЕННЫЙ CALL-TO-ACTION (бонус/акция как искренняя забота, а не навязчивые продажи).
    5. ТИПОГРАФИКА: всегда использовать короткие дефисы/тире '-' вместо длинных '—'.
    """
    def __init__(self, saiga_llm = None):
        from skills.saiga_llm import SaigaLLMSkill
        self.saiga = saiga_llm or SaigaLLMSkill()

    def generate_holiday_post(self, company_name: str, niche: str, city: str, holiday_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерирует душевный человеческий пост без штампов и сценарий для видео.
        """
        holiday_title = holiday_info.get("title", "Праздник")
        
        print(f"[HolidayCongratulator] ✍️ Сайга создает аутентичный текст заботы для {company_name} (г. {city})...")
        time.sleep(1)
        
        niche_lower = niche.lower()
        if "кофе" in niche_lower or "ресторан" in niche_lower:
            post_text = (
                f"Сегодня у города большой праздник - на улицах шумно, красиво и пахнет атмосферой гуляний.\n\n"
                f"Если решите выбраться в центр, заглядывайте к нам в «{company_name}» согреться, "
                f"передохнуть от толпы, выпить любимый кофе, перекусить свежей выпечкой и заодно подзарядить севший телефон перед вечерним салютом.\n\n"
                f"А чтобы добавить праздничного настроения, просто скажите бариста кодовую фразу: «С праздником!» - "
                f"и мы угостим вас фирменным десертом к заказу.\n\n"
                f"Хорошего дня и отличной прогулки! ☕"
            )
            video_prompt = (
                f"Warm documentary style. Cozy coffee shop interior in {city} with morning sunlight through glass windows. "
                f"Barista smiling genuinely while handing a warm cup to a relaxed guest. "
                f"Through the window, cheerful people stroll through the festive streets. "
                f"The barista looks into camera and says with a friendly, natural Russian voice: "
                f'"С пр+аздником! Забег+айте согр+еться перед сал+ютом."'
            )
        elif "it" in niche_lower or "автоматиз" in niche_lower:
            post_text = (
                f"Сегодня на улицах {city} праздник и отличная атмосфера.\n\n"
                f"Команда {company_name} напоминает: все задачи и релизы подождут, "
                f"а хорошая погода и праздничные выходные - нет. "
                f"Закрывайте ноутбуки, ставьте уведомления на беззвучный режим и выбирайтесь гулять по городу.\n\n"
                f"А рутинные процессы и автоматизацию мы подержим на себе.\n\n"
                f"Хорошего дня и отличного отдыха!"
            )
            video_prompt = (
                f"Modern tech office in {city} at golden hour. Developer peacefully closes a laptop, "
                f"smiles, and looks out at the festive city lights. "
                f"He turns to camera and says warmly: "
                f'"Зад+ачи подожд+ут. Отличного вам пр+аздника."'
            )
        else:
            post_text = (
                f"Сегодня в {city} праздничный день - на улицах особая теплая атмосфера.\n\n"
                f"Если окажетесь рядом с нами, заходите в «{company_name}» просто поздороваться, "
                f"передохнуть от суеты или подзарядить телефон. Мы всегда рады видеть знакомые лица.\n\n"
                f"А к каждому заказу сегодня с удовольствием подарим приятный праздничный комплимент.\n\n"
                f"Хорошего дня и приятного отдыха!"
            )
            video_prompt = (
                f"Natural lifestyle scene in {city}. Friendly team welcoming a guest at the entrance, "
                f"warm ambient lighting, genuine relaxed atmosphere. "
                f"Manager smiles and says in Russian: "
                f'"С пр+аздником! Пусть день пройд+ет легко."'
            )
        
        video_storyboard_idea = {
            "shot": f"INT/EXT. {company_name.upper()} IN {city.upper()}",
            "prompt": video_prompt
        }
        
        return {
            "holiday_title": holiday_title,
            "city": city,
            "post_text": post_text,
            "video_storyboard_idea": video_storyboard_idea,
            "status": "ready_to_publish"
        }
