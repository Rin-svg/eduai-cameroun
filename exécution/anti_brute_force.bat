@echo off
chcp 65001 > nul
title EDUAI Cameroun - Protection Anti Brute Force

echo.
echo  ============================================
echo   EDUAI Cameroun - Anti Brute Force
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

echo  Demarrage de la surveillance Anti-Brute Force...
echo  Laissez cette fenetre ouverte pendant la presentation.
echo  Appuyez sur Ctrl+C pour arreter.
echo.

powershell -ExecutionPolicy Bypass -File "C:\Users\RN-Re\Desktop\eduai_cameroun_v1.0\eduai_cameroun\scripts\anti_brute_force.ps1" -MySQLPath "C:\wamp64\bin\mysql\mysql9.1.0\bin\mysql.exe"

if errorlevel 1 (
    echo.
    echo  ERREUR lors de l'execution du script.
    echo  Verifiez que WAMP est demarre et que MySQL tourne.
) else (
    echo.
    echo  Protection desactivee.
)

pause
