@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo Деплой исправлений на сервер
echo ========================================
echo.
echo Отправка изменений в Git...
git add -A
git commit -m "Fix: Remove FallbackResource, fix layout.php paths, remove DirectoryMatch, add create-admin script"
git push origin main
echo.
echo ========================================
echo Деплой завершен!
echo ========================================
echo.
echo Следующие шаги на сервере:
echo 1. cd /ssd/www/videoeditor
echo 2. git pull origin main
echo 3. sudo nano /etc/apache2/sites-available/videoeditor.conf
echo    (убедиться что FallbackResource отсутствует)
echo 4. sudo apache2ctl configtest
echo 5. sudo systemctl restart apache2
echo 6. php scripts/create-admin.php
echo.
pause
