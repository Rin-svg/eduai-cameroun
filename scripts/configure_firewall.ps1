# =====================================================
# EDUAI Cameroun — Configuration Pare-feu Windows Defender
# À exécuter en tant qu'Administrateur sur le PC Serveur
# =====================================================

Write-Host "=== Configuration Pare-feu EDUAI Cameroun ===" -ForegroundColor Green

# Autoriser le port 80 (HTTP) en entrée pour XAMPP/Django
Write-Host "Ouverture du port 80 (HTTP)..."
New-NetFirewallRule -DisplayName "EDUAI-HTTP-80" `
    -Direction Inbound -Action Allow `
    -Protocol TCP -LocalPort 80 `
    -Description "EDUAI Cameroun — Accès HTTP Application Web" `
    -ErrorAction SilentlyContinue

# Port 8000 Django (mode développement)
Write-Host "Ouverture du port 8000 (Django dev)..."
New-NetFirewallRule -DisplayName "EDUAI-Django-8000" `
    -Direction Inbound -Action Allow `
    -Protocol TCP -LocalPort 8000 `
    -Description "EDUAI Cameroun — Django Development Server" `
    -ErrorAction SilentlyContinue

# Port 3306 MySQL (accès local uniquement)
Write-Host "MySQL 3306 — accès local uniquement..."
New-NetFirewallRule -DisplayName "EDUAI-MySQL-3306-Local" `
    -Direction Inbound -Action Allow `
    -Protocol TCP -LocalPort 3306 `
    -RemoteAddress LocalSubnet `
    -Description "EDUAI Cameroun — MySQL Local Only" `
    -ErrorAction SilentlyContinue

# Bloquer MySQL depuis l'extérieur
New-NetFirewallRule -DisplayName "EDUAI-MySQL-Block-External" `
    -Direction Inbound -Action Block `
    -Protocol TCP -LocalPort 3306 `
    -Description "EDUAI Cameroun — MySQL blocked from external" `
    -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✅ Configuration pare-feu terminée !" -ForegroundColor Green
Write-Host "   Port 80  : AUTORISÉ (application web)"
Write-Host "   Port 8000: AUTORISÉ (Django dev)"
Write-Host "   Port 3306: LOCAL UNIQUEMENT (MySQL)"
Write-Host ""

# Afficher les règles EDUAI créées
Write-Host "Règles EDUAI actives :" -ForegroundColor Yellow
Get-NetFirewallRule | Where-Object { $_.DisplayName -like "EDUAI*" } | `
    Select-Object DisplayName, Direction, Action, Enabled | Format-Table -AutoSize
