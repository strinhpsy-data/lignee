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
echo   Verification de l'empreinte du contrat...
%PY% "outils\empreinte.py" --verifier
echo.
if "%~1"=="" ( %PY% "tests\contrat.py" ) else ( %PY% "tests\contrat.py" "%~f1" )
set "CODE=%ERRORLEVEL%"
echo.
if "%CODE%"=="0" (
  echo   ====================================================
  echo     TOUT EST AU VERT. Le travail peut etre livre.
  echo   ====================================================
) else (
  echo   ====================================================
  echo     DES CONTROLES ECHOUENT. Le travail n'est pas fini.
  echo     Apres trois tentatives infructueuses sur un meme
  echo     controle, declarez un blocage B-xx au journal
  echo     puis lancez Collecter_Panne.bat.
  echo   ====================================================
)
echo.
pause
endlocal
