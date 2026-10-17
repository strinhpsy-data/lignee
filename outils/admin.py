#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
admin.py — le mot de passe du mode administrateur.

OÙ IL VIT. Nulle part en clair. Le projet ne garde qu'une empreinte salée
(PBKDF2-SHA256) dans outils/_admin.json, fichier exclu de git et de tout
export. C'est le serveur local qui compare : une page HTML ne peut rien
vérifier sans montrer ce qu'elle vérifie à qui ouvre sa source.

    python outils/admin.py            (demande le nouveau mot de passe)
    (ou double-clic sur Changer_Mot_De_Passe_Admin.bat)
"""

import getpass
import hashlib
import hmac
import json
import secrets
import sys
from pathlib import Path

FICHIER = Path(__file__).resolve().parent / "_admin.json"
TOURS = 240_000


def empreinte(mdp, sel):
    return hashlib.pbkdf2_hmac("sha256", mdp.encode("utf-8"), bytes.fromhex(sel), TOURS).hex()


def poser(mdp):
    sel = secrets.token_hex(16)
    FICHIER.write_text(json.dumps({"algo": "pbkdf2-sha256", "tours": TOURS, "sel": sel,
                                   "empreinte": empreinte(mdp, sel)}, indent=1),
                       encoding="utf-8")


def configure():
    return FICHIER.exists()


def verifier(mdp):
    if not isinstance(mdp, str) or not FICHIER.exists():
        return False
    try:
        c = json.loads(FICHIER.read_text(encoding="utf-8"))
        calc = hashlib.pbkdf2_hmac("sha256", mdp.encode("utf-8"), bytes.fromhex(c["sel"]),
                                   int(c.get("tours", TOURS))).hex()
        return hmac.compare_digest(calc, c["empreinte"])
    except Exception:
        return False


def main():
    print("=" * 58)
    print("  MOT DE PASSE DU MODE ADMINISTRATEUR")
    print("=" * 58)
    if FICHIER.exists():
        print("\n  Un mot de passe est déjà posé ; il sera remplacé.")
    a = getpass.getpass("\n  Nouveau mot de passe (rien ne s'affiche) : ")
    if not a:
        print("  Vide : rien n'a été changé."); return 1
    b = getpass.getpass("  Le même, une seconde fois               : ")
    if a != b:
        print("  Les deux saisies diffèrent : rien n'a été changé."); return 1
    poser(a)
    print("\n  Posé. Relancez Serveur_Local.bat s'il tourne déjà.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
