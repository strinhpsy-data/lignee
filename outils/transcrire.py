#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
transcrire.py — analyse les pages océrisées de « Michel Jean » et en tire des
fragments de données généalogiques, une page par fragment.

PRINCIPE, repris de la fiche projet : le script ordonne, le jugement reste
humain. L'analyseur n'émet que ce qu'il lit. Il ne complète pas, il ne devine
pas, il ne lisse pas. Tout ce qu'il ne reconnaît pas est conservé mot pour
mot dans un résidu, avec sa page.

C'est l'interdit numéro un à l'échelle de 5 500 personnes : une donnée
plausible mais fausse est indétectable dix ans plus tard, et à ce volume la
vigilance humaine ne suffit plus. Il faut que l'invention soit
structurellement impossible et que l'incertitude soit comptée.

TROIS GARDE-FOUS MESURABLES
  1. « 16 enfants: » suivi de 14 enfants lus — l'écart est signalé. La source
     se vérifie elle-même : le compte est écrit dans le texte. C'est aussi la
     parenthèse fermante de la grammaire, donc ce qui tient la filiation.
  2. Aucune ligne n'est jetée en silence.
  3. Chaque fait porte sa page. Rien n'entre sans provenance.

    python outils/transcrire.py --pages 131-140
    python outils/transcrire.py            (toutes les pages)
    python outils/transcrire.py --bilan
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "Scans OCR" / "michel-jean"
SORTIE = RACINE / "transcription" / "michel-jean"

# =====================================================================
# Normalisation — déterministe, chaque règle payée d'expérience
# =====================================================================

SUBSTITUTIONS = [
    (r"\{", "("),                      # l'OCR rend « ( » par « { »
    (r"\bT\.-?P\b\.?", "Trois-Pistoles"),
    (r"\bSte-Frse\b\.?", "Ste-Françoise"),
    (r"\bRiv\.-du-Loup\b", "Rivière-du-Loup"),
    (r"\bRim\b\.", "Rimouski"),
    (r"\bQué\b\.", "Québec"),
    (r"\bMtl\b\.?", "Montréal"),
]

def normalise(ligne):
    l = ligne.rstrip()
    for motif, remplacement in SUBSTITUTIONS:
        l = re.sub(motif, remplacement, l)
    # L'OCR insère des espaces dans les nombres : « 02-05-1 992 »,
    # « 10-1 1-2009 ». On ne recolle que ce qui est déjà encadré de chiffres
    # et de tirets, donc jamais deux nombres distincts.
    l = re.sub(r"\d[\d \-]{5,}\d",
               lambda m: re.sub(r"(?<=\d)[ ]+(?=\d)", "", m.group(0)), l)
    return l.strip()


# =====================================================================
# Grammaire
# =====================================================================

RE_GENERATION = re.compile(
    r"^\s*(\d+\s*[°ªeè](?:\s*,\s*\d+\s*[°ªeè])*)\s*g[ée]n[ée]rations?\s*[;:.]?\s*$", re.I)
RE_ENFANTS = re.compile(r"^\s*(\d+)\s+enfants?\b([^:]*):?\s*(.*)$", re.I)
RE_COUPLE = re.compile(
    r"^\s*([A-ZÉÈÀÎÔÛ][^;:]{2,60}?)\s+et\s+([A-ZÉÈÀÎÔÛ][^;:]{2,60}?)\s*[;:.]?\s*$")

# « M. » et « J. » devant un prénom sont Marie et Joseph, prénoms de baptême
# abrégés — ce ne sont pas des civilités.
RE_NOM = r"(?:[MJ]\.\s*)?(?:[A-ZÉÈÀÎÔÛ][\wÀ-ÿ'’\-\.]*\s*){1,6}"
RE_PERSONNE = re.compile(
    r"^\s*(?P<nom>" + RE_NOM + r")\s*,\s*"
    r"(?P<reste>(?:né|née|n\.|b\.|d\.|déc\.|s\.|sép\.|inh\.|m\.|conjoint)\b.*)$")

