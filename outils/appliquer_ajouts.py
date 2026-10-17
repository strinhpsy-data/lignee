#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
appliquer_ajouts.py — range dans le projet un fichier « ajouts-*.json »
produit depuis une fiche.

POURQUOI CE DÉTOUR. Une page ouverte en « file:// » ne peut pas écrire sur
le disque : c'est une barrière du navigateur, et aucune astuce ne la lève
sans serveur ni réseau — deux choses que ce projet s'interdit. La fiche
rend donc un fichier, et c'est cet outil qui le range.

L'avantage inattendu : ce chemin marche aussi pour un oncle à qui on envoie
une branche. Il remplit sa fiche, il renvoie un fichier de quelques kilo-
octets, et personne n'a eu à installer quoi que ce soit. C'est la réponse à
la question Q-02.

CE QU'IL NE FAIT JAMAIS
  - écraser une photo existante : il la garde et range la nouvelle à côté ;
  - remplacer en silence un fait attesté : il le signale et s'abstient ;
  - supprimer quoi que ce soit.

    python outils/appliquer_ajouts.py ajouts-samuel-trinh.json
    (ou glisser le fichier sur Appliquer_Ajouts.bat)
"""

import base64
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PHOTOS = RACINE / "photos"
REGISTRE = PHOTOS / "_ajouts_appliques.json"

EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
       "image/gif": ".gif", "image/heic": ".heic"}


def decoder(url):
    m = re.match(r"data:([^;]+);base64,(.*)$", url or "", re.S)
    if not m:
        return None, None
    return EXT.get(m.group(1), ".jpg"), base64.b64decode(m.group(2))


EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff")


def nom_nu_pris(base):
    """Le nom sans numéro est-il déjà employé, QUELLE QUE SOIT l'extension ?

    Le générateur cherche le portrait en essayant les extensions dans
    l'ordre, « .jpg » d'abord. Une photo de galerie installée sous
    « samuel-trinh.jpg » passait donc devant le vrai portrait
    « samuel-trinh.png » : c'est l'ordre alphabétique des extensions qui
    choisissait le visage, c'est-à-dire le hasard."""
    return any((PHOTOS / (base + e)).exists() for e in EXTENSIONS)


def place(base, ext, portrait):
    """Où ranger une image, sans jamais en écraser une autre.

    Le nom nu est RÉSERVÉ au portrait : une photo de galerie va toujours
    dans un emplacement numéroté, même si le nom nu est libre."""
    if portrait:
        if not nom_nu_pris(base):
            return PHOTOS / (base + ext), None
        occupe = next((PHOTOS / (base + e) for e in EXTENSIONS
                       if (PHOTOS / (base + e)).exists()), None)
    else:
        occupe = None
    for n in range(2, 200):
        q = PHOTOS / f"{base}-{n}{ext}"
        if not q.exists():
            return q, occupe
    raise RuntimeError("trop de photos pour " + base)


def certitude(texte):
    if re.search(r"\b\d{1,2}-\d{2}-\d{4}\b", texte):
        return "attestee"
    if re.search(r"\b(1[5-9]\d\d|20[0-2]\d)\b", texte):
        return "approximative"
    return "inconnue"


def fichier_des_donnees(pid):
    """Le fichier de données qui contient cette personne. On cherche plutôt
    que de le faire déclarer : un parent ne saura pas lequel c'est."""
    for f in sorted(RACINE.glob("genealogie_*.json")):
        if "brouillon" in f.name:
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if pid in d.get("personnes", {}):
            return f, d
    return None, None


