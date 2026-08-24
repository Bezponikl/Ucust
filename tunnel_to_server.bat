@echo off
chcp 65001 > nul
title UCust Remote Tunnel (194.67.95.119)

echo ======================================================================
echo 🌐 UCUST REMOTE SERVER TUNNEL (SSH PORT FORWARDING)
echo    Сервер: 194.67.95.119
echo ======================================================================
echo.
echo ⏳ Устанавливаем защищенный SSH-туннель:
echo    • Порт 3000 (Фронтенд Next.js)  -^> http://localhost:3000
echo    • Порт 8000 (AI Gateway / API)  -^> http://localhost:8000
echo    • Порт 8188 (ComfyUI / LTX-2)   -^> http://localhost:8188
echo    • Порт 6379 (Redis Cache)       -^> 127.0.0.1:6379
echo.
echo Введите пароль от root@194.67.95.119 при запросе.
echo (Окно консоли должно оставаться открытым во время работы)
echo ======================================================================
echo.

ssh -o ServerAliveInterval=30 -o ServerAliveCountMax=5 -o StrictHostKeyChecking=accept-new -N -L 3000:127.0.0.1:3000 -L 8000:127.0.0.1:8000 -L 8188:127.0.0.1:8188 -L 6379:127.0.0.1:6379 root@194.67.95.119

echo.
echo ❌ Туннель закрыт.
pause
