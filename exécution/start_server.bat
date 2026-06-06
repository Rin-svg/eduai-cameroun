@echo off
chcp 65001 > nul
title EDUAI Cameroun - Serveur Django

echo.
echo  ============================================
echo   EDUAI Cameroun - Plateforme Educative IA
echo  ============================================
echo.

:: Aller dans le dossier du projet (chemin fixe)
cd /d "C:\Users\RN-Re\Desktop\eduai_cameroun_v1.0\eduai_cameroun"
if errorlevel 1 (
    echo ERREUR : Dossier du projet introuvable.
    pause
    exit /b 1
)

:: Activer le virtualenv
echo [1/4] Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERREUR : .venv introuvable.
    pause
    exit /b 1
)

:: Appliquer les migrations si necessaire
echo [2/4] Verification des migrations...
python manage.py migrate --run-syncdb 2>nul

:: Recuperer l'IP Wi-Fi reelle
echo [3/4] Detection de l'adresse IP...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr "10.96"') do set IP=%%a
set IP=%IP: =%

:: Lancer le serveur
echo [4/4] Demarrage du serveur...
echo.
echo  Serveur accessible sur :
echo    - Local   : http://127.0.0.1:8000
echo    - Reseau  : http://%IP%:8000
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