MARQUEURS = [("naissance", r"n(?:ée|é|\.)"), ("bapteme", r"b\."),
             ("deces", r"(?:déc|d)\."), ("sepulture", r"(?:sép|inh|s)\."),
             ("mariage", r"m\.")]
RE_COUPURE = re.compile(
    r"(?:(?<=[\s,;(])|^)(?P<quoi>" + "|".join(m for _, m in MARQUEURS) +
    r")\s+(?=le\b|en\b|à\b|vers\b|et\s+b\b|\d)", re.I)
QUOI = {"né": "naissance", "née": "naissance", "n": "naissance", "b": "bapteme",
        "d": "deces", "déc": "deces", "s": "sepulture", "sép": "sepulture",
        "inh": "sepulture", "m": "mariage"}

RE_PARENTS = re.compile(r"\bp\.\s*(?P<pere>[^,;)]+),\s*(?P<mere>[^;)]+)", re.I)
RE_ANNEE = re.compile(r"\b(1[5-9]\d\d|20[0-2]\d)\b")
RE_PIED = re.compile(r"^\s*\d{1,4}\s*[;:.]?\s*$")


def annee(t):
    m = RE_ANNEE.search(t or "")
    return int(m.group(1)) if m else None


def certitude(valeur):
    """Un fait n'est attesté que si on y lit une date complète. « née à
    Godbout » sans date, « né le 04 » sans mois : approximatif ou inconnu,
    jamais comblé."""
    if not valeur:
        return "inconnue"
    if re.search(r"\b\d{1,2}-\d{2}-\d{4}\b", valeur):
        return "attestee"
    if RE_ANNEE.search(valeur):
        return "approximative"
    return "inconnue"


def masque(texte):
    """Remplace le contenu des parenthèses par un caractère neutre, en
    gardant la longueur. Les dates d'un conjoint vivent dans sa parenthèse :
    les découper comme des faits de la personne lui attribuerait le décès de
    sa femme. C'est arrivé, et ça ne se voit pas à la relecture."""
    out, prof = [], 0
    for ch in texte:
        if ch == "(":
            prof += 1; out.append(ch)
        elif ch == ")":
            prof = max(0, prof - 1); out.append(ch)
        else:
            out.append("\u00b7" if prof else ch)
    return "".join(out)


def segments(texte):
    """Découpe un énoncé en faits étiquetés. Un fait s'arrête au marqueur
    suivant, jamais à la fin de la ligne : sinon « déc. le 23-03-1911 à 2
    ans, sép. le 25 à St-Mathieu » met la sépulture dans le décès, et les
    deux faits deviennent faux ensemble."""
    # Les points de coupe se cherchent sur le texte masqué, et se
    # appliquent au texte réel : les deux ont la même longueur.
    coupes = [(m.start(), m.group("quoi"), m.end())
              for m in RE_COUPURE.finditer(masque(texte))]
    out = []
    for i, (deb, quoi, fin) in enumerate(coupes):
        suite = coupes[i + 1][0] if i + 1 < len(coupes) else len(texte)
        etiq = QUOI.get(quoi.lower().rstrip("."))
        if etiq:
            out.append((etiq, texte[fin:suite].strip(" ,;:")))
    return out


def lire_mariage(valeur):
    """« m. le 26-06-1936 à Ste-Anne, Godbout, à Imelda Tremblay (p. …) ».
    Le lieu et le conjoint sont tous deux introduits par « à ». Le conjoint
    est le DERNIER : l'énoncé finit toujours par lui."""
    detail = None
    m = re.search(r"\(([^)]*)\)\s*[;:.]?\s*$", valeur)
    if m:
        detail = m.group(1).strip()
        valeur = valeur[:m.start()].strip(" ,;")
    bouts = re.split(r"\s+à\s+", valeur)
    u = {"quand": bouts[0].strip(" ,;") if bouts else "",
         "conjoint_brut": bouts[-1].strip(" ,;") if len(bouts) > 1 else "",
         "lieu": " à ".join(bouts[1:-1]).strip(" ,;") if len(bouts) > 2 else ""}
    u["certitude"] = certitude(u["quand"])
    if detail:
        u["conjoint_detail"] = detail
        mp = RE_PARENTS.search(detail)
        if mp:
            u["beaux_parents"] = [mp.group("pere").strip(),
                                  mp.group("mere").strip()]
    return u


