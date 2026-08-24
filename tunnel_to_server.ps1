# PowerShell SSH Tunnel Script for UCust
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🌐 UCUST REMOTE SERVER TUNNEL (SSH PORT FORWARDING)" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan

$serverIp = Read-Host "Введите IP адрес вашего сервера"
$serverUser = Read-Host "Введите пользователя сервера [по умолчанию: root]"
if ([string]::IsNullOrWhiteSpace($serverUser)) { $serverUser = "root" }

Write-Host ""
Write-Host "⏳ Устанавливаем защищенный SSH-туннель:" -ForegroundColor Green
Write-Host "   • Порт 3000 (Фронтенд Next.js)  -> http://localhost:3000" -ForegroundColor White
Write-Host "   • Порт 8000 (AI Gateway / API)  -> http://localhost:8000" -ForegroundColor White
Write-Host "   • Порт 8188 (ComfyUI / LTX-2)   -> http://localhost:8188" -ForegroundColor White
Write-Host ""
Write-Host "После ввода пароля окно туннеля должно оставаться открытым!" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan

ssh -N -L 3000:localhost:3000 -L 8000:localhost:8000 -L 8188:localhost:8188 "$serverUser@$serverIp"
