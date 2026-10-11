#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contrôle de l'arbre généalogique — à passer avant de déclarer un travail terminé.

Usage :
    python verifier.py                    -> contrôle genealogie_jean.json
    python verifier.py mon_fichier.json   -> contrôle le fichier indiqué
    python verifier.py --sans-navigateur  -> saute la couche navigateur
    (ou double-clic sur Verifier.bat)

Deux couches :
  A. Contrôles de données et de génération — aucune dépendance, tournent partout.
  B. Contrôles de navigateur — exigent Playwright. Sautés proprement s'il manque.

Sort avec un code non nul dès qu'un contrôle échoue. C'est ce code que lit
Verifier.bat, et c'est lui qui fait foi : un travail n'est pas terminé tant
qu'il n'est pas à zéro.
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent   # le contrat vit dans tests/
CERTITUDES = {"attestee", "approximative", "deduite", "divergente", "incoherente", "inconnue"}

ok_total, ko_total, sautes = 0, 0, 0
_echecs = []
_vus = set()


def controle(code, nom, condition, detail=""):
    """Un contrôle du contrat. `code` est son identifiant T-xx, stable dans le
    temps : c'est lui que cite le journal, jamais le libellé."""
    global ok_total, ko_total
    if code in _vus:
        print(f"  !!!!  le code {code} sert deux fois — numérotation à reprendre")
    _vus.add(code)
    if condition:
        ok_total += 1
        print(f"  OK    {code}  {nom}")
    else:
        ko_total += 1
        _echecs.append((code, nom, detail))
        print(f"  ECHEC {code}  {nom}")
        if detail:
            for ligne in str(detail).splitlines()[:12]:
                print(f"        {ligne}")


def saut(nom, raison):
    global sautes
    sautes += 1
    print(f"  SAUTE {nom} — {raison}")


def verifier_empreinte():
    """Règle 4 du protocole : les tests sont intouchables par Qwen.
    Seul Claude repose l'empreinte, après une modification délibérée."""
    import hashlib
    dossier = Path(__file__).resolve().parent
    ref = dossier / "EMPREINTE.txt"
    if not ref.exists():
        print("  !!!!  tests/EMPREINTE.txt absent — le contrat n'est pas scellé")
        return True
    ecarts = []
    for ligne in ref.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#"):
            continue
        attendu, _, nom = ligne.partition("  ")
        f = dossier / nom.strip()
        if not f.exists():
            ecarts.append(f"{nom.strip()} : ABSENT")
        elif hashlib.sha256(f.read_bytes()).hexdigest() != attendu.strip():
            ecarts.append(f"{nom.strip()} : MODIFIE")
    if ecarts:
        print("\n" + "!" * 62)
        print("  LE CONTRAT A ETE MODIFIE — les resultats ne valent rien.")
        for e in ecarts:
            print(f"    {e}")
        print("")
        print("  Un test qu'on retouche pour le faire passer n'est pas un test.")
        print("  Retablissez les fichiers, ou demandez a Claude de reposer")
        print("  l'empreinte si la modification est voulue.")
        print("!" * 62 + "\n")
        return False
    return True


def titre(t):
    print(f"\n{t}\n{'-' * len(t)}")


