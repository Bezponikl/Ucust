@echo off
setlocal
cd /d "%~dp0"
echo ======================================================================
echo [UCUST] UPLOADING AI CODE DIRECTLY TO AI SERVER (185.182.108.124)
echo ======================================================================

echo Copying modules: skills, scripts, publishers, core, bridge, collectors, rag...
scp -r "ai/skills" "ai/scripts" "ai/publishers" "ai/core" "ai/bridge" "ai/collectors" "ai/rag" "ai/realism2.0.json" "ai/Photo_generations.json" root@185.182.108.124:/opt/ucust/ai/

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================================
    echo [SUCCESS] ALL FILES UPLOADED TO AI SERVER (185.182.108.124) DIRECTLY!
    echo ======================================================================
) else (
    echo.
    echo [ERROR] Upload failed. Please check SSH connection to 185.182.108.124.
)
echo.
pause
