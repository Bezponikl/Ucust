import os
import subprocess
import json
from collections import Counter
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class MediaUtils:
    """
    Утилиты для обработки медиа (CPU bound).
    Работа с цветами, нарезка и склейка видео (через ffmpeg).
    """

    @staticmethod
    def extract_dominant_colors(image_path: str, num_colors: int = 3) -> list:
        """
        Извлекает доминирующие HEX цвета из картинки. Используется для создания ИИ-брендбука.
        """
        if not PIL_AVAILABLE:
            print("[MediaUtils] ⚠️ PIL не установлен. Возвращаем дефолтные цвета.")
            return ["#000000", "#FFFFFF", "#1A2B3C"]
            
        try:
            image = Image.open(image_path).convert("RGB")
            # Уменьшаем картинку для скорости анализа
            image = image.resize((100, 100))
            pixels = list(image.getdata())
            # Считаем самые частые цвета
            most_common = Counter(pixels).most_common(num_colors)
            
            hex_colors = []
            for (r, g, b), count in most_common:
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                hex_colors.append(hex_color)
                
            return hex_colors
        except Exception as e:
            print(f"[MediaUtils] ⚠️ Ошибка извлечения цветов: {e}")
            return ["#FFFFFF"]

    @staticmethod
    def extract_frame_for_qa(video_path: str, output_image_path: str, time_sec: str = "00:00:01"):
        """
        Извлекает 1 кадр из видео с помощью ffmpeg для проверки Мундримом.
        """
        cmd = [
            "ffmpeg", "-y", "-i", video_path, 
            "-ss", time_sec, 
            "-vframes", "1", 
            output_image_path
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except Exception as e:
            print(f"[MediaUtils] ⚠️ Ошибка ffmpeg при извлечении кадра: {e}")
            return False

    @staticmethod
    def stitch_videos_cpu(video_paths: list, output_path: str):
        """
        Склеивает несколько видео-чанков в один финальный файл.
        """
        if not video_paths:
            return False
            
        list_file = "temp_stitch_list.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for vp in video_paths:
                f.write(f"file '{os.path.abspath(vp)}'\n")
                
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", 
            "-i", list_file, 
            "-c", "copy", 
            output_path
        ]
        
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            os.remove(list_file)
            print(f"[MediaUtils] 🎞️ Склейка завершена: {output_path}")
            return True
        except Exception as e:
            print(f"[MediaUtils] ⚠️ Ошибка ffmpeg при склейке: {e}")
            return False
