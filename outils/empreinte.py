#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scelle le contrat de vérification.

    python outils/empreinte.py --verifier   (par défaut)
    python outils/empreinte.py --poser      réservé à Claude

Pourquoi. Le protocole pose que les tests sont intouchables par Qwen : un test
qu'on retouche pour le faire passer n'est pas un test. L'empreinte rend la
retouche visible. Elle n'empêche rien — elle témoigne.

Seul Claude repose l'empreinte, et seulement après une modification délibérée
du contrat, consignée au journal sous un code C-xxx.
"""

import hashlib
import sys
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
TESTS = RACINE / "tests"
REF = TESTS / "EMPREINTE.txt"


def fichiers_scelles():
    """Le code des tests, pas les jeux de données : ceux-ci évoluent."""
    return sorted(TESTS.glob("*.py"))


def empreinte(f):
    return hashlib.sha256(f.read_bytes()).hexdigest()


def poser():
    lignes = [
        "# EMPREINTE DU CONTRAT DE VÉRIFICATION",
        "#",
        "# Posée par Claude le " + date.today().strftime("%Y-%m-%d") + ".",
        "# Ne pas modifier à la main. Si un contrôle vous semble faux,",
        "# inscrivez une question Q-xx au journal et poursuivez ailleurs.",
        "#",
    ]
    for f in fichiers_scelles():
        lignes.append(f"{empreinte(f)}  {f.name}")
    REF.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"Empreinte posée sur {len(fichiers_scelles())} fichier(s) :")
    for f in fichiers_scelles():
        print(f"  {f.name}")
    return 0


def verifier():
    if not REF.exists():
        print("EMPREINTE.txt absent — le contrat n'est pas scellé.")
        return 2
    attendus = {}
    for ligne in REF.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if ligne and not ligne.startswith("#"):
            h, _, nom = ligne.partition("  ")
            attendus[nom.strip()] = h.strip()

    ecarts = []
    for nom, h in attendus.items():
        f = TESTS / nom
        if not f.exists():
            ecarts.append(f"{nom} : ABSENT")
        elif empreinte(f) != h:
            ecarts.append(f"{nom} : MODIFIE")
    for f in fichiers_scelles():
        if f.name not in attendus:
            ecarts.append(f"{f.name} : AJOUTE (hors empreinte)")

    if ecarts:
        print("LE CONTRAT A ETE MODIFIE :")
        for e in ecarts:
            print(f"  {e}")
        return 1
    print(f"Contrat intact — {len(attendus)} fichier(s) conformes.")
    return 0


if __name__ == "__main__":
    sys.exit(poser() if "--poser" in sys.argv else verifier())