def verse(p, texte):
    """Verse les faits d'un énoncé sans jamais écraser un fait déjà lu : la
    première lecture est la plus proche du nom, donc la plus sûre."""
    for etiq, valeur in segments(texte):
        if not valeur:
            continue
        if etiq == "mariage":
            p.setdefault("unions", []).append(lire_mariage(valeur))
        elif etiq not in p:
            p[etiq] = {"texte": valeur, "certitude": certitude(valeur),
                       "tri": annee(valeur)}


def completer_jour_seul(p):
    """« né le 16, b. le 17-12-1911 » : le livre n'écrit le mois et l'année
    qu'une fois, sur le baptême. Le jour seul de la naissance les emprunte
    donc au baptême qui suit immédiatement.

    C'est une DÉDUCTION, pas une lecture : elle est marquée comme telle, et
    elle reste réversible puisque le texte d'origine est conservé. On ne la
    fait que si le baptême porte une date complète et la naissance un seul
    nombre — jamais autrement."""
    n, b = p.get("naissance"), p.get("bapteme")
    if not n or not b or n["certitude"] == "attestee":
        return
    jour = re.fullmatch(r"(?:le\s+)?(\d{1,2})", n["texte"].strip(" ,;"))
    plein = re.search(r"\b(\d{1,2})-(\d{2})-(\d{4})\b", b["texte"])
    if not (jour and plein):
        return
    p["naissance"] = {
        "texte": f"{int(jour.group(1)):02d}-{plein.group(2)}-{plein.group(3)}",
        "certitude": "deduite", "tri": int(plein.group(3)),
        "note": f"jour lu « {n['texte']} » ; mois et année empruntés au baptême"}


def assembler(lignes):
    """Recolle les lignes coupées avant toute analyse. L'OCR coupe au milieu
    d'une parenthèse de filiation et au milieu des mots (« Lau-/rette »).
    Une ligne dont la précédente laisse une parenthèse ouverte en est la
    suite : c'est le signal le plus sûr, et il ne se trompe pas."""
    out = []
    for brute in lignes:
        l = normalise(brute)
        if not l or len(l) < 2 or RE_PIED.match(l):
            continue
        if out:
            prec = out[-1]
            if prec.endswith("-") and re.match(r"^[a-zàâéèêëîïôöùûüç]", l):
                out[-1] = prec[:-1] + l
                continue
            if prec.count("(") > prec.count(")"):
                out[-1] = prec + " " + l
                continue
            if not prec.endswith(";") and not re.match(
                    r"^\s*(?:" + RE_NOM + r"\s*(?:,|et\s+[A-ZÉÈÀÎÔÛ])|"
                    r"\d+\s*[°ªeè].*g[ée]n[ée]rat|\d+\s+enfants?\b|"
                    r"(?:né|née|b\.|d\.|déc\.|s\.|sép\.|inh\.|m\.|et|conjoint|p\.))", l):
                out[-1] = prec + " " + l
                continue
        out.append(l)
    return out


