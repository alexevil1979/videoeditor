@echo off
chcp 65001 >nul
cd /d "%~dp0"
git add AI_CONTEXT.md
git add -A
git commit -m "Add: AI_CONTEXT.md with current project state and next steps"
git push origin main
echo.
echo ========================================
echo Деплой завершен!
echo AI_CONTEXT.md добавлен в репозиторий
echo ========================================
pause
