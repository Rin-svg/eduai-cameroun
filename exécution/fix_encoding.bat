@echo off
chcp 65001 > nul
title EDUAI Cameroun - Fix Encodage UTF-8

echo.
echo  ============================================
echo   EDUAI Cameroun - Correction Encodage
echo  ============================================
echo.

cd /d "C:\Users\RN-Re\Desktop\eduai_cameroun_v1.0\eduai_cameroun"

echo Activation du virtualenv...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERREUR : .venv introuvable.
    pause
    exit /b 1
)

echo Correction de l encodage en base...
python manage.py shell < scripts\fix_encoding_orm.py

if errorlevel 1 (
    echo ERREUR : Le script fix_encoding_orm.py a echoue.
    pause
    exit /b 1
)

echo.
echo  Correction terminee !
echo  Rechargez la page dans le navigateur.
echo.
pause
