# EDUAI Cameroun - Fix encodage UTF-8 MySQL (PowerShell / WAMP)
# Executer : PowerShell -ExecutionPolicy Bypass -File scripts\fix_encoding.ps1

$mysqlExe = $null

$wampBase = "C:\wamp64\bin\mysql"
if (Test-Path $wampBase) {
    $versions = Get-ChildItem -Path $wampBase -Directory | Sort-Object Name -Descending
    foreach ($v in $versions) {
        $candidat = Join-Path $v.FullName "bin\mysql.exe"
        if (Test-Path $candidat) {
            $mysqlExe = $candidat
            break
        }
    }
}

if (-not $mysqlExe) {
    $wampBase32 = "C:\wamp\bin\mysql"
    if (Test-Path $wampBase32) {
        $versions = Get-ChildItem -Path $wampBase32 -Directory | Sort-Object Name -Descending
        foreach ($v in $versions) {
            $candidat = Join-Path $v.FullName "bin\mysql.exe"
            if (Test-Path $candidat) { $mysqlExe = $candidat; break }
        }
    }
}

if (-not $mysqlExe) {
    Write-Host "mysql.exe introuvable dans WAMP." -ForegroundColor Red
    Write-Host "Ouvre l explorateur et cherche mysql.exe dans C:\wamp64\" -ForegroundColor Yellow
    exit 1
}

Write-Host "MySQL trouve : $mysqlExe" -ForegroundColor Green

$dbName  = "eduai_cameroun"
$dbUser  = "root"
$sqlFile = "$PSScriptRoot\fix_encoding_and_data.sql"

Write-Host "Correction de l encodage UTF-8..." -ForegroundColor Cyan

Get-Content -Path $sqlFile -Raw -Encoding UTF8 | & $mysqlExe -u $dbUser --password="" $dbName

if ($LASTEXITCODE -eq 0) {
    Write-Host "Encodage corrige avec succes !" -ForegroundColor Green
    Write-Host ""
    Write-Host "Lance maintenant les quiz de demo :" -ForegroundColor Cyan
    Write-Host "Get-Content scripts\init_data.py | python manage.py shell" -ForegroundColor White
} else {
    Write-Host "Echec. Si tu as un mot de passe MySQL, remplace --password=`"`" par --password=`"TonMotDePasse`"" -ForegroundColor Yellow
}
