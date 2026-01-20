@echo off
chcp 65001 >nul
cd /d "%~dp0"
git add -A
git commit -m "Fix PHP extensions requirements and update documentation"
git push origin main
pause
