@echo off
chcp 65001 > nul
echo ==================================================================
echo  🚀 Запуск Мок-Сервера UCust AI Gateway (CPU Mock Server)
echo ==================================================================
python start_mock.py --port 8000
pause
