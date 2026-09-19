# PowerShell Direct Upload Script to AI Server 185.182.108.124
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🚀 ПРЯМАЯ ЗАГРУЗКА AI-ФАЙЛОВ НА AI-СЕРВЕР (БЕЗ GIT)" -ForegroundColor Yellow
Write-Host "🌐 Сервер: root@185.182.108.124:/opt/ucust/ai" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$server = "root@185.182.108.124"
$remotePath = "/opt/ucust/ai"

Write-Host "⏳ Копирование модулей skills, scripts, publishers, core, bridge, collectors, rag..." -ForegroundColor Green
scp -r "ai/skills" "ai/scripts" "ai/publishers" "ai/core" "ai/bridge" "ai/collectors" "ai/rag" "ai/realism2.0.json" "ai/Photo_generations.json" "${server}:${remotePath}/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ ВСЕ ФАЙЛЫ УСПЕШНО ЗАГРУЖЕНЫ НА AI-СЕРВЕР (185.182.108.124)!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️ Ошибка при копировании файлов. Проверьте SSH-подключение к 185.182.108.124." -ForegroundColor Red
}