def appliquer(chemin, force=False):
    """Un même fichier appliqué deux fois dupliquait ses recettes et rangeait
    ses photos une seconde fois. Les protections tenaient — rien n'était
    écrasé — mais le résultat était faux quand même. On retient donc
    l'empreinte de ce qui a déjà été versé."""
    brut = Path(chemin).read_bytes()
    a = json.loads(brut.decode("utf-8"))
    pid = a.get("id")
    if not pid:
        print(f"  {chemin} : pas d'identifiant, ignoré."); return 1

    emp = hashlib.sha256(brut).hexdigest()[:16]
    vus = {}
    if REGISTRE.exists():
        try:
            vus = json.loads(REGISTRE.read_text(encoding="utf-8"))
        except Exception:
            vus = {}
    if emp in vus and not force:
        print(f"  {pid} — DÉJÀ APPLIQUÉ le {vus[emp]}. Rien refait.")
        print("    (relancer avec --force si c'est bien voulu)")
        return 0

    f, d = fichier_des_donnees(pid)
    if f is None:
        print(f"  « {pid} » ne figure dans aucun fichier de données du projet.")
        print("  Rien n'a été modifié.")
        return 2

    p = d["personnes"][pid]
    PHOTOS.mkdir(exist_ok=True)
    quand = a.get("date") or date.today().isoformat()
    marque = f"Ajout de {a.get('nom') or pid}, {quand}"
    faits_ecrits, photos_ecrites, recettes, refus = [], [], 0, []

    # ---- portrait ----
    if a.get("portrait"):
        ext, octets = decoder(a["portrait"]["donnee"])
        if octets:
            cible, occupe = place(pid, ext, portrait=True)
            cible.write_bytes(octets)
            photos_ecrites.append(cible.name)
            if occupe:
                refus.append(f"portrait déjà présent ({occupe.name}) — "
                             f"la nouvelle image est rangée en {cible.name}")

    # ---- photos de la galerie ----
    for ph in a.get("photos", []):
        ext, octets = decoder(ph.get("donnee"))
        if not octets:
            continue
        cible, _ = place(pid, ext, portrait=False)
        cible.write_bytes(octets)
        photos_ecrites.append(cible.name)
        if ph.get("legende"):
            p.setdefault("galerie", []).append(
                {"fichier": cible.name, "legende": ph["legende"]})

    # ---- faits datés ----
    for cle, texte in (a.get("faits") or {}).items():
        ancien = p.get(cle)
        if ancien and ancien.get("certitude") == "attestee":
            refus.append(f"{cle} : « {ancien.get('texte')} » est attesté par la "
                         f"source ; « {texte} » n'a pas été écrit")
            continue
        p[cle] = {"texte": texte, "certitude": certitude(texte),
                  "note": marque}
        m = re.search(r"\b(1[5-9]\d\d|20[0-2]\d)\b", texte)
        if m:
            p[cle]["tri"] = int(m.group(1))
        faits_ecrits.append(cle)

    # ---- recettes ----
    for rc in a.get("recettes", []):
        if not (rc.get("titre") or rc.get("texte")):
            continue
        p.setdefault("sections", []).append({
            "titre": "Recette — " + (rc.get("titre") or "sans nom"),
            "type": "texte", "source": marque,
            "contenu": [l for l in (rc.get("texte") or "").split("\n\n") if l.strip()]
                       or [rc.get("texte", "")]})
        recettes += 1

    if faits_ecrits or recettes or photos_ecrites:
        src = p.setdefault("sources", [])
        if marque not in src:
            src.append(marque)
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        vus[emp] = quand
        REGISTRE.write_text(json.dumps(vus, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"  {pid} — dans {f.name}")
    print(f"    photos rangées : {len(photos_ecrites)}"
          + (f"  ({', '.join(photos_ecrites)})" if photos_ecrites else ""))
    print(f"    faits versés   : {len(faits_ecrits)}"
          + (f"  ({', '.join(faits_ecrits)})" if faits_ecrits else ""))
    print(f"    recettes       : {recettes}")
    for x in refus:
        print(f"    NON ÉCRIT — {x}")
    return 0


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not args:
        args = [str(x) for x in sorted(RACINE.glob("ajouts-*.json"))]
    if not args:
        print(__doc__)
        print("Aucun fichier « ajouts-*.json » trouvé à la racine du projet.")
        return 1
    print("=" * 58)
    print("  APPLICATION DES AJOUTS")
    print("=" * 58)
    force = "--force" in sys.argv
    pire = 0
    for x in args:
        pire = max(pire, appliquer(x, force))
    print("\nRelancez Generer_Arbre.bat pour voir le résultat.")
    return pire


if __name__ == "__main__":
    sys.exit(main())
