# =====================================================
# EDUAI Cameroun — Configuration Pare-feu Windows Defender
# LANCER EN TANT QU'ADMINISTRATEUR
#
# Clic droit sur PowerShell → "Exécuter en tant qu'administrateur"
# Puis : powershell -ExecutionPolicy Bypass -File configure_firewall.ps1
# =====================================================

Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "   EDUAI Cameroun - Configuration Pare-feu       " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# --- Supprimer les anciennes règles EDUAI pour repartir propre ---
Write-Host "[1/5] Nettoyage des anciennes règles EDUAI..." -ForegroundColor Yellow
Get-NetFirewallRule | Where-Object { $_.DisplayName -like "EDUAI*" } | Remove-NetFirewallRule -ErrorAction SilentlyContinue
Write-Host "      OK" -ForegroundColor Green

# --- Port 8000 Django (réseau local uniquement) ---
Write-Host "[2/5] Ouverture du port 8000 (Django - réseau local)..." -ForegroundColor Yellow
New-NetFirewallRule `
    -DisplayName "EDUAI-Django-8000" `
    -Direction Inbound `
    -Action Allow `
    -Protocol TCP `
    -LocalPort 8000 `
    -RemoteAddress LocalSubnet `
    -Profile Any `
    -Description "EDUAI Cameroun - Serveur Django accessible sur le LAN" `
    -ErrorAction Stop | Out-Null
Write-Host "      Port 8000 OUVERT (LAN uniquement)" -ForegroundColor Green

# --- Port 80 HTTP (réseau local uniquement) ---
Write-Host "[3/5] Ouverture du port 80 (HTTP - réseau local)..." -ForegroundColor Yellow
New-NetFirewallRule `
    -DisplayName "EDUAI-HTTP-80" `
    -Direction Inbound `
    -Action Allow `
    -Protocol TCP `
    -LocalPort 80 `
    -RemoteAddress LocalSubnet `
    -Profile Any `
    -Description "EDUAI Cameroun - HTTP sur le LAN" `
    -ErrorAction Stop | Out-Null
Write-Host "      Port 80 OUVERT (LAN uniquement)" -ForegroundColor Green

# --- MySQL 3306 : LOCAL UNIQUEMENT (loopback, jamais le réseau) ---
Write-Host "[4/5] Sécurisation de MySQL (local uniquement)..." -ForegroundColor Yellow
New-NetFirewallRule `
    -DisplayName "EDUAI-MySQL-Allow-Local" `
    -Direction Inbound `
    -Action Allow `
    -Protocol TCP `
    -LocalPort 3306 `
    -RemoteAddress 127.0.0.1 `
    -Profile Any `
    -Description "EDUAI - MySQL accessible uniquement depuis localhost" `
    -ErrorAction SilentlyContinue | Out-Null

New-NetFirewallRule `
    -DisplayName "EDUAI-MySQL-Block-LAN" `
    -Direction Inbound `
    -Action Block `
    -Protocol TCP `
    -LocalPort 3306 `
    -RemoteAddress LocalSubnet `
    -Profile Any `
    -Description "EDUAI - MySQL bloqué depuis le réseau" `
    -ErrorAction SilentlyContinue | Out-Null
Write-Host "      MySQL 3306 : BLOQUÉ depuis le réseau, local OK" -ForegroundColor Green

# --- Récapitulatif ---
Write-Host ""
Write-Host "[5/5] Vérification des règles créées..." -ForegroundColor Yellow
Write-Host ""
Get-NetFirewallRule | Where-Object { $_.DisplayName -like "EDUAI*" } | `
    Select-Object DisplayName, Direction, Action, Enabled | `
    Format-Table -AutoSize

# --- Afficher l'IP locale (carte Wi-Fi réelle, ignore VPN/Hyper-V) ---
Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "   Configuration terminee !                      " -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Adresse IP du serveur (a communiquer aux eleves) :"

# Priorité : carte Wi-Fi → exclure VPN (10.2.x), Hyper-V (172.x), APIPA (169.x), loopback
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
    $_.IPAddress -notlike "127.*" -and
    $_.IPAddress -notlike "169.*" -and
    $_.IPAddress -notlike "172.*" -and
    $_.IPAddress -notlike "10.2.*"
} | Select-Object -First 1).IPAddress

if (-not $ip) {
    # Fallback : prendre n'importe quelle IP non-loopback
    $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" } | Select-Object -First 1).IPAddress
}

Write-Host ""
Write-Host "   http://${ip}:8000" -ForegroundColor White -BackgroundColor DarkGreen
Write-Host ""
Write-Host "Les appareils connectes au meme Wi-Fi peuvent utiliser cette adresse." -ForegroundColor Gray
Write-Host ""
Write-Host ">> Si l'IP est incorrecte, faire 'ipconfig' et chercher 'Carte reseau sans fil Wi-Fi'" -ForegroundColor Yellow
Write-Host ""
