# =====================================================
# EDUAI Cameroun — Anti-Brute Force PowerShell v2
# Synchronise les blocages Django → Pare-feu Windows
#
# Fonctionnement :
#   Django détecte les tentatives et bloque dans MySQL
#   Ce script lit MySQL toutes les 30s et applique
#   les mêmes blocages dans Windows Defender Firewall
#
# Lancer en tant qu'Administrateur :
#   powershell -ExecutionPolicy Bypass -File anti_brute_force.ps1
# =====================================================

param(
    [string]$MySQLPath  = "C:\wamp64\bin\mysql\mysql9.1.0\bin\mysql.exe",
    [string]$DBName     = "eduai_cameroun",
    [string]$DBUser     = "root",
    [string]$DBPassword = "",
    [string]$LogPath    = "C:\eduai\logs\anti_brute_force.log",
    [int]$IntervalSec   = 30
)

# ─── Fonctions utilitaires ────────────────────────────────────────────────────

function Write-Log {
    param([string]$Message, [string]$Niveau = "INFO")
    $ts   = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] [$Niveau] $Message"
    Write-Host $line -ForegroundColor $(switch ($Niveau) {
        "ALERTE" { "Red" }; "WARN" { "Yellow" }; "OK" { "Green" }; default { "Gray" }
    })
    try {
        $dir = Split-Path $LogPath
        if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        Add-Content -Path $LogPath -Value $line -Encoding UTF8
    } catch {}
}

function Executer-MySQL {
    param([string]$Query)
    $args_list = @("-u", $DBUser, "-e", $Query, $DBName)
    if ($DBPassword -ne "") { $args_list = @("-u", $DBUser, "-p$DBPassword") + $args_list[2..($args_list.Length-1)] }
    try {
        $result = & $MySQLPath @args_list 2>$null
        return $result
    } catch {
        return $null
    }
}

function Bloquer-IP-Firewall {
    param([string]$IP)
    $ruleName = "EDUAI-BruteForce-Block-$IP"
    $existe = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    if ($existe) { return $false }   # deja bloquee

    New-NetFirewallRule `
        -DisplayName $ruleName `
        -Direction Inbound `
        -Action Block `
        -RemoteAddress $IP `
        -Protocol TCP `
        -LocalPort @(80, 8000) `
        -Description "EDUAI: Brute force detecte par Django le $(Get-Date -Format 'dd/MM/yyyy HH:mm')" `
        | Out-Null

    Write-Log "Regle pare-feu creee : IP $IP bloquee sur ports 80 et 8000" "ALERTE"
    return $true
}

function Debloquer-IP-Firewall {
    param([string]$IP)
    $ruleName = "EDUAI-BruteForce-Block-$IP"
    $existe = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    if (-not $existe) { return }

    Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    Write-Log "Regle pare-feu supprimee : IP $IP debloquee" "OK"
}

function Verifier-MySQL-Accessible {
    $test = Executer-MySQL "SELECT 1;"
    return ($null -ne $test)
}

# ─── Démarrage ────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "   EDUAI Cameroun - Anti-Brute Force v2          " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Verifier que mysql.exe existe
if (-not (Test-Path $MySQLPath)) {
    Write-Host "[ERREUR] mysql.exe introuvable : $MySQLPath" -ForegroundColor Red
    Write-Host "         Verifiez que XAMPP est installe dans C:\xampp\" -ForegroundColor Yellow
    Write-Host "         Ou relancez avec : -MySQLPath 'C:\chemin\vers\mysql.exe'" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entree pour quitter"
    exit 1
}

Write-Log "Demarrage de la surveillance EDUAI Anti-Brute Force" "INFO"
Write-Log "Verification toutes les $IntervalSec secondes" "INFO"
Write-Log "Base de donnees : $DBName sur localhost:3306" "INFO"
Write-Host ""

# ─── Boucle principale ────────────────────────────────────────────────────────

$ips_bloquees_fw = @{}   # IPs actuellement bloquees dans le pare-feu par ce script

while ($true) {

    # 1. Verifier que MySQL tourne
    if (-not (Verifier-MySQL-Accessible)) {
        Write-Log "MySQL inaccessible, nouvelle tentative dans $IntervalSec sec..." "WARN"
        Start-Sleep -Seconds $IntervalSec
        continue
    }

    # 2. Lire les IPs bloquees par Django dans MySQL
    $query = "SELECT adresse_ip, nb_tentatives, fin_blocage FROM securite_tentativeconnexion WHERE est_bloque=1 AND fin_blocage > NOW();"
    $rows  = Executer-MySQL $query

    $ips_actives = @{}

    if ($rows) {
        foreach ($row in $rows) {
            # Ignorer l'en-tete MySQL
            if ($row -match "^adresse_ip") { continue }
            $cols = $row -split "\t"
            if ($cols.Count -lt 1) { continue }
            $ip = $cols[0].Trim()
            if ($ip -match "^\d+\.\d+\.\d+\.\d+$") {
                $ips_actives[$ip] = $true

                # Bloquer dans le pare-feu si pas encore fait
                $nouveau = Bloquer-IP-Firewall -IP $ip
                if ($nouveau) {
                    $tentatives = if ($cols.Count -gt 1) { $cols[1].Trim() } else { "?" }
                    $fin        = if ($cols.Count -gt 2) { $cols[2].Trim() } else { "?" }
                    Write-Log "BRUTE FORCE : IP=$ip | Tentatives=$tentatives | Deblocage=$fin" "ALERTE"

                    # Popup Windows si disponible
                    try {
                        $shell = New-Object -ComObject WScript.Shell
                        $shell.Popup("ALERTE SECURITE EDUAI`n`nIP bloquee : $ip`nTentatives : $tentatives`nDeblocage auto : $fin", 8, "EDUAI - Alerte", 48)
                    } catch {}
                }
            }
        }
    }

    # 3. Debloquer les IPs dont le blocage Django a expire
    foreach ($ip in @($ips_bloquees_fw.Keys)) {
        if (-not $ips_actives.ContainsKey($ip)) {
            Debloquer-IP-Firewall -IP $ip
            $ips_bloquees_fw.Remove($ip)
        }
    }

    # Mettre a jour le suivi local
    $ips_bloquees_fw = $ips_actives

    # 4. Afficher un resume toutes les 10 cycles (~5 min)
    $script:cycle = if ($script:cycle) { $script:cycle + 1 } else { 1 }
    if ($script:cycle % 10 -eq 0) {
        $nb_fw    = (Get-NetFirewallRule | Where-Object { $_.DisplayName -like "EDUAI-BruteForce*" }).Count
        $nb_mysql = $ips_actives.Count
        Write-Log "Resume : $nb_mysql IP(s) bloquees dans Django | $nb_fw regle(s) pare-feu actives" "INFO"
    }

    Start-Sleep -Seconds $IntervalSec
}
