# PowerShell SSH Tunnel Script for UCust vm-8720.user-project-3970.cloud.intcld.ru (194.67.95.119)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🌐 UCUST REMOTE SERVER TUNNEL (vm-8720.user-project-3970.cloud.intcld.ru)" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "⏳ Устанавливаем защищенный SSH-туннель:" -ForegroundColor Green
Write-Host "   • Порт 3000 (Фронтенд Next.js)  -> http://localhost:3000" -ForegroundColor White
Write-Host "   • Порт 8000 (AI Gateway / API)  -> http://localhost:8000" -ForegroundColor White
Write-Host "   • Порт 8188 (ComfyUI / LTX-2)   -> http://localhost:8188" -ForegroundColor White
Write-Host "   • Порт 6379 (Redis Cache)       -> 127.0.0.1:6379" -ForegroundColor White
Write-Host ""
Write-Host "Введите пароль от root@vm-8720.user-project-3970.cloud.intcld.ru при запросе." -ForegroundColor Yellow
Write-Host "(Окно консоли должно оставаться открытым во время работы)" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan

ssh -o ServerAliveInterval=30 -o ServerAliveCountMax=5 -o StrictHostKeyChecking=accept-new -N -L 3000:127.0.0.1:3000 -L 8000:127.0.0.1:8000 -L 8188:127.0.0.1:8188 -L 6379:127.0.0.1:6379 root@vm-8720.user-project-3970.cloud.intcld.ru
