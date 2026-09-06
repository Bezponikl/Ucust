"""
Setup ComfyUI Custom Nodes — Автоматический установщик кастомных нод для ComfyUI и LTX-2.3.
Скачивает и настраивает все необходимые репозитории в папку ComfyUI/custom_nodes/.
"""

import os
import sys
import subprocess
import shutil
from typing import List, Dict

# Список необходимых кастомных нод для LTX-Video, SMM-генерации и работы воркфлоу
REQUIRED_CUSTOM_NODES: List[Dict[str, str]] = [
    {
        "name": "ComfyUI-Manager",
        "url": "https://github.com/ltdrdata/ComfyUI-Manager.git",
        "desc": "Главный менеджер нод и авто-резолвер зависимостей"
    },
    {
        "name": "ComfyUI-LTXVideo",
        "url": "https://github.com/Lightricks/ComfyUI-LTXVideo.git",
        "desc": "Официальные ноды Lightricks LTX-Video (2.3 / 22B)"
    },
    {
        "name": "ComfyUI-VideoHelperSuite",
        "url": "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git",
        "desc": "Ноды Video Combine, слияние аудио и видео дорожек (VHS)"
    },
    {
        "name": "ComfyUI-GGUF",
        "url": "https://github.com/city96/ComfyUI-GGUF.git",
        "desc": "Поддержка квантованных GGUF текстовых моделей и клипов"
    },
    {
        "name": "ComfyUI_essentials",
        "url": "https://github.com/cubiq/ComfyUI_essentials.git",
        "desc": "Базовые утилиты ресайза (ResizeImageMaskNode, ImageCrop)"
    },
    {
        "name": "ComfyUI-Custom-Scripts",
        "url": "https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git",
        "desc": "Вспомогательные скрипты и ноды авто-сохранения"
    },
    {
        "name": "comfyui_controlnet_aux",
        "url": "https://github.com/Fannovel16/comfyui_controlnet_aux.git",
        "desc": "Препроцессоры глубины и поз для брендбуков (Depth Anything v2, DWPose, MeshGraphormer)"
    },
    {
        "name": "ComfyUI-Impact-Pack",
        "url": "https://github.com/ltdrdata/ComfyUI-Impact-Pack.git",
        "desc": "FaceDetailer и HandDetailer для локального восстановления анатомии"
    }
]


def find_comfyui_path() -> str:
    """Ищет путь к директории ComfyUI."""
    env_path = os.getenv("COMFYUI_PATH")
    if env_path and os.path.exists(env_path):
        return os.path.abspath(env_path)

    # Проверяем типовые расположения
    current_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.normpath(os.path.join(current_dir, "..", "..", "ComfyUI")),
        os.path.normpath(os.path.join(current_dir, "..", "ComfyUI")),
        "/opt/ucust/ComfyUI",
        "/opt/ComfyUI",
        os.path.expanduser("~/ComfyUI"),
        "ComfyUI"
    ]
    for c in candidates:
        if os.path.exists(c) and os.path.isdir(c):
            return os.path.abspath(c)

    # Если не найдено, создаем рядом с репозиторием
    fallback = os.path.normpath(os.path.join(current_dir, "..", "..", "ComfyUI"))
    return fallback


def install_comfyui_nodes(comfyui_dir: str = None, install_requirements: bool = True):
    """
    Автоматически клонирует отсутствующие ноды и устанавливает их зависимости.
    """
    if not comfyui_dir:
        comfyui_dir = find_comfyui_path()

    custom_nodes_dir = os.path.join(comfyui_dir, "custom_nodes")
    os.makedirs(custom_nodes_dir, exist_ok=True)

    print(f"\n=======================================================")
    print(f"📦 АВТОМАТИЧЕСКАЯ УСТАНОВКА КАСТОМНЫХ НОД COMFYUI")
    print(f"📁 Папка нод: {custom_nodes_dir}")
    print(f"=======================================================\n")

    for node in REQUIRED_CUSTOM_NODES:
        name = node["name"]
        url = node["url"]
        desc = node["desc"]
        node_path = os.path.join(custom_nodes_dir, name)

        if os.path.exists(node_path):
            print(f"✅ [{name}] уже установлена ({desc})")
        else:
            print(f"⏳ [{name}] Клонирование из {url}...")
            try:
                cmd = ["git", "clone", "--depth", "1", url, node_path]
                subprocess.run(cmd, check=True)
                print(f"   🎉 Успешно склонировано: {name}")
            except Exception as e:
                print(f"   ❌ Ошибка при клонировании {name}: {e}")
                continue

        # Установка зависимостей ноды
        req_file = os.path.join(node_path, "requirements.txt")
        if install_requirements and os.path.exists(req_file):
            print(f"   ⚙️ Установка зависимостей для {name}...")
            try:
                cmd = [sys.executable, "-m", "pip", "install", "-q", "-r", req_file]
                subprocess.run(cmd, check=True)
                print(f"   ✅ Зависимости для {name} успешно установлены.")
            except Exception as e:
                print(f"   ⚠️ Ошибка pip install для {name}: {e}")

    # Загрузка весов YOLOv8 детекторов (Face & Hand Detailers)
    bbox_models_dir = os.path.join(comfyui_dir, "models", "ultralytics", "bbox")
    os.makedirs(bbox_models_dir, exist_ok=True)
    models_to_download = [
        ("face_yolov8m.pt", "https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov8m.pt"),
        ("hand_yolov8n.pt", "https://huggingface.co/Bingsu/adetailer/resolve/main/hand_yolov8n.pt"),
        ("hand_yolov8s.pt", "https://huggingface.co/Bingsu/adetailer/resolve/main/hand_yolov8s.pt")
    ]
    for mname, murl in models_to_download:
        mpath = os.path.join(bbox_models_dir, mname)
        if not os.path.exists(mpath):
            print(f"⏳ Скачивание детектора {mname} в {bbox_models_dir}...")
            try:
                import urllib.request
                urllib.request.urlretrieve(murl, mpath)
                print(f"   ✅ Детектор {mname} успешно загружен.")
            except Exception as dl_e:
                print(f"   ⚠️ Ошибка скачивания {mname}: {dl_e}")
        else:
            print(f"✅ Детектор [{mname}] готов к работе.")

    print(f"\n✨ Все необходимые ноды и детекторы Impact Pack (Face/Hand) проверены и готовы к работе!\n")


if __name__ == "__main__":
    target_path = sys.argv[1] if len(sys.argv) > 1 else None
    install_comfyui_nodes(target_path)
