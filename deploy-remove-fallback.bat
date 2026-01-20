@echo off
chcp 65001 >nul
cd /d "%~dp0"
git add -A
git commit -m "Fix: Remove FallbackResource from Apache config (causes 500 error), use mod_rewrite only"
git push origin main
echo.
echo ========================================
echo Деплой завершен!
echo Уберите FallbackResource из конфигурации Apache на сервере
echo ========================================
pause
