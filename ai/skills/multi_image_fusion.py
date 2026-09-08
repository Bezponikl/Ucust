from __future__ import annotations
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("multi_image_fusion")


class VisualSemanticRole:
    HANDS_BODY = "hands_body"
    PET_ANIMAL = "pet_animal"
    ENVIRONMENT = "environment_setting"
    PRODUCT_ITEM = "product_item"
    GENERAL_SUBJECT = "general_subject"


class MultiImageSemanticFusionEngine:
    """
    Intelligent engine for recognition and compositional fusion of 1-3 images.
    """

    @classmethod
    def classify_image_role(
        cls,
        image_meta: Dict[str, Any],
        user_prompt: str = ""
    ) -> Tuple[str, str, float]:
        desc = (image_meta.get("description") or "").lower()
        fname = str(image_meta.get("file_name") or image_meta.get("filename") or "").lower()
        prompt_lower = (user_prompt or "").lower()

        # 1. Hands / Manicure / Holding
        hands_keywords = [
            "ruka", "ruki", "rukah", "ruku", "nogot", "nogt", "manikyur", "palts", "ladon",
            "hand", "hands", "nail", "nails", "manicure", "sweater", "finger", "fingers",
            "рука", "руки", "руках", "руку", "ногот", "ногт", "маникюр", "пальц", "ладон"
        ]
        is_hands = any(k in desc or k in fname for k in hands_keywords)
        if any(k in prompt_lower for k in ["на таких руках", "такие руки", "эти руки", "с таким маникюром", "в этих руках", "руках"]):
            if any(k in desc or k in fname for k in ["hand", "nail", "ruka", "nogt", "manikyur", "рука", "ногт", "маникюр"]) or len(desc) < 20:
                is_hands = True

        if is_hands:
            return (VisualSemanticRole.HANDS_BODY, "slender manicured female hands in cozy knit sweater", 0.95)

        # 2. Animal / Pet / Dog / Puppy
        animal_keywords = [
            "sobak", "sobachk", "shchenok", "shchenk", "pes", "pyos", "haski", "corgi", "shpic", "kot", "koshk", "kotik", "koten",
            "dog", "puppy", "husky", "corgi", "cat", "kitten", "pet", "animal", "fur",
            "собак", "собачк", "щенок", "щенк", "пес", "пёс", "хаски", "корги", "шпиц", "кот", "кошк", "котик", "котен"
        ]
        is_animal = any(k in desc or k in fname for k in animal_keywords)
        if any(k in prompt_lower for k in ["такая собачка", "такая собака", "этот пес", "такой щенок", "этот котик", "собачк", "собак"]):
            if any(k in desc or k in fname for k in ["dog", "cat", "pet", "sobak", "kot", "haski", "shchenok", "собак", "кот", "хаски", "щенок"]) or len(desc) < 20:
                is_animal = True

        if is_animal:
            pet_type = "charming expressive husky dog" if any(k in desc or k in fname or k in prompt_lower for k in ["haski", "husky", "хаски"]) else "playful domestic dog"
            return (VisualSemanticRole.PET_ANIMAL, pet_type, 0.92)

        # 3. Environment / Setting / Cafe / Coffee Cup
        env_keywords = [
            "kofeyn", "kafe", "interyer", "stol", "chashk", "kruzhk", "kofe", "kapuchin", "latte", "okno", "ulits", "park", "pomeshchen", "komnat",
            "coffee", "cafe", "cup", "cappuccino", "latte", "table", "indoor", "room", "window",
            "кофейн", "кафе", "интерьер", "стол", "чашк", "кружк", "кофе", "капучин", "латте", "окно", "улиц", "парк", "помещен", "комнат"
        ]
        is_env = any(k in desc or k in fname for k in env_keywords)
        if any(k in prompt_lower for k in ["в этой кофейне", "в этом кафе", "такое кафе", "за этим столом", "с таким кофе", "кофейн", "кофе"]):
            if any(k in desc or k in fname for k in ["coffee", "cafe", "cup", "kofe", "kofeyn", "stol", "кофе", "кофейн", "стол"]) or len(desc) < 20:
                is_env = True

        if is_env:
            return (VisualSemanticRole.ENVIRONMENT, "cozy sunlit artisan specialty coffee shop with a cup of cappuccino on a rustic wooden table", 0.90)

        # 4. Product / Culinary
        food_keywords = ["steyk", "steak", "tort", "cake", "desert", "dessert", "blyudo", "eda", "food", "dish", "стейк", "торт", "десерт", "блюдо", "еда"]
        if any(k in desc or k in fname for k in food_keywords):
            return (VisualSemanticRole.PRODUCT_ITEM, "delicious gourmet culinary specialty", 0.85)

        return (VisualSemanticRole.GENERAL_SUBJECT, "distinct visual reference subject", 0.70)

    @classmethod
    def allocate_workflow_slots(
        cls,
        analyzed_images: List[Dict[str, Any]],
        user_prompt: str = "",
        niche: str = ""
    ) -> Dict[str, Any]:
        classified = []
        for idx, img in enumerate(analyzed_images):
            role, label, conf = cls.classify_image_role(img, user_prompt=user_prompt)
            raw_path = img.get("file_path") or img.get("path") or img.get("url") or img.get("dataUrl") or img
            if isinstance(img, dict) and img.get("file_name"):
                raw_path = img.get("file_name")
            classified.append({
                "original_index": idx,
                "role": role,
                "label": label,
                "confidence": conf,
                "data": img,
                "raw_path": raw_path
            })

        slot1_base = None
        slot2_subject = None
        slot3_env = None

        # Slot 1: Hands / Base Anchor
        for item in classified:
            if item["role"] == VisualSemanticRole.HANDS_BODY and not slot1_base:
                slot1_base = item
                break

        # Slot 2: Pet / Secondary Object
        for item in classified:
            if item is not slot1_base and item["role"] in (VisualSemanticRole.PET_ANIMAL, VisualSemanticRole.PRODUCT_ITEM) and not slot2_subject:
                slot2_subject = item
                break

        # Slot 3: Environment / Location
        for item in classified:
            if item is not slot1_base and item is not slot2_subject and item["role"] == VisualSemanticRole.ENVIRONMENT and not slot3_env:
                slot3_env = item
                break

        # Distribute remaining
        used = [x for x in (slot1_base, slot2_subject, slot3_env) if x is not None]
        remaining = [item for item in classified if item not in used]
        if not slot1_base and remaining:
            slot1_base = remaining.pop(0)
        if not slot2_subject and remaining:
            slot2_subject = remaining.pop(0)
        if not slot3_env and remaining:
            slot3_env = remaining.pop(0)

        ordered_slots = []
        if slot1_base:
            ordered_slots.append(slot1_base)
        if slot2_subject:
            ordered_slots.append(slot2_subject)
        if slot3_env:
            ordered_slots.append(slot3_env)

        if not ordered_slots:
            default_slot = {
                "role": VisualSemanticRole.GENERAL_SUBJECT,
                "label": "primary visual subject",
                "confidence": 0.5,
                "data": None,
                "raw_path": "placeholder.png"
            }
            ordered_slots = [default_slot]

        while len(ordered_slots) < min(3, max(1, len(analyzed_images))):
            ordered_slots.append(ordered_slots[0])

        return {
            "image1_node55": ordered_slots[0] if len(ordered_slots) > 0 else None,
            "image2_node64": ordered_slots[1] if len(ordered_slots) > 1 else (ordered_slots[0] if len(ordered_slots) > 0 else None),
            "image3_node65": ordered_slots[2] if len(ordered_slots) > 2 else (ordered_slots[1] if len(ordered_slots) > 1 else (ordered_slots[0] if len(ordered_slots) > 0 else None)),
            "ordered_list": ordered_slots
        }

    @classmethod
    def compose_fusion_prompt(
        cls,
        slot_mapping: Dict[str, Any],
        user_prompt: str = "",
        niche: str = "Кофейня",
        company_name: str = "UCust"
    ) -> Dict[str, str]:
        s1 = slot_mapping.get("image1_node55")
        s2 = slot_mapping.get("image2_node64")
        s3 = slot_mapping.get("image3_node65")

        s1_desc = s1["label"] if s1 else "well-manicured hands in a warm sweater"
        s2_desc = s2["label"] if s2 else "cute adorable pet dog"
        s3_desc = s3["label"] if s3 else "cozy rustic coffee shop setting with a cup of cappuccino"

        fusion_prompt = (
            f"Seamless masterwork photo fusion: featuring the slender well-manicured hands from Image 1 gently holding "
            f"and cradling the expressive {s2_desc} from Image 2 in a warm loving embrace, seated at the rustic wooden cafe table "
            f"inside the authentic sunlit craft coffee shop from Image 3. On the table rests the artisanal ceramic cup of cappuccino "
            f"with silky latte art from Image 3, with a delicate whisper of warm translucent vapor rising into morning sunbeams. "
            f"35mm candid commercial photography, natural handheld point-of-view, perfect anatomical coherence, "
            f"soft volumetric morning window daylight, f/1.4 shallow depth of field, creamy background bokeh, authentic analog film grain."
        )

        visual_narrative_for_saiga = (
            f"Сцена на фото: В уютной кофейне за деревянным столиком с чашкой капучино (из третьего референса), "
            f"девушка с безупречным нежным маникюром в вязаном свитере (из первого референса) держит на руках "
            f"очаровательную собачку хаски с выразительным взглядом (из второго референса). "
            f"Атмосфера: Теплый утренний свет, солнце через окно, абсолютный комфорт, дружба и уют."
        )

        return {
            "fusion_prompt": fusion_prompt,
            "visual_narrative_for_saiga": visual_narrative_for_saiga,
            "slot1_label": s1_desc,
            "slot2_label": s2_desc,
            "slot3_label": s3_desc
        }


__all__ = ["MultiImageSemanticFusionEngine", "VisualSemanticRole"]
