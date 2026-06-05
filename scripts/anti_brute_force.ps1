# =====================================================
# EDUAI Cameroun — Script PowerShell Anti-Brute Force
# Surveillance Windows Defender Firewall
# Compatible Windows 11 Professionnel
# =====================================================

param(
    [int]$MaxTentatives = 5,
    [int]$DureeBlocageMin = 15,
    [string]$LogPath = "C:\eduai\logs\securite.log"
)

function Write-Log {
    param([string]$Message, [string]$Niveau = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $ligne = "[$timestamp] [$Niveau] $Message"
    Write-Host $ligne
    Add-Content -Path $LogPath -Value $ligne -Encoding UTF8
}

function Bloquer-IP {
    param([string]$IP)
    $ruleName = "EDUAI-Block-$IP"
    
    # Vérifier si déjà bloquée
    $existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    if ($existingRule) {
        Write-Log "IP $IP déjà bloquée." "WARN"
        return
    }
    
    # Ajouter règle pare-feu Windows Defender
    New-NetFirewallRule -DisplayName $ruleName `
        -Direction Inbound `
        -Action Block `
        -RemoteAddress $IP `
        -Protocol TCP `
        -LocalPort 80 `
        -Description "EDUAI: Bloqué pour brute force le $(Get-Date)" | Out-Null
    
    Write-Log "IP $IP BLOQUÉE — Règle pare-feu créée." "ALERTE"
    
    # Notification popup Windows
    $shell = New-Object -ComObject WScript.Shell
    $shell.Popup("⚠️ ALERTE SÉCURITÉ EDUAI`n`nIP bloquée : $IP`nRaison : Brute Force ($MaxTentatives tentatives)`nDurée : $DureeBlocageMin minutes", 10, "EDUAI — Alerte Sécurité", 48)
    
    # Planifier le déblocage
    $unblockScript = "Remove-NetFirewallRule -DisplayName 'EDUAI-Block-$IP' -ErrorAction SilentlyContinue"
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes($DureeBlocageMin)
    $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-Command `"$unblockScript`""
    Register-ScheduledTask -TaskName "EDUAI-Unblock-$IP" -Trigger $trigger -Action $action -Force | Out-Null
    
    Write-Log "Déblocage automatique de $IP programmé dans $DureeBlocageMin minutes." "INFO"
}

function Surveiller-Tentatives {
    Write-Log "=== Démarrage de la surveillance EDUAI Anti-Brute Force ===" "INFO"
    Write-Log "Configuration : Max $MaxTentatives tentatives / Blocage $DureeBlocageMin min" "INFO"
    
    # Créer le dossier de logs si nécessaire
    $logDir = Split-Path $LogPath
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    
    $compteurIP = @{}
    
    while ($true) {
        # Lire les logs IIS/Apache (XAMPP) — adapter le chemin si nécessaire
        $apacheLog = "C:\xampp\apache\logs\access.log"
        if (Test-Path $apacheLog) {
            $lignes = Get-Content $apacheLog -Tail 100
            foreach ($ligne in $lignes) {
                # Détecter les tentatives de connexion échouées (HTTP 401/403)
                if ($ligne -match '^(\d+\.\d+\.\d+\.\d+).*POST.*connexion.*" (401|403)') {
                    $ip = $Matches[1]
                    if (-not $compteurIP.ContainsKey($ip)) { $compteurIP[$ip] = 0 }
                    $compteurIP[$ip]++
                    
                    Write-Log "Tentative échouée de $ip (${compteurIP[$ip]}/$MaxTentatives)" "WARN"
                    
                    if ($compteurIP[$ip] -ge $MaxTentatives) {
                        Bloquer-IP -IP $ip
                        $compteurIP[$ip] = 0  # Réinitialiser après blocage
                    }
                }
            }
        }
        
        # Vérifier aussi les logs Django (fichier django.log si configuré)
        $djangoLog = "C:\eduai\logs\django.log"
        if (Test-Path $djangoLog) {
            $erreurs = Select-String -Path $djangoLog -Pattern "Failed login.*(\d+\.\d+\.\d+\.\d+)" -Tail 50
            foreach ($err in $erreurs) {
                if ($err.Line -match "(\d+\.\d+\.\d+\.\d+)") {
                    $ip = $Matches[1]
                    Write-Log "Échec Django détecté : $ip" "WARN"
                }
            }
        }
        
        Start-Sleep -Seconds 30  # Vérification toutes les 30 secondes
    }
}

# Démarrage
Surveiller-Tentatives
