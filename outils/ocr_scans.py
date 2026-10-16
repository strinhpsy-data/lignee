#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ocr_scans.py — océrise les documents paginés de Scans/ et nomme chaque page
par son numéro imprimé.

CE N'EST PAS UNE DEPENDANCE DU GENERATEUR. Le générateur d'arbre ne connaît
que Python et Pillow (H-10). Cet outil-ci a besoin de pdftoppm (poppler) et
de tesseract : s'ils manquent, c'est lui seul qui s'arrête, et Tester.bat
reste vert.

Deux phases, séparées exprès sur la ligne des dépendances :

  --ocr        rend et océrise chaque page vers un cache de texte brut.
               Lent, reprenable, exige poppler et tesseract.
  --resoudre   lit le cache, retrouve les numéros de page imprimés, et écrit
               Scans OCR/<document>/pNNN.txt. Rapide, pur Python, rejouable.

JAMAIS D'INVENTION. Un numéro déduit l'est à partir du décalage établi par
les numéros lus du même fichier de scan — c'est une preuve, pas une
supposition — et il est marqué « deduite ». Un numéro ni lu ni encadré reste
« inconnue », et son texte part dans _non-identifiees/.

    python outils/ocr_scans.py --ocr [--document <id>] [--secondes 150]
    python outils/ocr_scans.py --resoudre
