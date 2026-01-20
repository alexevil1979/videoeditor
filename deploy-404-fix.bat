@echo off
chcp 65001 >nul
cd /d "%~dp0"
git add -A
git commit -m "Fix: Add FallbackResource to Apache config and .htaccess for 404 routing issue"
git push origin main
echo.
echo ========================================
echo Деплой завершен!
echo Исправления для 404 отправлены в Git
echo ========================================
pause
