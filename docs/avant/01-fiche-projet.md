# 01 — Fiche projet

**Arbre généalogique Jean** · protocole v1.0 · mode **économe** · doc-v1

## Admission

- [x] **Aucune donnée clinique de client.** Ce projet n'en contient pas et n'en contiendra pas.

## Interdits

Ces cinq règles priment sur toute demande ponctuelle. En cas de doute entre un interdit et une consigne, l'interdit gagne et vous inscrivez une question `Q-xx`.

1. **Ne jamais inventer une donnée généalogique.** Aucune date, aucun lieu, aucun lien de filiation ne s'ajoute sans figurer dans une source citée. Un trou reste un trou, marqué comme tel. C'est l'interdit le plus important du projet : une généalogie se corrompt par les certitudes empruntées, et une donnée plausible mais fausse est indétectable dix ans plus tard.
2. **Ne jamais supprimer de fichier.** Ni données, ni fiches devenues orphelines, ni sorties. On signale, l'utilisateur décide.
3. **Ne jamais modifier `tests/`.** Un test qui vous semble faux appelle une `Q-xx`, pas une retouche.
4. **Aucun accès réseau** depuis le générateur ni depuis les pages produites. Tout doit fonctionner sur un poste hors ligne, et les fichiers produits doivent s'ouvrir sans connexion.
5. **Ne jamais se déclarer terminé sans tests verts.** `Tester.bat` fait foi, pas l'impression que le code est correct.

## But, en une phrase

Transformer un fichier de données généalogiques en un arbre HTML autonome, consultable hors ligne, avec une fiche descriptive par personne — et rester extensible pendant des années, au fil des trouvailles d'archives.

## Utilisateur et contexte

Un seul utilisateur : Sébastien Trinh. Usage personnel et familial, sur Windows, par double-clic. Il ne tape aucune commande. Le produit sera montré à de la parenté et possiblement transmis ; il doit donc fonctionner sur une machine quelconque, sans installation.

## Ce que le programme fait aujourd'hui

- Lit `genealogie_jean.json` : personnes, unions, points à vérifier, table cartographique.
- Intègre les portraits déposés dans `photos/` (recadrage carré, réduction, encodage dans le HTML).
- Produit `arbre_jean.html`, fichier unique et autonome : deux vues (Portraits en médaillons, Cartes en rectangles), zoom, déplacement, recherche, surlignage de la lignée directe, thème clair/sombre.
- Produit une page complète par personne dans `arbre_jean_fiches/`, reliées entre elles.
- Produit sur demande une version partageable d'où les sections confidentielles sont **physiquement retirées**.

## Inclus dans la phase 0

La mise sous protocole, **sans modifier un seul comportement**. Structure du dépôt, dépôt git, contrat de vérification codé `T-xx`, empreinte, journal. À la fin de la phase 0, le programme produit exactement les mêmes fichiers qu'avant.

## Exclus de la phase 0

Toute amélioration, toute correction d'apparence, toute nouvelle fonction. Elles attendent la phase 1. Un constat intéressant fait en cours de route va dans `docs/apres/11-questions.md`, pas dans le code.

## Exclus du projet entier

- Le travail éditorial : transcrire le livre, trancher les incohérences, décider ce qui entre dans l'arbre. Cela reste à Sébastien et à Claude.
- Toute forme de publication en ligne.

## Hypothèses validées au cadrage

| | |
|---|---|
| **H-01** | La phase 0 ne modifie aucun comportement du programme. |
| **H-02** | `src/generer_arbre.py` reste la base ; son architecture n'est pas remise en question. |
| **H-03** | Données réelles, photos, scans et fichiers produits sont au `.gitignore`. |
| **H-04** | Les tests tournent sur `tests/donnees/`, jamais sur les données personnelles. |
| **H-05** | Structure du protocole adoptée, mais tous les `.bat` restent à la racine. |
| **H-06** | La couche navigateur est facultative : `SAUTE` et non `ECHEC` tant que Playwright manque. |
| **H-07** | Les contrôles existants sont repris tels quels en `T-01` à `T-36`. |
| **H-08** | Le prompt de lancement est `D-001` ; la numérotation repart de zéro. |
| **H-09** | Qwen travaille sur Wilfred ; dellg5 n'est qu'un point d'échange. Seul Wilfred fait foi. |
| **H-10** | Aucune dépendance au-delà de Python et de Pillow (facultatif). |
