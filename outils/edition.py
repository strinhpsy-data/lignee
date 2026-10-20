#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
edition.py — les modifications faites directement depuis une fiche servie.

POURQUOI UN MODULE À PART. Le serveur reçoit une demande (« changer la date
de naissance », « retirer cette photo »), et c'est ici qu'on décide si elle
est permise, qu'on l'applique aux données et qu'on garde trace de ce qui
était là avant. Le serveur ne fait que transporter ; les règles vivent ici,
où on peut les éprouver sans navigateur.

LES TROIS RÈGLES (C-021)
  1. Rien ne se perd. Toute valeur remplacée ou retirée est consignée dans
     historique/<fichier de données>, avec la date, l'auteur (« admin » ou
     non) et le motif. Une photo retirée est DÉPLACÉE dans photos/_retirees/,
     un ancien portrait dans photos/_anciens_portraits/ — jamais effacée
     (interdit 2). L'historique vit hors du fichier de données : il ne part
     donc dans aucun export.
  2. Un fait attesté ne se remplace qu'en mode administrateur. Une saisie à
     la main ne vaut pas une source ; quand la source a été mal lue, c'est
     l'administrateur qui tranche, et l'ancienne lecture reste consignée.
  3. Retirer : ce que l'interface a ajouté se retire librement (c'est le
     défaut D-2 : une recette vide créée par erreur doit pouvoir partir).
     Ce qui vient des sources ne se retire qu'en mode administrateur, et
     reste restaurable.

