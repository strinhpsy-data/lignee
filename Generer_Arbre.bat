@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY ( where python >nul 2>&1 && set "PY=python" )
if not defined PY (
  echo.
  echo   ERREUR : Python est introuvable sur cette machine.
  echo.
  pause
  exit /b 1
)
echo.
if "%~1"=="" ( %PY% "src\generer_arbre.py" ) else ( %PY% "src\generer_arbre.py" "%~f1" )
echo.
pause
endlocal
