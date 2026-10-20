#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
serveur.py — sert le projet sur la boucle locale pour que les fiches
écrivent directement, sans passer par un fichier d'ajouts.

PERMIS PAR L'AMENDEMENT DE L'INTERDIT 4 (D-004, 2026-10-16), et seulement
pour le poste de travail. Les exports de branche doivent rester utilisables
par double-clic, sans serveur : la même fiche constate comment elle a été
ouverte et se comporte en conséquence.

CE QU'IL N'EST PAS. Il n'écoute que sur 127.0.0.1 — jamais 0.0.0.0 — donc
rien d'autre que cette machine ne peut l'atteindre. L'air-gap de Wilfred
n'est pas entamé : la boucle locale ne sort pas de l'ordinateur.

LES TROIS VERROUS, et pourquoi chacun
  1. Écoute sur 127.0.0.1 seulement. Sur 0.0.0.0, tout le réseau local
     pourrait écrire dans vos photos.
  2. Un jeton tiré au lancement. Sans lui, n'importe quelle page ouverte
     dans un autre onglet pourrait poster ici à votre insu — une page web
     peut émettre une requête vers localhost, c'est une attaque réelle et
     pas une hypothèse d'école.
  3. Écriture confinée à `photos/` et aux fichiers de données du projet.
     Les noms de fichiers sont fabriqués à partir des identifiants, jamais
     repris de ce que le navigateur envoie.

LE MODE ADMINISTRATEUR (C-021). Le mot de passe est vérifié ICI, contre une
empreinte gardée hors de git (outils/admin.py) ; la page ne le connaît pas.
Une connexion réussie rend un jeton de session, en mémoire seulement.

