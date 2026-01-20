@echo off
chcp 65001 >nul
cd /d "%~dp0"
git add -A
git commit -m "Fix: Add FallbackResource to Apache config for 404 routing fix"
git push origin main
echo.
echo ========================================
echo Деплой завершен!
echo Обновите конфигурацию Apache на сервере
echo ========================================
pause
