import os

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

class ResourceManager:
    """
    Менеджер распределения ресурсов системы (CPU / GPU).
    Гарантирует, что парсеры работают только на процессоре,
    а ИИ-модели используют видеокарту и имеют высокий приоритет.
    """
    
    @staticmethod
    def enforce_cpu_for_parsers():
        """
        Устанавливает низкий приоритет для текущего процесса (парсера)
        и запрещает ему использовать GPU (прячет CUDA-устройства).
        """
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        
        if not PSUTIL_AVAILABLE:
            print("[ResourceManager] ⚠️ psutil не установлен. Управление приоритетами отключено.")
            return

        try:
            p = psutil.Process(os.getpid())
            if os.name == 'nt':
                p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            else:
                p.nice(10)
            print(f"[ResourceManager] ⚙️ Ресурсы для Парсера ограничены (Только CPU, Низкий приоритет).")
        except Exception as e:
            print(f"[ResourceManager] ⚠️ Не удалось изменить приоритет CPU: {e}")

    @staticmethod
    def enforce_gpu_priority_for_ai():
        """
        Восстанавливает видимость GPU и задает высокий приоритет процессу ОС.
        """
        os.environ.pop("CUDA_VISIBLE_DEVICES", None)
        
        if not PSUTIL_AVAILABLE:
            return
            
        try:
            p = psutil.Process(os.getpid())
            if os.name == 'nt':
                p.nice(psutil.HIGH_PRIORITY_CLASS)
            else:
                p.nice(-10)
            
            if TORCH_AVAILABLE and torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                print(f"[ResourceManager] 🚀 Выделен GPU: {gpu_name}. Приоритет ИИ-агента ПОВЫШЕН!")
            else:
                print(f"[ResourceManager] ⚠️ CUDA недоступна (или torch не установлен), но приоритет ИИ-агента ПОВЫШЕН на CPU.")
        except Exception as e:
            print(f"[ResourceManager] ⚠️ Не удалось изменить приоритет GPU: {e}")
            
    @staticmethod
    def get_llamacpp_kwargs() -> dict:
        return {
            "n_gpu_layers": -1,
            "n_threads": max(1, os.cpu_count() - 1),
            "use_mmap": True,
            "use_mlock": False
        }