def analyser_page(numero):
    chemin = SOURCE / f"p{numero:03d}.txt"
    if not chemin.exists():
        return None
    brut = [l for l in chemin.read_text(encoding="utf-8").splitlines()
            if not l.startswith("#")]

    personnes, residu, annonces = [], [], []
    generation, couple, courante = None, None, None
    pile = []

    def depile():
        # Le compte annoncé referme le niveau. Sans ça, la fratrie suivante
        # devient la descendance de son aîné : une filiation inventée, et
        # l'interdit numéro un tombe en silence.
        while pile and pile[-1]["lus"] >= pile[-1]["annonce"]:
            pile.pop()

    for l in assembler(brut):
        m = RE_GENERATION.match(l)
        if m:
            generation = m.group(1).strip()
            courante = None
            continue

        mp = RE_PERSONNE.match(l)
        me = RE_ENFANTS.match(l)
        if me and not mp:
            niveau = {"annonce": int(me.group(1)), "lus": 0, "page": numero,
                      "precision": me.group(2).strip(" ,;:"),
                      "parent": courante["nom_brut"] if courante else (couple or "?")}
            annonces.append(niveau)
            pile.append(niveau)
            suite = me.group(3).strip()
            ms = RE_PERSONNE.match(suite) if suite else None
            if ms:
                courante = {"nom_brut": ms.group("nom").strip().rstrip(","),
                            "page": numero, "generation": generation,
                            "sous": niveau["parent"], "lignes": [ms.group("reste")]}
                verse(courante, ms.group("reste"))
                niveau["lus"] += 1
                personnes.append(courante)
                depile()
            continue

        if mp:
            courante = {"nom_brut": mp.group("nom").strip().rstrip(","),
                        "page": numero, "generation": generation,
                        "lignes": [mp.group("reste")]}
            verse(courante, mp.group("reste"))
            if pile:
                courante["sous"] = pile[-1]["parent"]
                pile[-1]["lus"] += 1
                personnes.append(courante)
                depile()
            else:
                courante["sous"] = couple
                personnes.append(courante)
            continue

        mc = RE_COUPLE.match(l)
        if mc:
            couple = f"{mc.group(1).strip()} & {mc.group(2).strip()}"
            pile, courante = [], None
            continue

        if courante is not None and re.match(
                r"^\s*(?:m\.|d\.|déc\.|s\.|sép\.|inh\.|et\b|conjoint|p\.|\()", l, re.I):
            courante["lignes"].append(l)
            verse(courante, l)
            continue

        residu.append(l)

    for p in personnes:
        completer_jour_seul(p)
    ecarts = [a for a in annonces if a["lus"] != a["annonce"]]
    return {"page": numero, "generation": generation, "personnes": personnes,
            "residu": residu, "comptes_annonces": annonces,
            "ecarts_de_compte": ecarts}


def plage(expr):
    out = []
    for bout in expr.split(","):
        bout = bout.strip()
        if "-" in bout:
            a, b = bout.split("-"); out.extend(range(int(a), int(b) + 1))
        elif bout:
            out.append(int(bout))
    return out


def bilan():
    frag = sorted(SORTIE.glob("p*.json"))
    tp = tr = 0
    cert, ec = Counter(), []
    for f in frag:
        d = json.loads(f.read_text(encoding="utf-8"))
        tp += len(d["personnes"]); tr += len(d["residu"])
        ec.extend(d["ecarts_de_compte"])
        for p in d["personnes"]:
            for cle in ("naissance", "bapteme", "deces", "sepulture"):
                if cle in p:
                    cert[p[cle]["certitude"]] += 1
    annonces = sum(len(json.loads(f.read_text(encoding='utf-8'))["comptes_annonces"])
                   for f in frag)
    print(f"pages analysées   : {len(frag)}")
    print(f"personnes lues    : {tp}")
    print(f"lignes en résidu  : {tr}")
    print(f"comptes annoncés  : {annonces}")
    print(f"écarts de compte  : {len(ec)}"
          + (f"  ({100 * len(ec) // max(annonces, 1)} %)" if annonces else ""))
    print(f"faits datés       : {dict(cert)}")
    return 0


def main():
    args = sys.argv[1:]
    SORTIE.mkdir(parents=True, exist_ok=True)
    if "--bilan" in args:
        return bilan()
    pages = plage(args[args.index("--pages") + 1]) if "--pages" in args else \
        [int(f.stem[1:]) for f in sorted(SOURCE.glob("p[0-9][0-9][0-9].txt"))]
    tp = tr = 0
    for n in pages:
        r = analyser_page(n)
        if r is None:
            continue
        (SORTIE / f"p{n:03d}.json").write_text(
            json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        tp += len(r["personnes"]); tr += len(r["residu"])
    print(f"{len(pages)} pages — {tp} personnes lues, {tr} lignes en résidu")
    return 0


if __name__ == "__main__":
    sys.exit(main())
