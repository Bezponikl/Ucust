@echo off
chcp 65001 > nul
title UCust Remote Tunnel (Port Forwarding)

echo ======================================================================
echo 🌐 UCUST REMOTE SERVER TUNNEL (SSH PORT FORWARDING)
echo ======================================================================
echo.

set /p SERVER_IP="Введите IP адрес вашего сервера (например, 194.67.95.7): "
set /p SERVER_USER="Введите пользователя сервера [по умолчанию: root]: "

if "%SERVER_USER%"=="" set SERVER_USER=root

echo.
echo ⏳ Устанавливаем защищенный SSH-туннель:
echo    • Порт 3000 (Фронтенд Next.js)  -^> http://localhost:3000
echo    • Порт 8000 (AI Gateway / API)  -^> http://localhost:8000
echo    • Порт 8188 (ComfyUI / LTX-2)   -^> http://localhost:8188
echo.
echo После ввода пароля окно туннеля должно оставаться открытым!
echo ======================================================================
echo.

ssh -N -L 3000:localhost:3000 -L 8000:localhost:8000 -L 8188:localhost:8188 %SERVER_USER%@%SERVER_IP%

echo.
echo ❌ Туннель закрыт.
pause