# =====================================================================
# A. DONNÉES
# =====================================================================
def controler_donnees(chemin):
    titre("A1. Le fichier de données")

    try:
        brut = chemin.read_text(encoding="utf-8")
    except Exception as e:
        controle("T-01", "le fichier se lit", False, str(e))
        return None
    controle("T-01", "le fichier se lit", True)

    try:
        d = json.loads(brut)
        controle("T-03", "le JSON est bien formé", True)
    except json.JSONDecodeError as e:
        controle("T-04", "le JSON est bien formé", False,
                 f"ligne {e.lineno}, colonne {e.colno} : {e.msg}")
        return None

    for code, cle in (("T-35", "personnes"), ("T-36", "unions")):
        controle(code, f"la clé « {cle} » existe", cle in d)
    if "personnes" not in d or "unions" not in d:
        return None

    P, U = d["personnes"], d["unions"]

    titre("A2. Cohérence du graphe")

    inconnus = []
    for u in U:
        for c in u.get("conjoints", []):
            if c not in P:
                inconnus.append(f"union {u.get('id','?')} : conjoint « {c} » inconnu")
        for e in u.get("enfants", []):
            if e not in P:
                inconnus.append(f"union {u.get('id','?')} : enfant « {e} » inconnu")
    controle("T-05", "toute personne citée dans une union existe", not inconnus, "\n".join(inconnus))

    doubles = []
    vus = {}
    for u in U:
        for e in u.get("enfants", []):
            if e in vus:
                doubles.append(f"« {e} » est enfant de {vus[e]} ET de {u.get('id','?')}")
            vus[e] = u.get("id", "?")
    controle("T-06", "aucune personne n'a deux couples de parents", not doubles, "\n".join(doubles))

    auto = [u.get("id", "?") for u in U
            if set(u.get("conjoints", [])) & set(u.get("enfants", []))]
    controle("T-07", "personne n'est son propre parent", not auto, "\n".join(auto))

    # cycles : on remonte la filiation depuis chaque personne
    parent_de = {}
    for u in U:
        for e in u.get("enfants", []):
            parent_de[e] = u.get("conjoints", [])
    cycles = []
    for depart in P:
        vu, courant, profondeur = {depart}, [depart], 0
        while courant and profondeur < 60:
            suivant = []
            for x in courant:
                for p in parent_de.get(x, []):
                    if p == depart:
                        cycles.append(depart)
                        suivant = []
                        break
                    if p not in vu:
                        vu.add(p)
                        suivant.append(p)
            courant = suivant
            profondeur += 1
    controle("T-08", "aucun cycle dans la filiation", not cycles, ", ".join(sorted(set(cycles))))

    racines = d.get("racines", [])
    ids_unions = {u.get("id") for u in U}
    absentes = [r for r in racines if r not in ids_unions]
    controle("T-09", "les racines désignent des unions existantes", not absentes, ", ".join(absentes))
    controle("T-10", "au moins une racine est déclarée", bool(racines) or bool(d.get("detaches")))

    detaches = [x for x in d.get("detaches", []) if x not in P]
    controle("T-11", "les nœuds détachés existent", not detaches, ", ".join(detaches))

    titre("A3. Qualité des faits")

    mauvaises = []
    for pid, p in P.items():
        for cle in ("naissance", "bapteme", "deces", "sepulture"):
            f = p.get(cle)
            if isinstance(f, dict) and f.get("certitude") and f["certitude"] not in CERTITUDES:
                mauvaises.append(f"{pid}.{cle} : « {f['certitude'] }»")
        for s in p.get("sections", []) or []:
            if s.get("type") == "faits":
                for e in s.get("contenu", []) or []:
                    if e.get("certitude") and e["certitude"] not in CERTITUDES:
                        mauvaises.append(f"{pid}, section « {s.get('titre','?')} » : « {e['certitude']} »")
    controle("T-12", "tout niveau de certitude est dans la liste permise", not mauvaises,
             "\n".join(mauvaises) + ("\n        permis : " + ", ".join(sorted(CERTITUDES)) if mauvaises else ""))

    sans_src = [pid for pid, p in P.items() if not p.get("sources")]
    controle("T-13", "toute personne porte au moins une source", not sans_src,
             f"{len(sans_src)} sans source : " + ", ".join(sorted(sans_src)[:8]))

    pb_inconnus = []
    for x in d.get("problemes", []):
        for who in x.get("personnes", []) or []:
            if who not in P:
                pb_inconnus.append(f"problème {x.get('id','?')} vise « {who} », inconnu")
    controle("T-14", "les points à vérifier visent des personnes existantes", not pb_inconnus,
             "\n".join(pb_inconnus))

    titre("A4. Table cartographique")

    carte = (d.get("meta") or {}).get("carte") or {}
    if not carte:
        saut("table cartographique", "aucune table meta.carte déclarée")
    else:
        table = carte.get("lieux") or {}
        employes = {l for p in P.values() for l in (p.get("lieux") or [])}
        hors = sorted(employes - set(table))
        controle("T-15", "tout lieu employé figure dans la table", not hors,
                 f"{len(hors)} hors table (lien construit au jugé) : " + " | ".join(hors[:6]))
        vides = [k for k, v in {**table, **(carte.get("toponymes") or {})}.items() if not v]
        print(f"  NOTE  {len(vides)} entrée(s) volontairement sans lien : " + ", ".join(vides[:8]))

    return d


