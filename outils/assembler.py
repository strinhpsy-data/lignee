#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assembler.py — réunit les fragments de transcription en un fichier au schéma
du projet, prêt à être dessiné.

CE FICHIER EST UN BROUILLON, et il le dit dans son titre. Il sort dans
genealogie_michel-jean_brouillon.json et NE TOUCHE JAMAIS
genealogie_jean.json : les 60 personnes de celui-là sont vérifiées à la main,
avec leurs sources et leurs huit contradictions relevées. Les 4 143 d'ici
sont lues par machine. Mélanger les deux détruirait le travail vérifié sous
une masse de données non vérifiées, et on ne saurait plus lesquelles sont
lesquelles.

IDENTIFIANTS. Chaque personne porte sa page : « xavier-devost-p133-02 ». Un
identifiant qui dit d'où vient la personne se vérifie d'un coup d'oeil.

RAPPROCHEMENTS. Le livre nomme la même personne deux fois : comme enfant dans
la fratrie de ses parents, puis comme tête de couple quand vient sa propre
descendance. On rapproche par nom replié à l'intérieur d'une fenêtre de
pages, et CHAQUE rapprochement est compté et consigné. Un rapprochement est
une hypothèse, pas une lecture : il doit rester visible et réversible.
"""

import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
FRAGMENTS = RACINE / "transcription" / "michel-jean"
SORTIE = RACINE / "genealogie_michel-jean_brouillon.json"
FENETRE = 12          # pages : au-delà, deux homonymes ne sont pas rapprochés


def replie(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


# « M. » et « J. » sont Marie et Joseph. On les développe pour que le
# rapprochement fonctionne entre « M. Thérèse » et « Marie-Thérèse ».
def cle_nom(nom):
    n = replie(nom)
    n = re.sub(r"^m\s+", "marie ", n)
    n = re.sub(r"^j\s+", "joseph ", n)
    mots = [m for m in n.split() if len(m) > 1]
    return " ".join(mots)


def slug(nom, page, rang):
    base = re.sub(r"\s+", "-", cle_nom(nom))[:46].strip("-") or "inconnu"
    return f"{base}-p{page:03d}-{rang:02d}"


def main():
    frags = sorted(FRAGMENTS.glob("p*.json"))
    if not frags:
        print("ERREUR : aucun fragment. Lancer d'abord outils/transcrire.py")
        return 2

    personnes, unions = {}, []
    unions_vues = set()
    par_cle = defaultdict(list)          # cle_nom -> [(page, id)]
    rapprochements = []
    compteur = Counter()

    def retrouve(nom, page):
        """Retrouve une personne déjà posée, sans en créer. Le report de
        pile d'une page à l'autre fait que « sous » désigne souvent un parent
        lu sur la page précédente : le chercher dans la seule page courante
        le rendait introuvable 455 fois."""
        cle = cle_nom(nom)
        for p_page, pid in reversed(par_cle.get(cle, [])):
            if abs(page - p_page) <= FENETRE:
                return pid
        return None

    def pose(nom, page, role):
        """Crée une personne, ou rend celle qu'on croit être la même."""
        cle = cle_nom(nom)
        if not cle:
            return None
        for p_page, pid in reversed(par_cle[cle]):
            if abs(page - p_page) <= FENETRE:
                rapprochements.append({"cle": cle, "page_vue": page,
                                       "page_origine": p_page, "id": pid,
                                       "role": role})
                compteur["rapprochees"] += 1
                return pid
        rang = sum(1 for _, i in par_cle[cle]) + 1
        pid = slug(nom, page, rang)
        while pid in personnes:
            rang += 1
            pid = slug(nom, page, rang)
        prenom, _, reste = nom.strip().partition(" ")
        personnes[pid] = {
            "prenom": prenom, "nom": reste.strip() or prenom,
            "nom_affiche": nom.strip(),
            "pays": "nf", "sources": [f"Michel Jean, p. {page}"],
            "_page": page, "_role": role,
        }
        par_cle[cle].append((page, pid))
        compteur["creees"] += 1
        return pid

    # ------------------------------------------------------------------
    for f in frags:
        d = json.loads(f.read_text(encoding="utf-8"))
        page = d["page"]
        vus_page = {}            # nom brut -> id, pour resoudre « sous »
        couples_page = {}        # « X & Y » -> id d'union

        for p in d["personnes"]:
            pid = pose(p["nom_brut"], page, "enfant")
            if pid is None:
                continue
            vus_page[p["nom_brut"]] = pid
            fiche = personnes[pid]
            for cle in ("naissance", "bapteme", "deces", "sepulture"):
                if cle in p and cle not in fiche:
                    fiche[cle] = {k: v for k, v in p[cle].items()
                                  if k in ("texte", "certitude", "tri", "note")}
            if p.get("generation") and "generation" not in fiche:
                fiche["generation"] = p["generation"]

            # le conjoint est une personne a son tour
            for u in p.get("unions", []):
                cj = u.get("conjoint_brut", "").strip()
                if not cj or len(cj) < 4:
                    continue
                cid = pose(cj, page, "conjoint")
                if cid is None:
                    continue
                # Le livre répète le mariage sur plusieurs lignes et
                # plusieurs pages. Sans ce garde-fou, le même conjoint
                # apparaissait trois fois à côté de la même personne.
                paire = frozenset((pid, cid))
                if paire in unions_vues:
                    continue
                unions_vues.add(paire)
                uni = {"id": f"u-{pid}-{cid}", "conjoints": [pid, cid],
                       "enfants": [], "sources": [f"Michel Jean, p. {page}"]}
                if u.get("quand"):
                    uni["mariage"] = {"texte": u["quand"],
                                      "certitude": u.get("certitude", "inconnue")}
                if u.get("lieu"):
                    uni.setdefault("notes", []).append(f"Lieu : {u['lieu']}")
                if u.get("conjoint_detail"):
                    personnes[cid].setdefault("notes", []).append(u["conjoint_detail"])
                if u.get("beaux_parents"):
                    personnes[cid].setdefault("notes", []).append(
                        "Parents : " + ", ".join(u["beaux_parents"]))
                unions.append(uni)
                compteur["unions"] += 1

        # ------- rattacher les enfants a l'union de leurs parents -------
        for p in d["personnes"]:
            pid = vus_page.get(p["nom_brut"])
            sous = p.get("sous")
            if not pid or not sous or sous == "?":
                compteur["sans parent"] += 1
                continue
            if " & " in sous:
                if sous not in couples_page:
                    a, b = [x.strip() for x in sous.split(" & ", 1)]
                    ida, idb = pose(a, page, "tete"), pose(b, page, "tete")
                    if not ida or not idb:
                        continue
                    paire = frozenset((ida, idb))
                    deja = next((u for u in unions
                                 if frozenset(u["conjoints"]) == paire), None)
                    if deja is not None:
                        couples_page[sous] = deja
                        couples_page[sous]["enfants"].append(pid)
                        compteur["rattachees"] += 1
                        continue
                    unions_vues.add(paire)
                    uni = {"id": f"u-couple-p{page:03d}-{len(couples_page)}",
                           "conjoints": [ida, idb], "enfants": [],
                           "sources": [f"Michel Jean, p. {page}"]}
                    unions.append(uni)
                    couples_page[sous] = uni
                    compteur["unions"] += 1
                couples_page[sous]["enfants"].append(pid)
                compteur["rattachees"] += 1
            else:
                parent = vus_page.get(sous) or retrouve(sous, page)
                if not parent:
                    compteur["parent introuvable"] += 1
                    continue
                # l'union du parent, ou une union a un seul conjoint
                cible = next((u for u in unions if parent in u["conjoints"]), None)
                if cible is None:
                    cible = {"id": f"u-seul-{parent}", "conjoints": [parent],
                             "enfants": [], "sources": [f"Michel Jean, p. {page}"]}
                    unions.append(cible)
                    compteur["unions"] += 1
                cible["enfants"].append(pid)
                compteur["rattachees"] += 1

    # ------------------------------------------------------------------
    # racines : les unions dont aucun conjoint n'est enfant d'une autre union
    enfant_de = {e for u in unions for e in u["enfants"]}
    racines = [u["id"] for u in unions
               if not any(c in enfant_de for c in u["conjoints"]) and u["enfants"]]
    racines.sort(key=lambda i: -len(next(u for u in unions if u["id"] == i)["enfants"]))

    detaches = [pid for pid in personnes
                if pid not in enfant_de
                and not any(pid in u["conjoints"] for u in unions)]

    data = {
        "meta": {
            "titre": "Michel Jean — transcription brute",
            "sous_titre": (f"{len(personnes)} personnes lues par machine sur 290 pages "
                           f"— BROUILLON NON VÉRIFIÉ"),
            "carte": {"actif": False, "lieux": {}, "toponymes": {}},
        },
        "problemes": [{
            "id": "brouillon", "type": "ambiguite", "gravite": "forte",
            "personnes": [], "pages": "1-290",
            "description": ("Ce fichier est une transcription automatique. "
                            f"{compteur['rapprochees']} personnes ont été rapprochées "
                            "par homonymie dans une fenêtre de 12 pages : chacune est "
                            "une hypothèse, non une lecture. Aucune donnée d'ici n'est "
                            "vérifiée sur la source.")}],
        "personnes": personnes, "unions": unions,
        "racines": racines, "detaches": [],
        "_brouillon": {
            "compteur": dict(compteur),
            "racines_candidates": len(racines),
            "detaches": len(detaches),
            "rapprochements": rapprochements[:400],
        },
    }
    SORTIE.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"personnes      : {len(personnes)}")
    print(f"unions         : {len(unions)}")
    for k, v in compteur.most_common():
        print(f"  {k:20s} {v}")
    print(f"racines candidates : {len(racines)}")
    print(f"detaches           : {len(detaches)}")
    print(f"\necrit : {SORTIE.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
