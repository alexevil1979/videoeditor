@echo off
chcp 65001 >nul
cd /d "%~dp0"
git add -A
git commit -m "Fix: Correct layout.php path in auth views and remove DirectoryMatch from .htaccess"
git push origin main
echo.
echo ========================================
echo Деплой завершен!
echo Исправления отправлены в Git
echo ========================================
pause
