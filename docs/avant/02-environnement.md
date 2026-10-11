# 02 — Environnement

## La machine

**Wilfred**, poste hors réseau. Aucune connexion, aucun téléchargement possible. Tout ce qui manque doit passer par le sas, à la main, sur clé.

**dellg5** n'est qu'un point d'échange : Claude peut y lire et y exécuter, mais **seul un résultat obtenu sur Wilfred fait foi** (H-09). Un test qui passe sur dellg5 et échoue sur Wilfred, c'est Wilfred qui a raison.

## À constater au démarrage

Ces valeurs ne sont pas connues au moment où cette documentation est écrite. Le prompt de lancement demande à Qwen de les établir lui-même et de les consigner en `E-001.1`, puis de **compléter ce tableau** :

| | Attendu | Constaté |
|---|---|---|
| Version de Python | 3.10 ou plus | à constater |
| Pillow | facultatif, pour les portraits | à constater |
| Git for Windows | requis | à constater |
| Playwright | facultatif en phase 0 | à constater |
| Navigateur pilotable | Edge suffit | à constater |

Si Python manque ou est trop ancien, c'est un blocage `B-xx` immédiat : rien d'autre n'est possible.

Si Git manque, le travail peut commencer mais **aucun commit ne sera possible** — donc aucune trace exploitable par Claude. Déclarez-le en `B-xx` dès la première séance.

## Dépendances

Le générateur fonctionne avec la bibliothèque standard de Python seule.

**Pillow** est facultatif : sans lui, les portraits sont intégrés tels quels, sans recadrage ni réduction. Le programme ne doit jamais s'arrêter parce que Pillow manque.

**Playwright** ne sert qu'aux contrôles `T-29` à `T-34`. Sans lui, ces contrôles s'affichent `SAUTE` et le contrat peut atteindre le vert (H-06). Pour l'installer plus tard : faire passer par le sas la roue pip de `playwright` (environ 46 Mo), puis piloter le **Edge déjà présent sur Windows 11** plutôt que de télécharger Chromium (150 Mo impossibles hors ligne). Le contrat essaie dans l'ordre : Chromium de Playwright, `msedge`, `chrome`.

## Dossiers

| Chemin | Rôle | Versionné |
|---|---|---|
| `src/` | le générateur | oui |
| `tests/` | le contrat de vérification et son empreinte | oui |
| `tests/donnees/` | jeux d'exemple, sans personne réelle | oui |
| `outils/` | empreinte, collecte de panne | oui |
| `docs/` | la documentation | oui |
| `journal/` | le journal de travail | oui |
| `prompts/` | les prompts de lancement et de reprise | oui |
| `genealogie_jean.json` | **les données réelles** | **non** |
| `photos/` | les portraits | **non** |
| `Scans/`, `Scans OCR/` | sources numérisées | **non** |
| `arbre_*.html`, `*_fiches/` | ce que le programme produit | **non** |

## Les `.bat`

Sébastien ne tape aucune commande. Toute opération récurrente a son `.bat` à la racine, lançable par double-clic ou par glisser-déposer d'un fichier de données.

| Fichier | Ce qu'il fait |
|---|---|
| `Generer_Arbre.bat` | produit l'arbre et les fiches |
| `Generer_Version_Partageable.bat` | idem, sections confidentielles retirées |
| `Tester.bat` | vérifie l'empreinte puis passe tout le contrat |
| `Collecter_Panne.bat` | emballe le diagnostic pour le sas |

Tout nouveau script livré en phase 1 ou plus tard reçoit son `.bat`. Un script qui s'exécute uniquement à la ligne de commande est un script non livré.

**Piège connu.** Windows bloque les `.bat` venant du web (marque d'origine Internet). Ceux qui arrivent par le sas peuvent l'être aussi : clic droit → Propriétés → Débloquer.

## Deux pièges rencontrés sur cette chaîne

**La suppression est refusée** sur les dossiers connectés : `rm`, `del`, `unlink` échouent avec « Opération non permise ». Le générateur a été écrit pour ne jamais supprimer — il signale les fiches orphelines et s'arrête là. Ne réintroduisez aucune suppression pour contourner l'obstacle.

**Un fichier produit n'est pas une preuve.** Le générateur peut écrire un HTML parfaitement formé dont le JavaScript est mort. Seul le contrôle navigateur, qui clique réellement, le détecte. C'est arrivé : une capture de pointeur rendait tous les médaillons inertes pendant qu'un test à événement simulé passait au vert.
