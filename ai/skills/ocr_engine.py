"""
Universal OCR Engine for UCust AI Ecosystem.
Supports PaddleOCR (primary on GPU/CPU), EasyOCR, and RapidOCR for multilingual (Russian & English) text extraction.
"""

from __future__ import annotations
import io
import os
import logging
import threading
from typing import Any, List, Optional, Union
from PIL import Image

logger = logging.getLogger("ocr_engine")

class OCREngine:
    """
    Потокобезопасный Singleton OCR-модуль для быстрого извлечения русского и английского текста с изображений.
    """
    _instance = None
    _lock = threading.Lock()
    _backend_name: Optional[str] = None
    _engine = None

    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        self._init_backend()

    def _init_backend(self):
        with OCREngine._lock:
            if OCREngine._engine is not None:
                return

            # 1. Попытка инициализации официального PaddleOCR
            try:
                from paddleocr import PaddleOCR
                use_gpu_flag = bool(self.use_gpu and os.getenv("DISABLE_OCR_GPU", "").lower() not in ["1", "true"])
                OCREngine._engine = PaddleOCR(use_angle_cls=True, lang='ru', use_gpu=use_gpu_flag, show_log=False)
                OCREngine._backend_name = "PaddleOCR"
                logger.info("[OCREngine] 🚀 Активирован PaddleOCR (Языки: ru, en)")
                return
            except Exception:
                pass

            # 2. Попытка инициализации EasyOCR
            try:
                import easyocr
                use_gpu_flag = bool(self.use_gpu and os.getenv("DISABLE_OCR_GPU", "").lower() not in ["1", "true"])
                OCREngine._engine = easyocr.Reader(['ru', 'en'], gpu=use_gpu_flag, verbose=False)
                OCREngine._backend_name = "EasyOCR"
                logger.info("[OCREngine] 🚀 Активирован EasyOCR (Языки: ru, en)")
                return
            except Exception:
                pass

            # 3. Попытка инициализации RapidOCR (ONNX)
            try:
                from rapidocr_onnxruntime import RapidOCR
                OCREngine._engine = RapidOCR()
                OCREngine._backend_name = "RapidOCR"
                logger.info("[OCREngine] 🚀 Активирован RapidOCR (ONNX)")
                return
            except Exception:
                pass

            logger.warning("[OCREngine] ⚠️ Ни один OCR-движок не установлен. OCR будет отключен.")

    def extract_text(self, image_input: Union[str, bytes, Image.Image]) -> str:
        """
        Извлекает распознанный текст со снимка единой строкой с фильтрацией мусора.
        """
        if OCREngine._engine is None:
            return ""

        try:
            # 1. PaddleOCR
            if OCREngine._backend_name == "PaddleOCR":
                import numpy as np
                if isinstance(image_input, Image.Image):
                    img_np = np.array(image_input.convert('RGB'))
                elif isinstance(image_input, bytes):
                    img_np = np.array(Image.open(io.BytesIO(image_input)).convert('RGB'))
                elif isinstance(image_input, str) and os.path.exists(image_input):
                    img_np = np.array(Image.open(image_input).convert('RGB'))
                else:
                    return ""

                result = OCREngine._engine.ocr(img_np, cls=True)
                if not result or not result[0]:
                    return ""
                lines = [line[1][0].strip() for line in result[0] if line[1][1] > 0.45]
                return " ".join(lines).strip()

            # 2. EasyOCR
            elif OCREngine._backend_name == "EasyOCR":
                import numpy as np
                if isinstance(image_input, Image.Image):
                    img_np = np.array(image_input.convert('RGB'))
                elif isinstance(image_input, bytes):
                    img_np = np.array(Image.open(io.BytesIO(image_input)).convert('RGB'))
                elif isinstance(image_input, str) and os.path.exists(image_input):
                    img_np = np.array(Image.open(image_input).convert('RGB'))
                else:
                    return ""

                result = OCREngine._engine.readtext(img_np)
                lines = [text.strip() for bbox, text, score in result if score > 0.35 and len(text.strip()) > 1]
                return " ".join(lines).strip()

            # 3. RapidOCR
            elif OCREngine._backend_name == "RapidOCR":
                import numpy as np
                if isinstance(image_input, Image.Image):
                    img_np = np.array(image_input.convert('RGB'))
                elif isinstance(image_input, bytes):
                    img_np = np.array(Image.open(io.BytesIO(image_input)).convert('RGB'))
                elif isinstance(image_input, str) and os.path.exists(image_input):
                    img_np = image_input
                else:
                    return ""

                result, _ = OCREngine._engine(img_np)
                if not result:
                    return ""
                lines = [line[1].strip() for line in result if float(line[2]) > 0.4]
                return " ".join(lines).strip()

        except Exception as e:
            logger.warning(f"[OCREngine] Ошибка распознавания текста: {e}")
            return ""

        return ""