Bibliothèque standard seule (H-10). Aucune suppression (interdit 2) : ce
qu'on retire est déplacé et consigné, voir outils/edition.py.

    python outils/serveur.py          (puis le navigateur s'ouvre)
"""

import json
import os
import socket
import secrets
import subprocess
import sys
import threading
import time
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))
from appliquer_ajouts import appliquer  # noqa: E402  (même dossier)
import admin as ADMIN                      # noqa: E402
import edition                             # noqa: E402

JETON = secrets.token_urlsafe(18)
PORT_SOUHAITE = 8731
MAX_OCTETS = 80 * 1024 * 1024      # 80 Mo : une poignée de photos, pas un disque
GENERATEUR = RACINE / "src" / "generer_arbre.py"

# Une seule écriture à la fois : deux modifications simultanées liraient le
# même fichier et la seconde effacerait la première.
VERROU = threading.Lock()

# Sessions administrateur : jeton -> échéance. En mémoire seulement ; elles
# meurent avec le serveur, et le mot de passe ne transite qu'une fois.
SESSIONS_ADMIN = {}
DUREE_ADMIN = 8 * 3600


def admin_valide(jeton):
    if not jeton:
        return False
    fin = SESSIONS_ADMIN.get(jeton)
    if not fin or fin < time.time():
        SESSIONS_ADMIN.pop(jeton, None)
        return False
    return True


def regenerer(source):
    """Refait l'arbre et les fiches du fichier modifié, puis -- s'il existe
    déjà -- la version partageable, pour qu'elle ne retarde pas."""
    r = subprocess.run([sys.executable, str(GENERATEUR), str(source)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        return False, (r.stderr or r.stdout or "").strip()[-600:]
    partage = source.with_name(source.stem.replace("genealogie_", "arbre_") + "_partage.html")
    if partage.exists():
        # Après la réponse, pas avant : la page qu'on modifie n'attend que
        # son arbre. La version partageable suit, sous le même verrou.
        def suite():
            with VERROU:
                subprocess.run([sys.executable, str(GENERATEUR), str(source), "--partage"],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
        threading.Thread(target=suite, daemon=True).start()
    return True, ""


class Poste(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *a):
        # str() : sur une erreur (404), le premier argument est un code
        # HTTPStatus et non la ligne de requête ; « in » plantait dessus.
        if "POST" in (str(a[0]) if a else ""):
            sys.stderr.write("  " + (fmt % a) + "\n")

    # ---- le jeton, lisible seulement depuis cette origine ----
    def do_GET(self):
        if self.path == "/_jeton":
            self.repondre({"jeton": JETON, "admin_possible": ADMIN.configure()})
            return
        super().do_GET()

    def end_headers(self):
        # Après une modification, la page se recharge : elle doit relire le
        # fichier régénéré, pas une copie gardée par le navigateur.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def lire_demande(self):
        """Les trois verrous d'une écriture : type JSON, jeton, taille."""
        if "application/json" not in (self.headers.get("Content-Type") or ""):
            self.repondre({"erreur": "type attendu : application/json"}, 415); return None
        if self.headers.get("X-Jeton") != JETON:
            self.repondre({"erreur": "jeton absent ou faux"}, 403); return None
        taille = int(self.headers.get("Content-Length") or 0)
        if taille <= 0 or taille > MAX_OCTETS:
            self.repondre({"erreur": f"taille refusée ({taille} octets)"}, 413); return None
        try:
            return json.loads(self.rfile.read(taille).decode("utf-8"))
        except Exception as e:
            self.repondre({"erreur": f"JSON illisible : {e}"}, 400); return None

    def modifier(self):
        a = self.lire_demande()
        if a is None:
            return
        admin = admin_valide(self.headers.get("X-Admin"))
        with VERROU:
            try:
                msg, source = edition.executer(a, admin=admin)
            except edition.Refus as e:
                self.repondre({"ok": False, "erreur": str(e)}); return
            except Exception as e:
                self.repondre({"ok": False, "erreur": f"{type(e).__name__} : {e}"}, 500); return
            if msg == "rien à changer":
                self.repondre({"ok": True, "message": msg, "inchange": True}); return
            ok, err = regenerer(source)
        sys.stderr.write(f"  modifié : {a.get('op')} {a.get('pid') or a.get('id') or ''} -- {msg}\n")
        self.repondre({"ok": True, "message": msg, "regenere": ok,
                       "avertissement": None if ok else "données enregistrées, mais "
                       "la régénération a échoué : " + err})

    def connexion_admin(self):
        a = self.lire_demande()
        if a is None:
            return
        if not ADMIN.configure():
            self.repondre({"ok": False, "erreur": "aucun mot de passe posé -- lancez "
                           "Changer_Mot_De_Passe_Admin.bat"}); return
        if not ADMIN.verifier(a.get("motdepasse")):
            time.sleep(1.2)          # freine qui essaierait au hasard
            self.repondre({"ok": False, "erreur": "mot de passe refusé"}); return
        j = secrets.token_urlsafe(24)
        SESSIONS_ADMIN[j] = time.time() + DUREE_ADMIN
        self.repondre({"ok": True, "admin": j})

    def historique(self):
        a = self.lire_demande()
        if a is None:
            return
        if not admin_valide(self.headers.get("X-Admin")):
            self.repondre({"ok": False, "erreur": "réservé au mode administrateur"}); return
        try:
            self.repondre({"ok": True,
                           "entrees": edition.historique_de(a.get("source"), a.get("pid"))})
        except edition.Refus as e:
            self.repondre({"ok": False, "erreur": str(e)})

    def repondre(self, obj, code=200):
        corps = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corps)))
        self.end_headers()
        self.wfile.write(corps)

    def do_POST(self):
        if self.path == "/_modifier":
            self.modifier(); return
        if self.path == "/_admin":
            self.connexion_admin(); return
        if self.path == "/_admin_sortir":
            SESSIONS_ADMIN.pop(self.headers.get("X-Admin"), None)
            self.repondre({"ok": True}); return
        if self.path == "/_historique":
            self.historique(); return
        if self.path != "/_ajouts":
            self.repondre({"erreur": "chemin inconnu"}, 404); return

        # Le type doit être application/json : cela force le navigateur à
        # demander la permission avant d'envoyer depuis une autre origine,
        # et nous la refusons en ne répondant pas aux requêtes OPTIONS.
        if "application/json" not in (self.headers.get("Content-Type") or ""):
            self.repondre({"erreur": "type attendu : application/json"}, 415); return
        if self.headers.get("X-Jeton") != JETON:
            self.repondre({"erreur": "jeton absent ou faux"}, 403); return

        taille = int(self.headers.get("Content-Length") or 0)
        if taille <= 0 or taille > MAX_OCTETS:
            self.repondre({"erreur": f"taille refusée ({taille} octets)"}, 413); return

        try:
            a = json.loads(self.rfile.read(taille).decode("utf-8"))
        except Exception as e:
            self.repondre({"erreur": f"JSON illisible : {e}"}, 400); return

        pid = a.get("id")
        if not isinstance(pid, str) or not pid or "/" in pid or "\\" in pid or ".." in pid:
            self.repondre({"erreur": "identifiant absent ou douteux"}, 400); return

        # On réutilise l'outil déjà éprouvé plutôt que d'en écrire un second :
        # un deuxième chemin d'écriture, c'est un deuxième jeu de garde-fous
        # à maintenir, et c'est celui qu'on teste le moins qui lâche.
        tmp = RACINE / f"ajouts-{pid}.json"
        tmp.write_text(json.dumps(a, ensure_ascii=False), encoding="utf-8")
        sortie = []
        import io, contextlib
        tampon = io.StringIO()
        with contextlib.redirect_stdout(tampon):
            code = appliquer(str(tmp))
        sortie = [l for l in tampon.getvalue().splitlines() if l.strip()]
        self.repondre({"ok": code == 0, "rapport": sortie,
                       "fichier": tmp.name}, 200)

    def do_OPTIONS(self):
        # Pas de permission accordée à une autre origine. C'est le refus
        # qui protège, pas un en-tête permissif mal réglé.
        self.send_response(405); self.end_headers()


class Serveur(ThreadingHTTPServer):
    """Un port déjà pris doit être REFUSÉ. http.server pose
    SO_REUSEADDR, et sous Windows cette option laisse un second serveur
    s'installer sur un port occupé, sans erreur : deux Serveur_Local
    écoutaient alors sur 8731, et le navigateur parlait à l'un ou à l'autre
    au hasard -- y compris à celui d'un autre dossier (C-024). On
    demande l'usage exclusif, et la recherche d'un port libre joue enfin."""
    allow_reuse_address = os.name != "nt"

    def server_bind(self):
        if os.name == "nt" and hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def main():
    gest = partial(Poste, directory=str(RACINE))
    port = PORT_SOUHAITE
    for essai in range(12):
        try:
            srv = Serveur(("127.0.0.1", port), gest)
            break
        except OSError:
            port += 1
    else:
        print("Aucun port libre entre 8731 et 8742."); return 2

    # Quel arbre ouvrir. L'ordre alphabetique donnait arbre_jean.html --
    # le premier arbre du projet, plus l'arbre par defaut depuis le
    # 16 octobre. On ouvrait donc la mauvaise genealogie, en silence.
    # L'arbre par defaut d'abord ; sinon le plus recemment genere.
    arbres = list(RACINE.glob("arbre_*.html"))
    defaut = RACINE / "arbre_samuel.html"
    if defaut.exists():
        page = defaut.name
    elif arbres:
        page = max(arbres, key=lambda f: f.stat().st_mtime).name
    else:
        page = ""
    url = f"http://127.0.0.1:{port}/{page}"

    print("=" * 62)
    print("  SERVEUR LOCAL — arbre généalogique")
    print("=" * 62)
    print(f"\n  {url}\n")
    print("  Écoute sur 127.0.0.1 seulement : rien d'autre que cet")
    print("  ordinateur ne peut l'atteindre.")
    print("\n  Les fiches ouvertes PAR CETTE ADRESSE se modifient sur place :")
    print("  un clic sur une valeur, on corrige, l'arbre se refait seul.")
    print("  Ouvertes par double-clic, elles rendent un fichier d'ajouts,")
    print("  comme avant — c'est ce qui permet de les envoyer à la parenté.")
    if not ADMIN.configure():
        print("\n  (Mode administrateur indisponible : aucun mot de passe posé.)")
    print("\n  Fermez cette fenêtre pour arrêter le serveur.")
    print("-" * 62)
    threading.Timer(0.7, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêté.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
