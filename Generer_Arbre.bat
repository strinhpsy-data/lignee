@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY ( where python >nul 2>&1 && set "PY=python" )
if not defined PY goto :pasdepython

if "%~1"=="" goto :defaut

rem Un fichier glisse sur l'icone. Le generateur nomme sa sortie en
rem remplacant "genealogie_" par "arbre_" ; on refait le meme calcul.
set "NOM=%~n1"
set "CIBLE=arbre_!NOM:genealogie_=!.html"
echo.
%PY% "src\generer_arbre.py" "%~f1"
set "CODE=!ERRORLEVEL!"
goto :apres

:defaut
set "CIBLE=arbre_samuel.html"
echo.
%PY% "src\generer_arbre.py"
set "CODE=!ERRORLEVEL!"
goto :apres

:apres
echo.
if not "!CODE!"=="0" goto :echec
if not exist "!CIBLE!" goto :introuvable

rem Le fichier est fait. Reste a le MONTRER : sans cela la fenetre se
rem ferme et il ne se passe visiblement rien. Si le serveur local tourne
rem deja, on ouvre par lui -- c'est le seul mode ou les fiches
rem enregistrent directement dans le projet.
powershell -NoProfile -Command "try{$c=New-Object Net.Sockets.TcpClient;$c.Connect('127.0.0.1',8731);$c.Close();exit 0}catch{exit 1}" >nul 2>&1
if errorlevel 1 goto :sansserveur

echo   --------------------------------------------------------------
echo    Ouverture par le serveur local.
echo    Vos ajouts s'enregistreront directement dans le projet.
echo   --------------------------------------------------------------
start "" "http://127.0.0.1:8731/!CIBLE!"
goto :fin

:sansserveur
echo   --------------------------------------------------------------
echo    Fichier produit : !CIBLE!
echo.
echo    Le serveur local ne tourne pas. Vous pouvez regarder l'arbre,
echo    mais le bouton des fiches dira "Enregistrer mes ajouts" et
echo    rendra un fichier au lieu d'ecrire dans le projet.
echo    Pour contribuer : lancez Serveur_Local.bat.
echo   --------------------------------------------------------------
start "" "%~dp0!CIBLE!"
goto :fin

:echec
echo   --------------------------------------------------------------
echo    LA GENERATION A ECHOUE (code !CODE!).
echo    Le message ci-dessus dit pourquoi. L'arbre n'a PAS ete refait.
echo   --------------------------------------------------------------
goto :fin

:introuvable
echo   --------------------------------------------------------------
echo    Le generateur s'est termine sans erreur, mais !CIBLE! est
echo    introuvable. Signalez-le : c'est anormal.
echo   --------------------------------------------------------------
goto :fin

:pasdepython
echo.
echo   ERREUR : Python est introuvable sur cette machine.
echo.

:fin
echo.
pause
endlocal
