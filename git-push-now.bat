@echo off
chcp 65001 >nul
cd /d "%~dp0"
git add -A
git commit -m "Add: Enhanced debugging and logging for routing issues"
git push origin main
echo.
echo ========================================
echo Деплой завершен! Теперь на сервере:
echo git pull origin main
echo ========================================
pause
