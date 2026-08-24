@echo off
chcp 65001 > nul
title UCust Remote Tunnel (vm-8720)

echo ======================================================================
echo 🌐 UCUST REMOTE SERVER TUNNEL (SSH PORT FORWARDING)
echo    Сервер: vm-8720.user-project-3970.cloud.intcld.ru (194.67.95.164)
echo ======================================================================
echo.
echo ⏳ Устанавливаем защищенный SSH-туннель:
echo    • Порт 3000 (Фронтенд Next.js)  -^> http://localhost:3000
echo    • Порт 8000 (AI Gateway / API)  -^> http://localhost:8000
echo    • Порт 8188 (ComfyUI / LTX-2)   -^> http://localhost:8188
echo.
echo Введите пароль от сервера root@194.67.95.164 при запросе.
echo (Окно консоли должно оставаться открытым во время работы)
echo ======================================================================
echo.

ssh -N -L 3000:localhost:3000 -L 8000:localhost:8000 -L 8188:localhost:8188 root@194.67.95.164

echo.
echo ❌ Туннель закрыт.
pause
