@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY ( where python >nul 2>&1 && set "PY=python" )
if not defined PY ( echo Python est introuvable. & pause & exit /b 9 )
echo.
%PY% outils\admin.py
echo.
pause
