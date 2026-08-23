"""
start_all.py
Единый лаунчер для всех компонентов UCust.AI.
Запускает:
 1. Ядро Octopoda (API + Dashboard)
 2. Агентов UCust.AI (Heartbeat)
 3. Smart Proxy (Авто-авторизация)

Используйте Ctrl+C для корректного завершения всех процессов.
"""
import os
import sys
import time
import subprocess
import webbrowser
import threading
import signal

# Цвета для вывода в консоль
COLORS = {
    "OCTOPODA": "\033[96m", # Cyan
    "AGENTS": "\033[92m",   # Green
    "PROXY": "\033[93m",    # Yellow
    "SYSTEM": "\033[95m",   # Magenta
    "RESET": "\033[0m"
}

def print_sys(msg):
    print(f"{COLORS['SYSTEM']}[SYSTEM] {msg}{COLORS['RESET']}", flush=True)

def stream_output(pipe, prefix, color_key):
    """Считывает вывод процесса и добавляет к нему цветной префикс"""
    color = COLORS.get(color_key, "")
    reset = COLORS["RESET"]
    try:
        for line in iter(pipe.readline, b''):
            decoded_line = line.decode("utf-8", errors="replace").rstrip('\r\n')
            print(f"{color}[{prefix}]{reset} {decoded_line}", flush=True)
    except Exception:
        pass

def main():
    # Настраиваем переменные окружения, общие для всех
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["OCTOPODA_API_KEY"] = "local-dev"
    env["OCTOPODA_BASE_URL"] = "http://localhost:8741"
    env["OCTOPODA_MODE"] = "auto"
    
    # Возвращаем Postgres из Docker для полной поддержки Атласа
    env["DATABASE_URL"] = "postgresql://postgres:postgres@127.0.0.1:5432/ai_smm"
    env["SYNRIX_BACKEND"] = "postgres"
    if "OCTOPODA_DB_PATH" in env:
        del env["OCTOPODA_DB_PATH"]
    
    python_exe = sys.executable

    print_sys("Инициализация сервисов UCust.AI...")
    processes = []

    try:
        # 1. Запуск ядра Octopoda
        print_sys("Запускаем Octopoda Server (API: 8741, Flask: 7842)...")
        p_core = subprocess.Popen(
            [python_exe, "-m", "synrix_runtime.start"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1
        )
        processes.append(("OCTOPODA", p_core))
        threading.Thread(target=stream_output, args=(p_core.stdout, "OCTOPODA", "OCTOPODA"), daemon=True).start()
        
        # Ждем запуска ядра
        time.sleep(5)

        # 2. Запуск агентов
        print_sys("Запускаем UCust.AI Agents (Heartbeat)...")
        p_agents = subprocess.Popen(
            [python_exe, "infrastructure/run_agents.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1
        )
        processes.append(("AGENTS", p_agents))
        threading.Thread(target=stream_output, args=(p_agents.stdout, "AGENTS", "AGENTS"), daemon=True).start()

        # Ждем запуска агентов
        time.sleep(3)

        # 3. Запуск прокси
        print_sys("Запускаем Smart Proxy (порт 7843)...")
        p_proxy = subprocess.Popen(
            [python_exe, "infrastructure/proxy_dashboard.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1
        )
        processes.append(("PROXY", p_proxy))
        threading.Thread(target=stream_output, args=(p_proxy.stdout, "PROXY", "PROXY"), daemon=True).start()

        time.sleep(2)
        
        url = "http://localhost:7843/dashboard/agents"
        print_sys(f"Все сервисы запущены! Открываю дашборд: {url}")
        webbrowser.open(url)

        print_sys("Нажмите Ctrl+C в этом окне для остановки всех сервисов.")
        
        # Бесконечный цикл, ждем остановки
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print_sys("\nПолучен сигнал остановки (Ctrl+C).")
    finally:
        print_sys("Завершаем фоновые процессы...")
        for name, p in processes:
            if p.poll() is None:  # Если процесс еще работает
                print_sys(f"Останавливаем {name}...")
                p.terminate()
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    p.kill()
        print_sys("Все сервисы остановлены.")

if __name__ == "__main__":
    main()
