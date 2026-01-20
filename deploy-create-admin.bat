@echo off
chcp 65001 >nul
cd /d "%~dp0"
git add -A
git commit -m "Add: Script to create admin user and login credentials documentation"
git push origin main
echo.
echo ========================================
echo Деплой завершен!
echo На сервере выполните: php scripts/create-admin.php
echo ========================================
pause