# =====================================================================
# B. GÉNÉRATION
# =====================================================================
def controler_generation(chemin, d):
    titre("B1. Le générateur s'exécute")

    gen = RACINE / "src" / "generer_arbre.py"
    if not gen.exists():
        controle("T-16", "src/generer_arbre.py est présent", False, str(gen))
        return None
    controle("T-17", "src/generer_arbre.py est présent", True)

    base = chemin.stem.replace("genealogie_", "arbre_")
    sortie = chemin.with_name(base + ".html")
    dossier = chemin.with_name(base + "_fiches")

    # témoin : un fichier étranger ne doit pas être supprimé
    temoin = dossier / "_temoin_verification.txt"
    dossier.mkdir(exist_ok=True)
    temoin.write_text("ne pas supprimer", encoding="utf-8")

    t0 = time.time()
    r = subprocess.run([sys.executable, "-I", str(gen), str(chemin)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    duree = time.time() - t0
    controle("T-18", "le générateur sort sans erreur",
             r.returncode == 0, (r.stderr or r.stdout or "").strip())
    if r.returncode != 0:
        return None
    print(f"  NOTE  généré en {duree:.1f} s")

    controle("T-19", "le générateur ne supprime aucun fichier étranger", temoin.exists(),
             "le témoin _temoin_verification.txt a disparu")
    if temoin.exists():
        try:
            temoin.unlink()
        except OSError:
            pass  # suppression bloquée : sans conséquence ici

    titre("B2. Les fichiers produits")

    controle("T-20", "l'arbre est produit", sortie.exists(), str(sortie))
    if not sortie.exists():
        return None
    taille = sortie.stat().st_size
    controle("T-21", "l'arbre n'est pas vide", taille > 20_000, f"{taille} octets")

    html = sortie.read_text(encoding="utf-8")
    controle("T-22", "le gabarit est entièrement rempli",
             "__DONNEES__" not in html and "__TITRE__" not in html
             and "__DOSSIER_FICHES__" not in html,
             "un marque-place __…__ subsiste dans la sortie")

    P = d["personnes"]
    manquantes = [pid for pid in P if not (dossier / f"{pid}.html").exists()]
    controle("T-23", "chaque personne a sa page", not manquantes,
             f"{len(manquantes)} manquantes : " + ", ".join(manquantes[:8]))

    titre("B3. Les liens internes")

    casses = []
    for pid in P:
        f = dossier / f"{pid}.html"
        if not f.exists():
            continue
        t = f.read_text(encoding="utf-8")
        for cible in re.findall(r'href="([^":#?]+\.html)"', t):
            if cible.startswith("../"):
                if not (dossier.parent / cible[3:]).exists():
                    casses.append(f"{pid}.html -> {cible}")
            elif not (dossier / cible).exists():
                casses.append(f"{pid}.html -> {cible}")
    controle("T-24", "aucun lien entre pages ne pointe dans le vide", not casses,
             f"{len(casses)} cassés : " + " | ".join(casses[:6]))

    lien_fiche = re.search(r'href="([^"]*_fiches)/\$\{encodeURIComponent', html)
    controle("T-25", "l'arbre pointe vers le bon dossier de fiches",
             bool(lien_fiche) and lien_fiche.group(1) == dossier.name,
             f"attendu « {dossier.name} », trouvé « {lien_fiche.group(1) if lien_fiche else 'rien'} »")

    return sortie


# =====================================================================
# C. CONFIDENTIALITÉ
# =====================================================================
def controler_confidentialite(chemin, d):
    titre("C. Version partageable")

    P = d["personnes"]
    secrets = []
    for p in P.values():
        for s in p.get("sections", []) or []:
            if s.get("prive"):
                c = s.get("contenu")
                morceaux = c if isinstance(c, list) else [c]
                for m in morceaux:
                    if isinstance(m, str) and len(m) > 30:
                        secrets.append(m[:60])
                if s.get("titre"):
                    secrets.append(s["titre"])
    if not secrets:
        saut("version partageable", "aucune section confidentielle dans ce jeu de données")
        return

    gen = RACINE / "src" / "generer_arbre.py"
    r = subprocess.run([sys.executable, "-I", str(gen), str(chemin), "--partage"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    controle("T-26", "la version partageable se génère", r.returncode == 0,
             (r.stderr or "").strip())
    if r.returncode != 0:
        return

    base = chemin.stem.replace("genealogie_", "arbre_") + "_partage"
    cible = chemin.with_name(base + ".html")
    dossier = chemin.with_name(base + "_fiches")

    corpus = cible.read_text(encoding="utf-8") if cible.exists() else ""
    for f in dossier.glob("*.html"):
        corpus += f.read_text(encoding="utf-8")

    fuites = [s for s in secrets if s and s in corpus]
    controle("T-27", "AUCUN contenu confidentiel dans la version partageable", not fuites,
             f"{len(fuites)} fuite(s) : " + " | ".join(x[:50] for x in fuites[:4]))


# =====================================================================
# D. NAVIGATEUR
# =====================================================================
def controler_navigateur(sortie, d):
    titre("D. Comportement réel dans un navigateur")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        saut("couche navigateur", "Playwright absent — voir DOC/SPECIFICATION.md")
        return

    P = d["personnes"]
    cible = next((k for k, v in P.items() if v.get("ancetre")), None) or next(iter(P))

    erreurs = []
    try:
        with sync_playwright() as pw:
            # Sur Wilfred, le Chromium de Playwright n'est pas installé (150 Mo
            # de téléchargement impossible hors ligne). On se rabat sur le Edge
            # livré avec Windows, qui fait le même travail.
            nav, voie = None, None
            for essai in (None, "msedge", "chrome"):
                try:
                    nav = pw.chromium.launch(channel=essai) if essai else pw.chromium.launch()
                    voie = essai or "chromium fourni"
                    break
                except Exception:
                    continue
            if nav is None:
                saut("couche navigateur",
                     "aucun navigateur pilotable — ni Chromium Playwright, ni Edge, ni Chrome")
                return
            print(f"  NOTE  navigateur employé : {voie}")
            page = nav.new_page(viewport={"width": 1400, "height": 900})
            page.on("pageerror", lambda e: erreurs.append(str(e)))
            page.on("console", lambda m: erreurs.append(m.text) if m.type == "error" else None)
            page.goto(sortie.as_uri())
            page.wait_for_timeout(1200)

            controle("T-28", "la page se charge sans erreur JavaScript", not erreurs,
                     "\n".join(erreurs[:5]))

            puces = page.eval_on_selector_all(".puce", "a=>a.length")
            controle("T-29", "les médaillons sont dessinés", puces > 0, f"{puces} dessinés")

            # VRAI clic : un événement simulé ne prouve rien, il contourne
            # justement les mécanismes (capture de pointeur) qui cassent le clic.
            page.evaluate("id=>centrer(id)", cible)
            page.wait_for_timeout(300)
            page.locator(f'[data-id="{cible}"]').click()
            page.wait_for_timeout(400)
            controle("T-30", "un clic réel sur un médaillon ouvre la fiche",
                     page.is_visible("#fiche"), f"cible : {cible}")

            if page.is_visible("#fiche"):
                href = page.get_attribute("#fiche .f-plus", "href")
                controle("T-31", "la fiche porte un lien « En savoir plus »", bool(href))
                if href:
                    f = (sortie.parent / href).resolve()
                    controle("T-32", "ce lien mène à un fichier existant", f.exists(), str(f))

                page.mouse.move(120, 840)
                page.mouse.down()
                page.mouse.move(300, 860, steps=10)
                page.mouse.up()
                page.wait_for_timeout(300)
                controle("T-33", "un glissement referme la fiche", not page.is_visible("#fiche"))

            nav.close()
    except Exception as e:
        controle("T-34", "la couche navigateur s'exécute", False, f"{type(e).__name__}: {e}")


# =====================================================================
def une_passe(chemin, sans_nav):
    print("\n" + "=" * 62)
    print(f"  JEU DE DONNÉES — {chemin.name}")
    print("=" * 62)
    if not chemin.exists():
        print(f"\nERREUR : fichier introuvable -> {chemin}")
        return False
    d = controler_donnees(chemin)
    if d is None:
        print("\nLes données ne tiennent pas : le reste n'a pas été contrôlé.")
        return False
    sortie = controler_generation(chemin, d)
    controler_confidentialite(chemin, d)
    if sortie and not sans_nav:
        controler_navigateur(sortie, d)
    elif sans_nav:
        saut("couche navigateur", "écartée par --sans-navigateur")
    return True


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sans_nav = "--sans-navigateur" in sys.argv

    print("=" * 62)
    print("  CONTRAT DE VÉRIFICATION — arbre généalogique")
    print("=" * 62)

    if not verifier_empreinte():
        return 3

    # Sans argument : on éprouve les jeux d'exemple du dépôt, jamais les
    # données personnelles. Un test qui dépend d'un fichier privé n'est
    # ni partageable ni rejouable.
    if args:
        jeux = [Path(args[0]).resolve()]
    else:
        jeux = sorted((RACINE / "tests" / "donnees").glob("*.json"))
        if not jeux:
            print("\nERREUR : aucun jeu d'exemple dans tests/donnees/")
            return 2

    for j in jeux:
        une_passe(j, sans_nav)

    print("\n" + "=" * 62)
    print(f"  TOTAL — {ok_total} réussis · {ko_total} échoués · {sautes} sautés")
    print(f"  sur {len(jeux)} jeu(x) de données")
    print("=" * 62)
    if ko_total:
        print("\nÉCHECS À REPRENDRE :")
        for code, nom, _ in _echecs:
            print(f"  - {code}  {nom}")
        print("\nLe travail n'est pas terminé. Après trois tentatives")
        print("infructueuses sur un même contrôle, déclarez un blocage B-xx")
        print("et lancez Collecter_Panne.bat.")
    else:
        print("\nTout est au vert.")
    return 1 if ko_total else 0


if __name__ == "__main__":
    sys.exit(main())
