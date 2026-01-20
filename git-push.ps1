$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
git add -A
git commit -m "Fix PHP extensions requirements and update documentation"
git push origin main
Write-Host "Done!"
