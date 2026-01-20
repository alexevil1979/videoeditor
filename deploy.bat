@echo off
chcp 65001 >nul
cd /d "%~dp0"
git add -A
git commit -m "Auto-deploy: %date% %time%"
git push origin main
echo.
echo ========================================
echo Деплой завершен!
echo ========================================
pause
