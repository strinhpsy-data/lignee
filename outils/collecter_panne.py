#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rassemble tout ce qu'il faut pour diagnostiquer une panne, en une archive.

Produit  panne_AAAA-MM-JJ_HHhMM.zip  à côté du projet.
C'est CE fichier qui passe par le sas — rien à recopier à la main.

Ce qui entre dans l'archive :
  - la sortie complète du contrôle (verifier.py), erreurs comprises
  - la sortie complète du générateur
  - les fichiers SOURCE : .py, .json, .bat, .md
  - l'inventaire du répertoire avec tailles et dates
  - les versions de Python et des bibliothèques utiles
  - le journal de travail de Qwen s'il existe

Ce qui N'ENTRE PAS :
  - les fichiers produits (.html, dossiers *_fiches) : ils se régénèrent,
    ils pèsent plus que tout le reste réuni, et les lire coûte cher.
  - les photos : lourdes et sans rapport avec un défaut de code.
"""

import json
import platform
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent   # le script vit dans outils/
EXT_SOURCE = {".py", ".json", ".bat", ".md", ".txt", ".yaml", ".yml"}
EXCLUS_DOSSIERS = {"photos", "Scans", "Scans OCR", "__pycache__", ".git", "sorties"}


def lancer(cmd, minutes=5):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=minutes * 60)
        return (f"$ {' '.join(str(c) for c in cmd)}\n"
                f"[code de sortie : {r.returncode}]\n\n"
                f"--- sortie standard ---\n{r.stdout}\n"
                f"--- sortie d'erreur ---\n{r.stderr}\n")
    except subprocess.TimeoutExpired:
        return f"$ {' '.join(str(c) for c in cmd)}\n[DÉPASSEMENT DE DÉLAI après {minutes} min]\n"
    except Exception as e:
        return f"$ {' '.join(str(c) for c in cmd)}\n[IMPOSSIBLE À LANCER] {type(e).__name__}: {e}\n"


def environnement():
    L = [f"date            : {datetime.now():%Y-%m-%d %H:%M}",
         f"machine         : {platform.node()}",
         f"système         : {platform.platform()}",
         f"python          : {sys.version.splitlines()[0]}",
         f"exécutable      : {sys.executable}"]
    for mod in ("PIL", "playwright"):
        try:
            m = __import__(mod)
            L.append(f"{mod:<16}: {getattr(m, '__version__', 'présent')}")
        except ImportError:
            L.append(f"{mod:<16}: ABSENT")
    return "\n".join(L)


def inventaire():
    L = []
    for f in sorted(RACINE.rglob("*")):
        if any(part in EXCLUS_DOSSIERS for part in f.parts):
            continue
        rel = f.relative_to(RACINE)
        if f.is_dir():
            n = len(list(f.glob("*")))
            L.append(f"{'<dossier>':>12}  {rel}/   ({n} éléments)")
        else:
            d = datetime.fromtimestamp(f.stat().st_mtime)
            L.append(f"{f.stat().st_size:>12}  {rel}   {d:%Y-%m-%d %H:%M}")
    return "\n".join(L)


def main():
    horodate = f"{datetime.now():%Y-%m-%d_%Hh%M}"
    archive = RACINE / f"panne_{horodate}.zip"

    print("Collecte en cours — les contrôles sont relancés, patientez.\n")

    print("  1/4  environnement")
    env = environnement()

    print("  2/4  générateur")
    sortie_gen = lancer([sys.executable, "-I", str(RACINE / "src" / "generer_arbre.py")])

    print("  3/4  contrôles")
    sortie_ver = lancer([sys.executable, "-I", str(RACINE / "tests" / "contrat.py")], minutes=10)

    print("  4/4  inventaire et mise en archive")
    inv = inventaire()

    entete = (
        "RAPPORT DE PANNE — arbre généalogique\n"
        "=====================================\n\n"
        "Produit automatiquement. Aucune ligne n'a été saisie à la main.\n\n"
        "À LIRE EN PREMIER : la section CONTRÔLES ci-dessous indique quels\n"
        "contrôles échouent. Commencez par là ; n'ouvrez les sources que\n"
        "pour les fonctions que ces échecs désignent.\n\n"
        "Les fichiers produits (.html, dossiers *_fiches) ne sont PAS dans\n"
        "cette archive : ils se régénèrent en lançant Generer_Arbre.bat.\n"
    )

    rapport = (f"{entete}\n\n"
               f"{'=' * 62}\nENVIRONNEMENT\n{'=' * 62}\n{env}\n\n"
               f"{'=' * 62}\nGÉNÉRATEUR\n{'=' * 62}\n{sortie_gen}\n\n"
               f"{'=' * 62}\nCONTRÔLES\n{'=' * 62}\n{sortie_ver}\n\n"
               f"{'=' * 62}\nINVENTAIRE DU RÉPERTOIRE\n{'=' * 62}\n{inv}\n")

    n = 0
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("RAPPORT.txt", rapport)
        for f in sorted(RACINE.rglob("*")):
            if not f.is_file():
                continue
            if any(part in EXCLUS_DOSSIERS for part in f.parts):
                continue
            if f.suffix.lower() not in EXT_SOURCE:
                continue
            if f.name.startswith("panne_"):
                continue
            z.write(f, str(f.relative_to(RACINE)))
            n += 1

    ko = archive.stat().st_size // 1024
    print(f"\nArchive produite : {archive.name}  ({ko} Ko, {n} fichiers source)")
    print("\nC'est ce seul fichier qui passe par le sas.")
    echecs = sortie_ver.count("\n  ECHEC ")
    if echecs:
        print(f"Rappel : {echecs} contrôle(s) en échec sont décrits dans RAPPORT.txt.")
    else:
        print("Note : aucun contrôle n'échoue actuellement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
