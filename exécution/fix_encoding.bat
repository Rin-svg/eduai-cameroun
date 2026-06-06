@echo off
chcp 65001 > nul
title EDUAI Cameroun - Fix Encodage UTF-8

echo.
echo  ============================================
echo   EDUAI Cameroun - Correction Encodage
echo  ============================================
echo.

cd /d "%~dp0"

echo Activation du virtualenv...
call .venv\Scripts\activate.bat

echo Correction de l encodage en base...
powershell -Command "Get-Content scripts\fix_encoding_orm.py | python manage.py shell"

echo.
echo Correction terminee ! Rechargez la page dans le navigateur.
pause
