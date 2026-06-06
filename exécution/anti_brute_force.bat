@echo off
chcp 65001 > nul
title EDUAI Cameroun - Protection Anti Brute Force

echo.
echo  ============================================
echo   EDUAI Cameroun - Anti Brute Force
echo  ============================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0scripts\anti_brute_force.ps1" -MySQLPath "C:\wamp64\bin\mysql\mysql9.1.0\bin\mysql.exe"

if errorlevel 1 (
    echo.
    echo ERREUR lors de l'execution du script.
) else (
    echo.
    echo Protection activee avec succes !
)

pause
