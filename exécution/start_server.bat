@echo off
chcp 65001 > nul
title EDUAI Cameroun - Serveur Django

echo.
echo  ============================================
echo   EDUAI Cameroun - Plateforme Educative IA
echo  ============================================
echo.

:: Aller dans le dossier du projet
cd /d "%~dp0"

:: Activer le virtualenv
echo [1/3] Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERREUR : .venv introuvable. Verifiez que le venv est installe.
    pause
    exit /b 1
)

:: Appliquer les migrations si necessaire
echo [2/3] Verification des migrations...
python manage.py migrate --run-syncdb 2>nul

:: Lancer le serveur
echo [3/3] Demarrage du serveur...
echo.
echo  Serveur accessible sur :
echo    - Local    : http://127.0.0.1:8000
echo    - Reseau   : http://192.168.1.10:8000
echo.
echo  Comptes de demo :
echo    admin       / EduAI2025!
echo    enseignant1 / EduAI2025!
echo    eleve1      / EduAI2025!
echo.
echo  Appuyez sur Ctrl+C pour arreter le serveur.
echo  ============================================
echo.

python manage.py runserver 0.0.0.0:8000

pause
