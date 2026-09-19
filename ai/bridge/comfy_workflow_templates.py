"""
File: ai/bridge/comfy_workflow_templates.py
Базовый API-граф для ComfyUI (Формат Prompt API).
"""

from __future__ import annotations

import copy
import os
import random
from typing import Dict, Any, Optional

BASE_SDXL_API_JSON = {
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "seed": 0,
            "steps": 30,
            "cfg": 7.0,
            "sampler_name": "dpmpp_2m",
            "scheduler": "karras",
            "denoise": 1.0,
            "model": ["4", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0]
        }
    },
    "4": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {
            "ckpt_name": "sd_xl_base_1.0.safetensors"
        }
    },
    "5": {
        "class_type": "EmptyLatentImage",
        "inputs": {
            "batch_size": 1,
            "width": 1024,
            "height": 1024
        }
    },
    "6": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "",
            "clip": ["4", 1]
        }
    },
    "7": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "ugly, deformed, bad anatomy, bad hands, blurry, low quality, cgi, 3d render, plastic",
            "clip": ["4", 1]
        }
    },
    "8": {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": ["3", 0],
            "vae": ["4", 2]
        }
    },
    "9": {
        "class_type": "SaveImage",
        "inputs": {
            "filename_prefix": "ucust_render",
            "images": ["8", 0]
        }
    }
}


class WorkflowBuilder:
    @classmethod
    def build_payload(
        cls,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        seed: Optional[int] = None,
        steps: int = 30,
        cfg: float = 7.0,
        ckpt_name: Optional[str] = None,
        filename_prefix: str = "ucust_render"
    ) -> Dict[str, Any]:
        """Инжектит параметры генерации в эталонный Prompt API граф."""
        workflow = copy.deepcopy(BASE_SDXL_API_JSON)
        
        # 1. Чекпоинт
        active_ckpt = ckpt_name or os.getenv("COMFYUI_CHECKPOINT_NAME", "sd_xl_base_1.0.safetensors")
        workflow["4"]["inputs"]["ckpt_name"] = active_ckpt
        
        # 2. Разрешение кадра
        workflow["5"]["inputs"]["width"] = width
        workflow["5"]["inputs"]["height"] = height
        
        # 3. Промпты
        workflow["6"]["inputs"]["text"] = prompt
        if negative_prompt:
            workflow["7"]["inputs"]["text"] = negative_prompt
            
        # 4. Сэмплер
        workflow["3"]["inputs"]["seed"] = seed if seed is not None else random.randint(100000, 999999999999)
        workflow["3"]["inputs"]["steps"] = steps
        workflow["3"]["inputs"]["cfg"] = cfg
        
        # 5. Префикс сохранения
        workflow["9"]["inputs"]["filename_prefix"] = filename_prefix
        
        return workflow