"""

import json
import os
import re
import shutil
import tempfile
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SCANS = RACINE / "Scans"
SORTIE = RACINE / "Scans OCR"
DECLARATION = SCANS / "_documents.json"
TESSDATA = RACINE / "outils" / "tessdata"
DPI = 200          # éprouvé : qualité pleine en français et en vietnamien
ENV = dict(os.environ, OMP_THREAD_LIMIT="1")


def lire_declaration():
    if not DECLARATION.exists():
        print(f"ERREUR : déclaration absente -> {DECLARATION}")
        print("Elle dit quels fichiers de scan appartiennent à quel document.")
        sys.exit(2)
    return json.loads(DECLARATION.read_text(encoding="utf-8"))["documents"]


def outil_present(nom):
    return shutil.which(nom) is not None


# =====================================================================
# Phase 1 — rendu et OCR
# =====================================================================

def nb_pages(pdf):
    s = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
    for ligne in s.stdout.splitlines():
        if ligne.startswith("Pages:"):
            return int(ligne.split()[1])
    return 0


def orientation(png):
    """Demande à tesseract s'il faut tourner la page. Trois pages du premier
    PDF étaient numérisées à l'envers, et une quatrième l'est dans le
    document vietnamien : une chaîne qui ne regarde pas l'orientation
    produit du texte inventé avec aplomb. L'appel coûte 0,8 s, l'OCR en
    coûte 8 : ce n'est pas là qu'il faut économiser."""
    s = subprocess.run(["tesseract", str(png), "-", "--psm", "0"],
                       capture_output=True, text=True, env=ENV)
    m = re.search(r"Rotate:\s*(\d+)", s.stdout)
    return int(m.group(1)) if m else 0


def ocr_image(png, langue):
    tourne = orientation(png)
    if tourne:
        from PIL import Image
        with Image.open(png) as im:
            im.rotate(-tourne, expand=True).save(png)
    # --psm 3 et non 1 : le mode 1 refait en interne la detection
    # d'orientation qu'on vient de lui demander separement. Deux secondes
    # par page, sur 407 pages, c'est un quart d'heure.
    cmd = ["tesseract", str(png), "-", "-l", langue, "--psm", "3"]
    if TESSDATA.exists():
        cmd += ["--tessdata-dir", str(TESSDATA)]
    s = subprocess.run(cmd, capture_output=True, text=True, env=ENV)
    return s.stdout, tourne


def phase_ocr(documents, filtre, secondes):
    for outil in ("pdfinfo", "pdftoppm", "tesseract"):
        if not outil_present(outil):
            print(f"ERREUR : {outil} est absent. Cette phase a besoin de "
                  "poppler et de tesseract.")
            return 2

    debut = time.time()
    faites = sautees = 0

    # Les rendus intermédiaires sont des déchets de fabrication : ils vont
    # dans un dossier temporaire du système, JAMAIS dans le dossier du
    # projet. Deux raisons, et la première suffit : ils n'ont rien à faire
    # sous les yeux de l'utilisateur. La seconde est qu'un dossier connecté
    # peut refuser la suppression, et la chaîne s'arrêtait là.
    tmp = Path(tempfile.mkdtemp(prefix="ocr_arbre_"))

    # Un fichier de scan se rend d'un seul coup (0,4 s par page au lieu de
    # 2 s), puis ses pages s'océrisent en parallèle. Tesseract se parallélise
    # mal tout seul : on lui interdit ses propres fils (OMP_THREAD_LIMIT=1)
    # et on lance autant de processus que de coeurs. C'est ce qui ramène
    # l'affaire d'une heure à une dizaine de minutes.
    ouvriers = max(1, os.cpu_count() or 2)
    print(f"({ouvriers} ouvriers en parallèle, rendu à {DPI} dpi)")

    for doc in documents:
        if filtre and doc["id"] != filtre:
            continue
        brut = SORTIE / doc["id"] / "_brut"
        brut.mkdir(parents=True, exist_ok=True)
        print(f"\n=== {doc['id']} — {doc['titre']} — langue {doc['langue']} ===")

        for nom in doc["fichiers"]:
            pdf = SCANS / nom
            if not pdf.exists():
                print(f"  ABSENT  {nom}")
                continue
            tige = pdf.stem
            total = nb_pages(pdf)
            manquantes = [p for p in range(1, total + 1)
                          if not (brut / f"{tige}-{p:03d}.txt").exists()]
            sautees += total - len(manquantes)
            if not manquantes:
                continue
            if time.time() - debut > secondes:
                print(f"\n  (temps imparti atteint — relancer pour continuer ; "
                      f"{faites} pages faites cette passe)")
                shutil.rmtree(tmp, ignore_errors=True)
                return 0

            atelier = tmp / tige
            atelier.mkdir(parents=True, exist_ok=True)
            subprocess.run(["pdftoppm", "-r", str(DPI), "-gray", "-png",
                            str(pdf), str(atelier / "p")], capture_output=True)
            rendus = {}
            for png in atelier.glob("p-*.png"):
                m = re.search(r"p-(\d+)\.png$", png.name)
                if m:
                    rendus[int(m.group(1))] = png

            def une(page):
                png = rendus.get(page)
                if png is None:
                    return page, None, None
                texte, tourne = ocr_image(png, doc["langue"])
                return page, texte, tourne

            with ThreadPoolExecutor(max_workers=ouvriers) as pool:
                for page, texte, tourne in pool.map(une, manquantes):
                    if texte is None:
                        print(f"  RENDU IMPOSSIBLE  {tige} page {page}")
                        continue
                    entete = (f"@@ scan={tige} page_physique={page} "
                              f"rotation={tourne}\n")
                    (brut / f"{tige}-{page:03d}.txt").write_text(
                        entete + texte, encoding="utf-8")
                    faites += 1
            shutil.rmtree(atelier, ignore_errors=True)
            print(f"  {tige} : {len(manquantes)} pages faites "
                  f"({time.time() - debut:.0f} s écoulées)")

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{faites} pages océrisées cette passe, {sautees} déjà faites.")
    return 0


# =====================================================================
# Phase 2 — retrouver les numéros imprimés
# =====================================================================

def candidats_numero(texte):
    """Numéros de page candidats, avec un poids.

    On ne regarde QUE les bords de la page. Au milieu d'une généalogie, un
    nombre est une date, un âge ou un nombre d'enfants — jamais une
    pagination. Lire le corps du texte produirait des numéros plausibles et
    faux, ce qui est la pire sortie possible pour ce projet.
    """
    lignes = [l.strip() for l in texte.splitlines() if l.strip()]
    lignes = [l for l in lignes if not l.startswith("@@ ")]
    if not lignes:
        return []
    zones = []
    for l in lignes[-2:]:
        zones.append(("bas", l))
    for l in lignes[:2]:
        zones.append(("haut", l))

    out = []
    for zone, l in zones:
        if re.fullmatch(r"\d{1,4}", l):
            out.append((int(l), 3, zone))       # la ligne n'est que le numéro
            continue
        m = re.search(r"(?:^|\s)(\d{1,4})\s*[.·]?\s*$", l)
        if m:
            out.append((int(m.group(1)), 2, zone))
        m = re.match(r"^(\d{1,4})(?:\s|$)", l)
        if m:
            out.append((int(m.group(1)), 2 if zone == "haut" else 1, zone))
    return [(n, p, z) for (n, p, z) in out if 1 <= n <= 9999]


def resoudre_fichier(brut, tige, total):
    """Pour un fichier de scan : établit le décalage entre page physique et
    numéro imprimé, puis en déduit le numéro de chaque page.

    Le décalage est constant à l'intérieur d'un fichier, puisqu'un fichier
    est un lot de pages consécutives. C'est cette régularité qui permet de
    déduire sans deviner : un seul numéro lu suffit à nommer tout le lot, et
    plusieurs numéros lus se vérifient mutuellement.
    """
    lu = {}
    for page in range(1, total + 1):
        f = brut / f"{tige}-{page:03d}.txt"
        lu[page] = candidats_numero(f.read_text(encoding="utf-8")) if f.exists() else []

    votes = Counter()
    for page, cands in lu.items():
        for n, poids, _ in cands:
            if poids >= 2:
                votes[n - page] += poids

    if not votes:
        return None, {p: ("inconnue", None, lu[p]) for p in lu}

    decalage, _ = votes.most_common(1)[0]
    pages = {}
    for page, cands in lu.items():
        attendu = page + decalage
        if attendu < 1:
            pages[page] = ("inconnue", None, cands)
            continue
        if any(n == attendu for n, _, _ in cands):
            pages[page] = ("attestee", attendu, cands)
        elif cands:
            pages[page] = ("incoherente", attendu, cands)
        else:
            pages[page] = ("deduite", attendu, cands)
    return decalage, pages


def phase_resoudre(documents):
    inventaire_global = {}
    for doc in documents:
        base = SORTIE / doc["id"]
        brut = base / "_brut"
        if not brut.exists():
            print(f"{doc['id']} : aucun texte brut — lancer d'abord --ocr")
            continue
        inconnues = base / "_non-identifiees"
        inconnues.mkdir(parents=True, exist_ok=True)

        entrees = []
        occupe = {}
        for nom in doc["fichiers"]:
            tige = Path(nom).stem
            total = len(list(brut.glob(f"{tige}-*.txt")))
            if total == 0:
                continue
            decalage, pages = resoudre_fichier(brut, tige, total)
            for page in sorted(pages):
                certitude, numero, cands = pages[page]
                src = brut / f"{tige}-{page:03d}.txt"
                texte = src.read_text(encoding="utf-8") if src.exists() else ""
                corps = "\n".join(l for l in texte.splitlines()
                                  if not l.startswith("@@ "))
                if numero is None:
                    cible = inconnues / f"{tige}-{page:03d}.txt"
                else:
                    cible = base / f"p{numero:03d}.txt"
                    if numero in occupe:
                        # Un doublon n'est PAS une incoherence. Les lots se
                        # chevauchent d'une page ou deux aux jointures, parce
                        # qu'on repose le livre sur la vitre : c'est normal,
                        # et l'appeler incoherence ferait crier au loup.
                        certitude = "doublon"
                        cible = inconnues / f"p{numero:03d}-doublon-{tige}-{page:03d}.txt"
                    else:
                        occupe[numero] = (tige, page)
                enrobage = (f"# document : {doc['titre']}\n"
                            f"# page imprimée : {numero if numero else 'inconnue'}"
                            f"  (certitude : {certitude})\n"
                            f"# scan : {tige}.pdf, page physique {page}"
                            f"  (décalage {decalage if decalage is not None else '?'})\n"
                            f"#\n")
                cible.write_text(enrobage + corps, encoding="utf-8")
                entrees.append({"scan": tige, "page_physique": page,
                                "page_imprimee": numero, "certitude": certitude,
                                "decalage": decalage,
                                "candidats": [[n, p] for n, p, _ in cands],
                                "fichier": cible.name})

        compte = Counter(e["certitude"] for e in entrees)
        numeros = sorted(n for n in occupe)
        trous = [n for n in range(min(numeros), max(numeros) + 1)
                 if n not in occupe] if numeros else []
        inventaire_global[doc["id"]] = {
            "titre": doc["titre"], "langue": doc["langue"],
            "pages_declarees": doc.get("pages"),
            "pages_nommees": len(numeros),
            "etendue": [min(numeros), max(numeros)] if numeros else None,
            "lacunes_internes": trous,
            "certitudes": dict(compte),
            "pages": entrees,
        }
        print(f"\n=== {doc['id']} — {doc['titre']} ===")
        print(f"  pages nommées   : {len(numeros)}"
              + (f"  (p. {min(numeros)} à {max(numeros)})" if numeros else ""))
        for c in ("attestee", "deduite", "doublon", "incoherente", "inconnue"):
            if compte.get(c):
                print(f"  {c:14s}: {compte[c]}")
        print(f"  lacunes internes: {len(trous)}"
              + (f"  -> {trous[:20]}{' …' if len(trous) > 20 else ''}" if trous else ""))

    (SORTIE / "_inventaire.json").write_text(
        json.dumps(inventaire_global, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"\nInventaire écrit dans « Scans OCR/_inventaire.json ».")
    return 0


def main():
    documents = lire_declaration()
    args = sys.argv[1:]
    filtre = None
    secondes = 150
    if "--document" in args:
        filtre = args[args.index("--document") + 1]
    if "--secondes" in args:
        secondes = int(args[args.index("--secondes") + 1])

    if "--resoudre" in args:
        return phase_resoudre(documents)
    if "--ocr" in args:
        return phase_ocr(documents, filtre, secondes)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
