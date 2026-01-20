@echo off
chcp 65001 >nul
cd /d "%~dp0"
git add -A
git commit -m "Fix: Remove FallbackResource, fix layout.php paths, remove DirectoryMatch from .htaccess, add create-admin script, update AI_CONTEXT"
git push origin main
echo.
echo ========================================
echo Деплой завершен!
echo Все исправления отправлены в Git
echo ========================================
echo.
echo Следующие шаги на сервере:
echo 1. git pull origin main
echo 2. Убрать FallbackResource из Apache конфигурации
echo 3. php scripts/create-admin.php
echo ========================================
pause
