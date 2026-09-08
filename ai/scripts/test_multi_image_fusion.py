# -*- coding: utf-8 -*-
import sys, os, asyncio

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from skills.multi_image_fusion import MultiImageSemanticFusionEngine, VisualSemanticRole
from core.orchestrator import UnifiedOrchestrator

async def main():
    print('Testing Multi-Image Fusion & Node Routing...')
    user_prompt = 'хочу что бы на таких руках у меня сидела такая собачка и мы пили кофе в этой кофейне'
    raw_attachments = [
        {'file_name': 'hands_manicure_sweater.png', 'description': 'slender manicured hands with nude almond nails in a soft cream knit sweater', 'path': 'hands_manicure_sweater.png'},
        {'file_name': 'husky_surprised_face.jpg', 'description': 'adorable husky dog with expressive wide blue eyes and smile', 'path': 'husky_surprised_face.jpg'},
        {'file_name': 'coffee_shop_table_cup.png', 'description': 'artisanal ceramic cup of cappuccino with latte art on rustic wooden table in cozy cafe', 'path': 'coffee_shop_table_cup.png'}
    ]
    slot_mapping = MultiImageSemanticFusionEngine.allocate_workflow_slots(raw_attachments, user_prompt=user_prompt, niche='Кофейня')
    fusion_res = MultiImageSemanticFusionEngine.compose_fusion_prompt(slot_mapping, user_prompt=user_prompt, niche='Кофейня', company_name='Maison Cafe')
    
    print('Slot 1 (Node 55):', slot_mapping['image1_node55']['raw_path'], '->', slot_mapping['image1_node55']['role'])
    print('Slot 2 (Node 64):', slot_mapping['image2_node64']['raw_path'], '->', slot_mapping['image2_node64']['role'])
    print('Slot 3 (Node 65):', slot_mapping['image3_node65']['raw_path'], '->', slot_mapping['image3_node65']['role'])
    
    assert slot_mapping['image1_node55']['role'] == VisualSemanticRole.HANDS_BODY
    assert slot_mapping['image2_node64']['role'] == VisualSemanticRole.PET_ANIMAL
    assert slot_mapping['image3_node65']['role'] == VisualSemanticRole.ENVIRONMENT
    print('Fusion prompt:', fusion_res['fusion_prompt'])
    assert 'Image 1' in fusion_res['fusion_prompt'] and 'Image 2' in fusion_res['fusion_prompt'] and 'Image 3' in fusion_res['fusion_prompt']

    orchestrator = UnifiedOrchestrator()
    res = await orchestrator.execute_task('generate_post', {
        'user_id': 'usr_fusion_test',
        'company_name': 'Maison Cafe',
        'niche': 'Кофейня',
        'city': 'Москва',
        'prompt': user_prompt,
        'attachments': raw_attachments,
        'generate_image': False,
        'comments_enabled': True
    })
    print('Post text:\n', res.get('post_text'))
    assert res.get('status') == 'success'
    print('All tests passed successfully!')

if __name__ == '__main__':
    asyncio.run(main())
