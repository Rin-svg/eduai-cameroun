@echo off
chcp 65001 > nul
title EDUAI Cameroun - Configuration Pare-feu

echo.
echo  ============================================
echo   EDUAI Cameroun - Configuration Pare-feu
echo   NECESSITE LES DROITS ADMINISTRATEUR
echo  ============================================
echo.

:: Verifier si on est administrateur
net session >nul 2>&1
if errorlevel 1 (
    echo  Ce script necessite les droits Administrateur.
    echo  Relancement automatique en mode administrateur...
    echo.
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Lancer le script PowerShell pare-feu
powershell -ExecutionPolicy Bypass -File "C:\Users\RN-Re\Desktop\eduai_cameroun_v1.0\eduai_cameroun\scripts\configure_firewall.ps1"

if errorlevel 1 (
    echo.
    echo  ERREUR lors de la configuration du pare-feu.
    echo  Verifiez que vous etes bien administrateur.
) else (
    echo.
    echo  Pare-feu configure avec succes !
)

pause
