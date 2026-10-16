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

Bibliothèque standard seule (H-10). Aucune suppression (interdit 2).

    python outils/serveur.py          (puis le navigateur s'ouvre)
"""

import json
import secrets
import sys
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))
from appliquer_ajouts import appliquer  # noqa: E402  (même dossier)

JETON = secrets.token_urlsafe(18)
PORT_SOUHAITE = 8731
MAX_OCTETS = 80 * 1024 * 1024      # 80 Mo : une poignée de photos, pas un disque


class Poste(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *a):
        if "POST" in (a[0] if a else ""):
            sys.stderr.write("  " + (fmt % a) + "\n")

    # ---- le jeton, lisible seulement depuis cette origine ----
    def do_GET(self):
        if self.path == "/_jeton":
            self.repondre({"jeton": JETON})
            return
        super().do_GET()

    def repondre(self, obj, code=200):
        corps = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corps)))
        self.end_headers()
        self.wfile.write(corps)

    def do_POST(self):
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


def main():
    gest = partial(Poste, directory=str(RACINE))
    port = PORT_SOUHAITE
    for essai in range(12):
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", port), gest)
            break
        except OSError:
            port += 1
    else:
        print("Aucun port libre entre 8731 et 8742."); return 2

    arbres = sorted(RACINE.glob("arbre_*.html"))
    page = arbres[0].name if arbres else ""
    url = f"http://127.0.0.1:{port}/{page}"

    print("=" * 62)
    print("  SERVEUR LOCAL — arbre généalogique")
    print("=" * 62)
    print(f"\n  {url}\n")
    print("  Écoute sur 127.0.0.1 seulement : rien d'autre que cet")
    print("  ordinateur ne peut l'atteindre.")
    print("\n  Les fiches ouvertes PAR CETTE ADRESSE enregistrent directement.")
    print("  Ouvertes par double-clic, elles rendent un fichier d'ajouts,")
    print("  comme avant — c'est ce qui permet de les envoyer à la parenté.")
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