Bibliothèque standard seule.
"""

import base64
import json
import re
import secrets
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PHOTOS = RACINE / "photos"
HISTORIQUE = RACINE / "historique"
RETIREES = PHOTOS / "_retirees"
ANCIENS = PHOTOS / "_anciens_portraits"

CERTITUDES = ("attestee", "approximative", "deduite", "divergente", "incoherente", "inconnue")
FAITS = ("naissance", "bapteme", "deces", "sepulture")
NOMS = ("prenom", "nom", "nom_affiche")          # administrateur seulement
CHAMPS_LIBRES = ("surnom",)
LISTES = ("variantes", "metiers", "lieux", "notes", "marquants")
EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff")
MIME = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
        "image/gif": ".gif", "image/bmp": ".bmp", "image/tiff": ".tif"}
NOM_SOURCE = re.compile(r"^genealogie_[A-Za-z0-9_-]+\.json$")


class Refus(Exception):
    """Une demande qu'on n'applique pas, avec la raison à montrer."""


# ---------------------------------------------------------------------
# outils
# ---------------------------------------------------------------------
def maintenant():
    return datetime.now().isoformat(timespec="seconds")


def annee(texte):
    m = re.search(r"\b(1[0-9]\d\d|20\d\d)\b", texte or "")
    return int(m.group(1)) if m else None


def certitude_devinee(texte):
    """Même lecture que appliquer_ajouts : une date complète vaut attestée,
    une année seule approximative, le reste inconnu."""
    if re.search(r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{4}\b", texte or ""):
        return "attestee"
    if annee(texte):
        return "approximative"
    return "inconnue"


def texte_propre(v, maxi=20000):
    if v is None:
        return ""
    if not isinstance(v, str):
        raise Refus("valeur attendue : du texte")
    v = v.replace("\r\n", "\n").strip()
    if len(v) > maxi:
        raise Refus(f"texte trop long ({len(v)} caractères)")
    return v


def chemin_source(nom):
    """Le fichier de données visé, vérifié. Le nom vient de la page ; on ne
    le suit que s'il a exactement la forme d'un fichier du projet."""
    if not isinstance(nom, str) or not NOM_SOURCE.match(nom):
        raise Refus("fichier de données absent ou douteux")
    if "brouillon" in nom:
        raise Refus("un brouillon se refabrique avec outils/assembler.py : "
                    "une modification faite ici serait perdue au prochain assemblage")
    f = RACINE / nom
    if not f.exists():
        raise Refus(f"{nom} n'existe pas dans le projet")
    return f


def decoder_image(url):
    m = re.match(r"data:([^;,]+);base64,(.*)$", url or "", re.S)
    if not m:
        raise Refus("image illisible")
    try:
        octets = base64.b64decode(m.group(2), validate=False)
    except Exception:
        raise Refus("image illisible")
    if not octets:
        raise Refus("image vide")
    return MIME.get(m.group(1).lower(), ".jpg"), octets


def portrait_actuel(pid, p):
    if p.get("photo"):
        for base in (PHOTOS, RACINE):
            f = base / p["photo"]
            if f.exists():
                return f
        return None
    for e in EXTENSIONS:
        f = PHOTOS / (pid + e)
        if f.exists():
            return f
    return None


def photos_galerie(pid):
    """Les photos de galerie d'une personne : « <id>-<n>.<ext> », en ordre
    numérique. Même convention que appliquer_ajouts (le nom nu est réservé
    au portrait)."""
    motif = re.compile(re.escape(pid) + r"-(\d+)(\.[A-Za-z]+)$")
    trouvees = []
    if PHOTOS.exists():
        for f in PHOTOS.iterdir():
            m = motif.match(f.name)
            if m and f.suffix.lower() in EXTENSIONS and f.is_file():
                trouvees.append((int(m.group(1)), f.name))
    return [n for _, n in sorted(trouvees)]


def place_libre(dossier, nom):
    """Un nom libre dans « dossier », sans jamais en écraser un autre."""
    dossier.mkdir(parents=True, exist_ok=True)
    cible = dossier / nom
    if not cible.exists():
        return cible
    tige, ext = Path(nom).stem, Path(nom).suffix
    for n in range(2, 10000):
        c = dossier / f"{tige}~{n}{ext}"
        if not c.exists():
            return c
    raise Refus("trop de fichiers du même nom dans " + dossier.name)


def est_recette(s):
    return bool(s.get("recette")) or str(s.get("titre", "")).startswith("Recette — ")


def titre_recette(s):
    t = str(s.get("titre", ""))
    return t[len("Recette — "):] if t.startswith("Recette — ") else t


# ---------------------------------------------------------------------
# l'historique
# ---------------------------------------------------------------------
class Historique:
    """historique/<fichier de données> : une liste d'entrées, jamais
    raccourcie. Chaque entrée dit ce qui était là avant ; c'est ce qui rend
    toute modification et tout retrait réversibles."""

    def __init__(self, source: Path):
        self.f = HISTORIQUE / source.name
        try:
            self.d = json.loads(self.f.read_text(encoding="utf-8"))
        except Exception:
            self.d = {"entrees": []}
        self.d.setdefault("entrees", [])

    def noter(self, **e):
        e["n"] = max([x.get("n", 0) for x in self.d["entrees"]] + [0]) + 1
        e["date"] = maintenant()
        self.d["entrees"].append(e)
        return e

    def ajoute_par_interface(self, pid, champ, valeur):
        """Cette valeur a-t-elle été AJOUTÉE par l'interface (et pas lue dans
        une source) ? Sert à permettre son retrait sans administrateur."""
        for e in reversed(self.d["entrees"]):
            if e.get("pid") == pid and e.get("champ") == champ and e.get("nouveau") == valeur:
                return e.get("action") == "ajout"
        return False

    def entree(self, n):
        for e in self.d["entrees"]:
            if e.get("n") == n:
                return e
        raise Refus(f"entrée {n} introuvable dans l'historique")

    def pour(self, pid):
        return [e for e in self.d["entrees"]
                if e.get("pid") == pid or pid in (e.get("personnes") or [])]

    def texte(self):
        return json.dumps(self.d, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------------
# les opérations
# ---------------------------------------------------------------------
def _personne(d, pid):
    if not isinstance(pid, str) or pid not in d.get("personnes", {}):
        raise Refus(f"« {pid} » ne figure pas dans ce fichier de données")
    return d["personnes"][pid]


def _admin_requis(admin, quoi):
    if not admin:
        raise Refus(quoi + " — réservé au mode administrateur")


def op_fait(d, h, a, admin):
    pid, cle = a.get("pid"), a.get("cle")
    p = _personne(d, pid)
    if cle not in FAITS:
        raise Refus(f"fait inconnu : {cle}")
    texte = texte_propre(a.get("texte"), 500)
    ancien = p.get(cle)
    if ancien and ancien.get("certitude") == "attestee":
        _admin_requis(admin, f"« {ancien.get('texte')} » est attesté par la source ; "
                             "le remplacer")
    if not texte:
        # Une saisie vide n'efface pas (défaut D-1). Retirer est un geste
        # à part, et il passe par la règle des retraits.
        raise Refus("saisie vide : rien n'a été changé (pour retirer, utilisez « Retirer »)")
    cert = a.get("certitude") or certitude_devinee(texte)
    if cert not in CERTITUDES:
        raise Refus(f"niveau de certitude inconnu : {cert}")
    nouveau = {"texte": texte, "certitude": cert}
    if annee(texte):
        nouveau["tri"] = annee(texte)
    note = texte_propre(a.get("note"), 1000)
    if note:
        nouveau["note"] = note
    elif ancien and ancien.get("note") and ancien.get("texte") == texte:
        nouveau["note"] = ancien["note"]
    if ancien == nouveau:
        return "rien à changer"
    p[cle] = nouveau
    h.noter(pid=pid, champ=cle, action="modification" if ancien else "ajout",
            ancien=ancien, nouveau=nouveau, admin=admin, motif=a.get("motif"))
    return "fait enregistré"


def op_champ(d, h, a, admin):
    pid, cle = a.get("pid"), a.get("cle")
    p = _personne(d, pid)
    if cle not in NOMS + CHAMPS_LIBRES:
        raise Refus(f"champ inconnu : {cle}")
    if cle in NOMS:
        _admin_requis(admin, "changer un nom lu dans les sources")
    v = texte_propre(a.get("valeur"), 300)
    ancien = p.get(cle)
    if not v:
        raise Refus("saisie vide : rien n'a été changé (pour retirer, utilisez « Retirer »)")
    if v == ancien:
        return "rien à changer"
    p[cle] = v
    h.noter(pid=pid, champ=cle, action="modification" if ancien else "ajout",
            ancien=ancien, nouveau=v, admin=admin, motif=a.get("motif"))
    return "enregistré"


def op_liste(d, h, a, admin):
    pid, champ = a.get("pid"), a.get("champ")
    p = _personne(d, pid)
    if champ not in LISTES:
        raise Refus(f"liste inconnue : {champ}")
    liste = p.setdefault(champ, [])
    i = a.get("index")
    v = texte_propre(a.get("valeur"), 4000)
    if i is None:
        if not v:
            raise Refus("saisie vide : rien n'a été ajouté")
        liste.append(v)
        if champ == "lieux":
            _inscrire_lieu(d, v)
        h.noter(pid=pid, champ=champ, action="ajout", ancien=None, nouveau=v, admin=admin)
        return "ajouté"
    if not isinstance(i, int) or not 0 <= i < len(liste):
        raise Refus("élément introuvable — la page est peut-être périmée ; rechargez-la")
    ancien = liste[i]
    if a.get("attendu") is not None and a.get("attendu") != ancien:
        raise Refus("cet élément a changé depuis l'ouverture de la page ; rechargez-la")
    if not v:
        raise Refus("saisie vide : rien n'a été changé (pour retirer, utilisez « Retirer »)")
    if v == ancien:
        return "rien à changer"
    liste[i] = v
    if champ == "lieux":
        _inscrire_lieu(d, v)
    h.noter(pid=pid, champ=champ, action="modification", ancien=ancien, nouveau=v,
            admin=admin, index=i, motif=a.get("motif"))
    return "enregistré"


def _inscrire_lieu(d, lieu):
    """Un lieu ajouté entre dans la table cartographique, sinon son lien
    serait construit au jugé (contrôle T-15)."""
    carte = (d.get("meta") or {}).get("carte")
    if isinstance(carte, dict):
        table = carte.setdefault("lieux", {})
        if lieu not in table:
            q = re.sub(r"\([^)]*\)", " ", lieu)
            table[lieu] = re.sub(r"\s{2,}", " ", q).strip(" ,;")


def op_portrait(d, h, a, admin, source):
    pid = a.get("pid")
    p = _personne(d, pid)
    ext, octets = decoder_image(a.get("donnee"))
    PHOTOS.mkdir(exist_ok=True)
    ancien = portrait_actuel(pid, p)
    deplace = None
    if ancien is not None:
        # L'ancien visage n'est pas effacé : il part à côté, daté.
        tampon = datetime.now().strftime("%Y%m%d-%H%M%S")
        cible = place_libre(ANCIENS, f"{ancien.stem}_{tampon}{ancien.suffix}")
        shutil.move(str(ancien), str(cible))
        deplace = str(cible.relative_to(RACINE)).replace("\\", "/")
    nouveau = PHOTOS / (pid + ext)
    nouveau.write_bytes(octets)
    if p.get("photo"):
        # Un portrait déclaré nommément pointerait encore vers l'ancien.
        h.noter(pid=pid, champ="photo", action="modification", ancien=p["photo"],
                nouveau=None, admin=admin)
        p.pop("photo")
    h.noter(pid=pid, champ="portrait", action="modification" if ancien else "ajout",
            ancien=deplace, nouveau=nouveau.name, admin=admin)
    return "portrait remplacé" if ancien else "portrait ajouté"


def op_photo(d, h, a, admin):
    pid, action = a.get("pid"), a.get("action")
    p = _personne(d, pid)
    galerie = p.setdefault("galerie", [])

    def legende_de(nom):
        return next((g for g in galerie if g.get("fichier") == nom), None)

    if action == "ajout":
        ext, octets = decoder_image(a.get("donnee"))
        PHOTOS.mkdir(exist_ok=True)
        n = 2
        while any((PHOTOS / f"{pid}-{n}{e}").exists() for e in EXTENSIONS):
            n += 1
        cible = PHOTOS / f"{pid}-{n}{ext}"
        cible.write_bytes(octets)
        lg = texte_propre(a.get("legende"), 600)
        galerie.append({"fichier": cible.name, "legende": lg, "ajout": True})
        h.noter(pid=pid, champ="galerie", action="ajout", ancien=None,
                nouveau=cible.name, admin=admin)
        return "photo ajoutée"

    nom = a.get("fichier")
    if not isinstance(nom, str) or "/" in nom or "\\" in nom or ".." in nom \
            or not nom.startswith(pid + "-") or not (PHOTOS / nom).exists():
        raise Refus("photo introuvable")

    if action == "legende":
        lg = texte_propre(a.get("legende"), 600)
        g = legende_de(nom)
        ancien = g.get("legende") if g else None
        if (ancien or "") == lg:
            return "rien à changer"
        if g:
            g["legende"] = lg
        else:
            galerie.append({"fichier": nom, "legende": lg})
        h.noter(pid=pid, champ="legende", action="modification", ancien=ancien,
                nouveau=lg, admin=admin, fichier=nom)
        return "légende enregistrée"

    if action == "retrait":
        g = legende_de(nom)
        if not admin and not (g and g.get("ajout")):
            _admin_requis(False, "retirer une photo qui ne vient pas de l'interface")
        cible = place_libre(RETIREES, nom)
        shutil.move(str(PHOTOS / nom), str(cible))
        if g:
            galerie.remove(g)
        if not galerie:
            p.pop("galerie", None)
        h.noter(pid=pid, champ="galerie", action="retrait", ancien=nom, nouveau=None,
                admin=admin, deplacee=str(cible.relative_to(RACINE)).replace("\\", "/"),
                legende=(g or {}).get("legende"), motif=a.get("motif"))
        return "photo retirée (rangée dans photos/_retirees)"
    raise Refus("action inconnue sur une photo")


def op_recette(d, h, a, admin):
    pid = a.get("pid")
    p = _personne(d, pid)
    sections = p.setdefault("sections", [])
    i = a.get("index")
    titre = texte_propre(a.get("titre"), 300)
    texte = texte_propre(a.get("texte"), 60000)

    if a.get("retrait"):
        if not isinstance(i, int) or not 0 <= i < len(sections) or not est_recette(sections[i]):
            raise Refus("recette introuvable — rechargez la page")
        s = sections[i]
        if not admin and not s.get("ajout"):
            _admin_requis(False, "retirer une recette qui vient des sources")
        sections.pop(i)
        if not sections:
            p.pop("sections", None)
        h.noter(pid=pid, champ="sections", action="retrait", ancien=s, nouveau=None,
                admin=admin, index=i, motif=a.get("motif"))
        return "recette retirée"

    if not (titre or texte):
        # Défaut D-2 : une recette vide n'est pas un ajout.
        raise Refus("recette vide : rien n'a été enregistré")
    contenu = [x.strip() for x in texte.split("\n\n") if x.strip()] or [""]
    if i is None:
        s = {"titre": "Recette — " + (titre or "sans nom"), "type": "texte",
             "recette": True, "ajout": True, "contenu": contenu,
             "source": "Ajout par la fiche, " + maintenant()[:10]}
        sections.append(s)
        h.noter(pid=pid, champ="sections", action="ajout", ancien=None, nouveau=s, admin=admin)
        return "recette ajoutée"
    if not isinstance(i, int) or not 0 <= i < len(sections) or not est_recette(sections[i]):
        raise Refus("recette introuvable — rechargez la page")
    s = sections[i]
    ancien = json.loads(json.dumps(s))
    s["titre"] = "Recette — " + (titre or "sans nom")
    s["contenu"] = contenu
    s["recette"] = True
    if s == ancien:
        return "rien à changer"
    h.noter(pid=pid, champ="sections", action="modification", ancien=ancien,
            nouveau=json.loads(json.dumps(s)), admin=admin, index=i)
    return "recette enregistrée"


def op_section_retrait(d, h, a, admin):
    pid, i = a.get("pid"), a.get("index")
    p = _personne(d, pid)
    sections = p.get("sections") or []
    if not isinstance(i, int) or not 0 <= i < len(sections):
        raise Refus("section introuvable — rechargez la page")
    s = sections[i]
    if not (admin or s.get("ajout")):
        _admin_requis(False, "retirer une section")
    sections.pop(i)
    if not sections:
        p.pop("sections", None)
    h.noter(pid=pid, champ="sections", action="retrait", ancien=s, nouveau=None,
            admin=admin, index=i, motif=a.get("motif"))
    return "section retirée"


def op_retrait(d, h, a, admin):
    """Retirer un fait, un champ ou un élément de liste."""
    pid, cle = a.get("pid"), a.get("cle")
    p = _personne(d, pid)
    if cle in FAITS + NOMS + CHAMPS_LIBRES:
        if cle not in p:
            raise Refus("rien à retirer")
        ancien = p[cle]
        if not admin and not h.ajoute_par_interface(pid, cle, ancien):
            _admin_requis(False, "retirer une information qui vient des sources")
        p.pop(cle)
        h.noter(pid=pid, champ=cle, action="retrait", ancien=ancien, nouveau=None,
                admin=admin, motif=a.get("motif"))
        return "retiré"
    if cle in LISTES:
        liste = p.get(cle) or []
        i = a.get("index")
        if not isinstance(i, int) or not 0 <= i < len(liste):
            raise Refus("élément introuvable — rechargez la page")
        ancien = liste[i]
        if a.get("attendu") is not None and a.get("attendu") != ancien:
            raise Refus("cet élément a changé depuis l'ouverture de la page ; rechargez-la")
        if not admin and not h.ajoute_par_interface(pid, cle, ancien):
            _admin_requis(False, "retirer une information qui vient des sources")
        liste.pop(i)
        if not liste:
            p.pop(cle)
        h.noter(pid=pid, champ=cle, action="retrait", ancien=ancien, nouveau=None,
                admin=admin, index=i, motif=a.get("motif"))
        return "retiré"
    raise Refus(f"champ inconnu : {cle}")


def op_evenement(d, h, a, admin):
    """Un fait marquant, rattaché à une ou plusieurs personnes."""
    evs = d.setdefault("evenements", [])
    eid = a.get("id")
    trouve = next((e for e in evs if e.get("id") == eid), None) if eid else None
    if eid and not trouve:
        raise Refus("fait marquant introuvable — rechargez la page")

    if a.get("retrait"):
        if not (admin or trouve.get("ajout")):
            _admin_requis(False, "retirer un fait marquant venu des sources")
        evs.remove(trouve)
        h.noter(champ="evenements", action="retrait", ancien=trouve, nouveau=None,
                admin=admin, personnes=trouve.get("personnes"), motif=a.get("motif"))
        return "fait marquant retiré"

    texte = texte_propre(a.get("texte"), 4000)
    if not texte:
        raise Refus("un fait marquant sans texte n'est pas un fait : rien n'a été enregistré")
    personnes = a.get("personnes") or []
    if not isinstance(personnes, list) or not personnes:
        raise Refus("rattachez le fait à au moins une personne")
    personnes = list(dict.fromkeys(personnes))
    for x in personnes:
        _personne(d, x)
    date_ = texte_propre(a.get("date"), 120)
    cert = a.get("certitude") or (certitude_devinee(date_) if date_ else "inconnue")
    if cert not in CERTITUDES:
        raise Refus(f"niveau de certitude inconnu : {cert}")
    nouveau = {"texte": texte, "personnes": personnes, "certitude": cert}
    # La source du fait arrive sous « provenance » : « source » est le
    # fichier de données de la demande.
    for cle, champ, maxi in (("date", "date", 120), ("lieu", "lieu", 300),
                             ("source", "provenance", 1000)):
        v = texte_propre(a.get(champ), maxi)
        if v:
            nouveau[cle] = v
    if annee(date_):
        nouveau["tri"] = annee(date_)

    if trouve is None:
        nouveau["id"] = "ev-" + secrets.token_hex(4)
        nouveau["ajout"] = True
        evs.append(nouveau)
        h.noter(champ="evenements", action="ajout", ancien=None, nouveau=nouveau,
                admin=admin, personnes=personnes)
        return "fait marquant ajouté"
    if trouve.get("certitude") == "attestee" and not trouve.get("ajout"):
        _admin_requis(admin, "modifier un fait marquant attesté par la source")
    ancien = json.loads(json.dumps(trouve))
    nouveau["id"] = trouve["id"]
    if trouve.get("ajout"):
        nouveau["ajout"] = True
    if {k: v for k, v in ancien.items()} == nouveau:
        return "rien à changer"
    trouve.clear()
    trouve.update(nouveau)
    h.noter(champ="evenements", action="modification", ancien=ancien, nouveau=nouveau,
            admin=admin, personnes=sorted(set(personnes) | set(ancien.get("personnes") or [])))
    return "fait marquant enregistré"


NATURES = ("conjoint", "mariage")


def identifiant(d, prenom, nom, an):
    """Un identifiant neuf, à la façon des autres : prenom-nom-annee, sans
    accents. Jamais réutilisé : un suffixe s'ajoute s'il est pris."""
    brut = " ".join(x for x in (prenom, nom, str(an or "")) if x)
    plat = unicodedata.normalize("NFD", brut.replace("đ", "d").replace("Đ", "D"))
    plat = "".join(c for c in plat if not unicodedata.combining(c)).lower()
    base = re.sub(r"[^a-z0-9]+", "-", plat).strip("-") or "personne"
    pid, n = base, 2
    while pid in d["personnes"]:
        pid, n = f"{base}-{n}", n + 1
    return pid


def op_conjoint(d, h, a, admin):
    """Un(e) conjoint(e) — significatif(ve) ou marié(e) — pour une personne.

    La personne rattachée est soit déjà dans les données (« personne »),
    soit créée ici (« nouvelle » : prénom, nom, naissance, sexe). L'union
    porte « nature » : « conjoint » pour un(e) conjoint(e) significatif(ve),
    « mariage » sinon, et « debut » pour la date ou la période."""
    pid = a.get("pid")
    _personne(d, pid)
    unions = d.setdefault("unions", [])
    uid = a.get("union")

    if uid:
        u = next((x for x in unions if x.get("id") == uid), None)
        if u is None or pid not in u.get("conjoints", []):
            raise Refus("union introuvable — rechargez la page")

        if a.get("retrait"):
            if not (admin or u.get("ajout")):
                _admin_requis(False, "retirer une union qui vient des sources")
            if u.get("enfants"):
                raise Refus("cette union a des enfants : on ne la retire pas d'ici")
            unions.remove(u)
            # La personne créée avec l'union part avec elle si plus rien ne
            # la relie à l'arbre ; elle reste dans l'historique.
            partie = None
            autre = next((c for c in u["conjoints"] if c != pid), None)
            if autre and d["personnes"].get(autre, {}).get("ajout") and not any(
                    autre in x.get("conjoints", []) or autre in (x.get("enfants") or [])
                    for x in unions):
                partie = {"id": autre, "donnees": d["personnes"].pop(autre)}
            h.noter(pid=pid, champ="unions", action="retrait",
                    ancien={"union": u, "personne": partie}, nouveau=None, admin=admin,
                    personnes=u["conjoints"], motif=a.get("motif"))
            return "union retirée"

        nature = a.get("nature") or u.get("nature") or "mariage"
        if nature not in NATURES:
            raise Refus("nature d'union inconnue")
        if not (admin or u.get("ajout")) and nature != (u.get("nature") or "mariage"):
            _admin_requis(False, "changer la nature d'une union lue dans les sources")
        ancien = json.loads(json.dumps(u))
        texte = texte_propre(a.get("debut"), 300)
        cle = "mariage" if nature == "mariage" else "debut"
        for k in ("mariage", "debut"):
            if k != cle and k in u and (u.get("ajout") or admin):
                u.pop(k)
        if texte:
            if (u.get(cle) or {}).get("certitude") == "attestee" and u[cle].get("texte") != texte:
                _admin_requis(admin, "remplacer une date d'union attestée")
            u[cle] = {"texte": texte, "certitude": certitude_devinee(texte)}
        if nature == "conjoint":
            u["nature"] = "conjoint"
        else:
            u.pop("nature", None)
        note = texte_propre(a.get("note"), 1000)
        if note and note not in (u.get("notes") or []):
            u.setdefault("notes", []).append(note)
        if u == ancien:
            return "rien à changer"
        h.noter(pid=pid, champ="unions", action="modification", ancien=ancien,
                nouveau=json.loads(json.dumps(u)), admin=admin, personnes=u["conjoints"])
        return "union enregistrée"

    # ---- ajout ----
    nature = a.get("nature") or "conjoint"
    if nature not in NATURES:
        raise Refus("nature d'union inconnue")
    autre = a.get("personne")
    creee = None
    if autre:
        _personne(d, autre)
        if autre == pid:
            raise Refus("une personne n'est pas sa propre conjointe")
        if any(set(u.get("conjoints", [])) == {pid, autre} for u in unions):
            raise Refus("ces deux personnes sont déjà unies dans l'arbre")
    else:
        n = a.get("nouvelle") or {}
        prenom = texte_propre(n.get("prenom"), 120)
        nom = texte_propre(n.get("nom"), 120)
        if not (prenom or nom):
            raise Refus("donnez au moins un prénom ou un nom, ou choisissez une personne de l'arbre")
        naissance = texte_propre(n.get("naissance"), 300)
        autre = identifiant(d, prenom, nom, annee(naissance))
        p = {"prenom": prenom, "nom": nom, "sexe": n.get("sexe") if n.get("sexe") in ("F", "M") else "",
             "sources": ["Ajout par la fiche, " + maintenant()[:10]], "ajout": True}
        if not p["sexe"]:
            p.pop("sexe")
        if naissance:
            p["naissance"] = {"texte": naissance, "certitude": certitude_devinee(naissance)}
            if annee(naissance):
                p["naissance"]["tri"] = annee(naissance)
        d["personnes"][autre] = p
        creee = autre
    u = {"id": "u-" + secrets.token_hex(4), "conjoints": [pid, autre], "enfants": [],
         "ajout": True, "sources": ["Ajout par la fiche, " + maintenant()[:10]]}
    if nature == "conjoint":
        u["nature"] = "conjoint"
    texte = texte_propre(a.get("debut"), 300)
    if texte:
        u["mariage" if nature == "mariage" else "debut"] = {
            "texte": texte, "certitude": certitude_devinee(texte)}
    note = texte_propre(a.get("note"), 1000)
    if note:
        u["notes"] = [note]
    unions.append(u)
    h.noter(pid=pid, champ="unions", action="ajout", ancien=None,
            nouveau={"union": u, "personne_creee": creee}, admin=admin, personnes=[pid, autre])
    return "conjoint(e) ajouté(e)"


def op_restaurer(d, h, a, admin):
    """Remettre ce qu'une entrée de l'historique a remplacé ou retiré."""
    _admin_requis(admin, "restaurer depuis l'historique")
    e = h.entree(a.get("n"))
    if e.get("restauree"):
        raise Refus("déjà restaurée")
    champ, pid, ancien = e.get("champ"), e.get("pid"), e.get("ancien")

    if champ == "unions":
        unions = d.setdefault("unions", [])
        if e["action"] == "retrait":
            pers = (ancien or {}).get("personne")
            if pers and pers["id"] not in d["personnes"]:
                d["personnes"][pers["id"]] = pers["donnees"]
            for c in ancien["union"]["conjoints"]:
                _personne(d, c)
            unions.append(ancien["union"])
        elif e["action"] == "modification":
            cur = next((x for x in unions if x.get("id") == ancien.get("id")), None)
            if cur is None:
                raise Refus("cette union n'existe plus")
            cur.clear(); cur.update(ancien)
        else:
            raise Refus("un ajout se défait en retirant l'élément")
    elif champ == "evenements":
        evs = d.setdefault("evenements", [])
        if e["action"] == "retrait":
            evs.append(ancien)
        elif e["action"] == "modification":
            cur = next((x for x in evs if x.get("id") == ancien.get("id")), None)
            if cur is None:
                evs.append(ancien)
            else:
                cur.clear(); cur.update(ancien)
        else:
            raise Refus("un ajout se défait en retirant l'élément")
    elif champ == "portrait":
        if not ancien:
            raise Refus("il n'y avait pas de portrait avant")
        src = RACINE / ancien
        if not src.exists():
            raise Refus("l'ancien portrait n'est plus à " + ancien)
        p = _personne(d, pid)
        actuel = portrait_actuel(pid, p)
        if actuel is not None:
            tampon = datetime.now().strftime("%Y%m%d-%H%M%S")
            shutil.move(str(actuel), str(place_libre(ANCIENS, f"{actuel.stem}_{tampon}{actuel.suffix}")))
        shutil.move(str(src), str(PHOTOS / (pid + src.suffix)))
    elif champ == "galerie" and e["action"] == "retrait":
        src = RACINE / e.get("deplacee", "")
        if not src.is_file():
            raise Refus("la photo retirée n'est plus dans photos/_retirees")
        cible = PHOTOS / ancien
        if cible.exists():
            raise Refus(f"{ancien} est déjà occupé")
        shutil.move(str(src), str(cible))
        p = _personne(d, pid)
        p.setdefault("galerie", []).append({"fichier": ancien, "legende": e.get("legende") or ""})
    elif champ == "sections":
        p = _personne(d, pid)
        secs = p.setdefault("sections", [])
        if e["action"] == "retrait":
            secs.insert(min(e.get("index", len(secs)), len(secs)), ancien)
        elif e["action"] == "modification":
            i = e.get("index")
            if isinstance(i, int) and i < len(secs) and est_recette(secs[i]):
                secs[i] = ancien
            else:
                secs.append(ancien)
        else:
            raise Refus("un ajout se défait en retirant l'élément")
    elif champ in LISTES:
        p = _personne(d, pid)
        liste = p.setdefault(champ, [])
        if e["action"] == "retrait":
            liste.insert(min(e.get("index", len(liste)), len(liste)), ancien)
        elif e["action"] == "modification":
            i = e.get("index")
            if isinstance(i, int) and i < len(liste) and liste[i] == e.get("nouveau"):
                liste[i] = ancien
            else:
                liste.append(ancien)
        else:
            raise Refus("un ajout se défait en retirant l'élément")
    elif champ in FAITS + NOMS + CHAMPS_LIBRES + ("photo",):
        p = _personne(d, pid)
        if ancien is None:
            raise Refus("il n'y avait rien avant : retirez plutôt la valeur")
        p[champ] = ancien
    elif champ == "legende":
        p = _personne(d, pid)
        g = next((x for x in p.get("galerie", []) if x.get("fichier") == e.get("fichier")), None)
        if g is None:
            raise Refus("la photo n'est plus là")
        g["legende"] = ancien or ""
    else:
        raise Refus("cette entrée ne se restaure pas")

    e["restauree"] = maintenant()
    h.noter(pid=pid, champ=champ, action="restauration", ancien=None, nouveau=ancien,
            admin=True, entree=e["n"], personnes=e.get("personnes"))
    return "restauré"


OPERATIONS = {
    "fait": op_fait, "champ": op_champ, "liste": op_liste, "photo": op_photo,
    "recette": op_recette, "section_retrait": op_section_retrait,
    "retrait": op_retrait, "evenement": op_evenement, "restaurer": op_restaurer,
    "conjoint": op_conjoint,
}


def executer(a, admin=False):
    """Applique UNE demande. Valide avant d'écrire : les données ne sont
    écrites qu'après avoir été remises en JSON et relues avec succès."""
    if not isinstance(a, dict):
        raise Refus("demande illisible")
    source = chemin_source(a.get("source"))
    op = a.get("op")
    try:
        d = json.loads(source.read_text(encoding="utf-8"))
    except Exception as e:
        raise Refus(f"{source.name} est illisible : {e}")
    h = Historique(source)

    if op == "portrait":
        msg = op_portrait(d, h, a, admin, source)
    elif op in OPERATIONS:
        msg = OPERATIONS[op](d, h, a, admin)
    else:
        raise Refus(f"opération inconnue : {op}")
    if msg == "rien à changer":
        return msg, source

    texte = json.dumps(d, ensure_ascii=False, indent=1)
    json.loads(texte)                         # valider avant d'écrire
    HISTORIQUE.mkdir(exist_ok=True)
    h.f.write_text(h.texte(), encoding="utf-8")
    tmp = source.with_name(source.name + ".ecriture")
    tmp.write_text(texte, encoding="utf-8")
    tmp.replace(source)
    return msg, source


def historique_de(source_nom, pid):
    source = chemin_source(source_nom)
    return Historique(source).pour(pid)
