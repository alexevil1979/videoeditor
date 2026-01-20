# PowerShell script for deploying fixes to server
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploying fixes to server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Pushing changes to Git..." -ForegroundColor Yellow

# Add all changes
git add -A

# Create commit
git commit -m "Fix: Remove FallbackResource, fix layout.php paths, remove DirectoryMatch, add create-admin script"

# Push to repository
git push origin main

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deploy completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps on server:" -ForegroundColor Yellow
Write-Host "1. cd /ssd/www/videoeditor"
Write-Host "2. git pull origin main"
Write-Host "3. sudo nano /etc/apache2/sites-available/videoeditor.conf"
Write-Host "   (verify that FallbackResource is absent)"
Write-Host "4. sudo apache2ctl configtest"
Write-Host "5. sudo systemctl restart apache2"
Write-Host "6. php scripts/create-admin.php"
Write-Host ""
