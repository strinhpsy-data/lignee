# 01 — Fiche projet

**Arbre généalogique de Samuel** · protocole v1.0 · mode **économe** · doc-v3

> doc-v1 décrivait l'arbre de la famille Jean. La demande `D-002` l'élargit :
> l'arbre devient celui de Samuel, et la famille Jean en devient une des quatre
> branches. Le programme de la phase 0 reste inchangé ; c'est la phase 1 qui
> porte cet élargissement.

## Admission

- [x] **Aucune donnée clinique de client.** Ce projet n'en contient pas et n'en contiendra pas.

Le point 5 de `D-002` fait entrer des informations de santé **de parents**, versées
par eux-mêmes et de leur plein gré. Ce n'est pas du matériel clinique et cela ne
relève pas du dossier professionnel. Deux règles le couvrent : une section
`"prive": true` est **physiquement retirée** de tout fichier qui sort, et tout
export de branche est une version partageable (H-21). Rien d'autre n'est à
inventer là-dessus.

## Interdits

Ces six règles priment sur toute demande ponctuelle. En cas de doute entre un interdit et une consigne, l'interdit gagne et vous inscrivez une question `Q-xx`.

1. **Ne jamais inventer une donnée généalogique.** Aucune date, aucun lieu, aucun lien de filiation ne s'ajoute sans figurer dans une source citée. Un trou reste un trou, marqué comme tel. C'est l'interdit le plus important du projet : une généalogie se corrompt par les certitudes empruntées, et une donnée plausible mais fausse est indétectable dix ans plus tard.
2. **Ne jamais supprimer de fichier.** Ni données, ni fiches devenues orphelines, ni sorties. On signale, l'utilisateur décide.
3. **Ne jamais modifier `tests/`.** Un test qui vous semble faux appelle une `Q-xx`, pas une retouche.
4. **Le générateur ne fait aucun appel réseau, et TOUT EXPORT DESTINÉ À LA PARENTÉ s'ouvre par double-clic, sans serveur, sans installation, hors ligne.** *Reformulé le 2026-10-16 (`D-004`).* L'interdit porte sur ce qui **sort** de la maison, pas sur la façon de travailler : sur son poste, Sébastien utilise ce qu'il veut, serveur local compris. La contrainte n'a jamais eu pour objet de le gêner — elle existe parce qu'un parent qui reçoit une branche n'a personne à appeler si elle ne s'ouvre pas. Déplacée là, elle devient **vérifiable** : ce n'est plus une règle d'écriture qu'on tient par discipline, c'est une propriété de l'export qu'un contrôle éprouve (`T-37`).
5. **Ne jamais se déclarer terminé sans tests verts.** `Tester.bat` fait foi, pas l'impression que le code est correct.
6. **Ne jamais faire entrer les données d'une branche dans l'export d'une autre.** Et ne jamais traiter cela par un filtre appliqué après coup : la règle de parcours de `07-branches-export.md` l'interdit par construction, parce qu'un filtre s'oublie et qu'un parcours, non.

## But, en une phrase

Transformer un fichier de données généalogiques en l'arbre de Samuel — quatre
branches familiales autour de lui, en HTML autonome, consultable hors ligne, avec
une fiche descriptive par personne — et pouvoir en détacher une branche à envoyer
à la parenté.

## Utilisateur et contexte

Un seul utilisateur : Sébastien Trinh. Usage personnel et familial, sur Windows, par double-clic. Il ne tape aucune commande.

Les exports de branche, eux, sont **destinés à des tiers** : oncles, tantes,
cousins. Ils doivent s'ouvrir sur une machine quelconque, sans installation, sans
connexion, et se comprendre sans explication orale.

## Ce que le programme fait aujourd'hui

- Lit `genealogie_jean.json` : personnes, unions, points à vérifier, table cartographique.
- Intègre les portraits déposés dans `photos/` (recadrage carré, réduction, encodage dans le HTML).
- Produit `arbre_jean.html`, fichier unique et autonome : deux vues (Portraits en médaillons, Cartes en rectangles), zoom, déplacement, recherche, surlignage de la lignée directe, thème clair/sombre.
- Produit une page complète par personne dans `arbre_jean_fiches/`, reliées entre elles.
- Produit sur demande une version partageable d'où les sections confidentielles sont **physiquement retirées**.
- **Ne parcourt l'arbre que vers le bas.** Douze endroits du code parcourent les enfants ; aucun ne parcourt les parents. C'est le constat qui fixe le travail de la phase 1.

## Inclus dans la phase 0

La mise sous protocole, **sans modifier un seul comportement**. Structure du dépôt, dépôt git, contrat de vérification codé `T-xx`, empreinte, journal. À la fin de la phase 0, le programme produit exactement les mêmes fichiers qu'avant.

## Inclus dans la phase 1

Le pivot, le sablier, les quatre branches, l'export de branche, la galerie de
portraits. Le détail est dans `06-plan.md`, le modèle de données dans
`03-donnees.md`, les branches dans `07-branches-export.md`.

## Exclus de la phase 0

Toute amélioration, toute correction d'apparence, toute nouvelle fonction. Elles attendent la phase 1. Un constat intéressant fait en cours de route va dans `docs/apres/11-questions.md`, pas dans le code.

## Exclus du projet entier

- Le travail éditorial : transcrire le livre, trancher les incohérences, décider ce qui entre dans l'arbre. Cela reste à Sébastien et à Claude. **La saisie des branches Trinh, Dionne et Gagné en fait partie** : la phase 1 fournit la structure qui les accueille, elle ne remplit rien.
- Toute forme de publication en ligne.
- L'envoi des exports. Le programme produit des fichiers ; la transmission est manuelle.

## Hypothèses validées au cadrage

### doc-v1 — phase 0

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
| **H-09** | **Corrigée le 2026-10-16.** Le projet vit sur **dellg5** et y restera. Wilfred n'est qu'un **prêt temporaire**, et pour une seule raison : faire exécuter une partie de la programmation par un modèle local, afin d'économiser les jetons mensuels. Ce n'est ni la machine de référence, ni la destination. Un résultat obtenu sur dellg5 fait foi ; un contrôle qui ne passerait que sur Wilfred serait le signe d'un problème, pas d'une preuve. |
| **H-10** | Aucune dépendance au-delà de Python et de Pillow (facultatif). |

### doc-v2 — phase 1

| | |
|---|---|
| **H-11** | **Corrigée.** Le pivot s'ajoute à `meta` ; **aucun champ existant ne change de forme**. Vérifié dans le code : l'index inverse `unionParente` est déjà construit côté navigateur, et `union_parente` existe déjà côté Python pour les pages de personne. La migration est additive, et non la rupture de format annoncée au premier cadrage. |
| **H-12** | **Corrigée.** Un seul moteur de parcours, **paramétré par une direction**. Le sablier et l'export de branche en sont deux usages, pas deux moteurs. |
| **H-13** | La branche est **calculée** à chaque génération, jamais stockée sur la personne. |
| **H-14** | **Retirée.** Les niveaux de diffusion sont écartés par `D-002.4` : un parent met ce qu'il veut, il peut ne rien mettre. Le `"prive": true` existant suffit. |
| **H-15** | Les quatre têtes de branche sont les grands-parents du pivot. **Déclarées** dans `meta.branches`, **vérifiées** à la génération. |
| **H-16** | Le modèle accueille dès maintenant la conjointe et les enfants futurs de Samuel, même s'ils ne sont pas encore dessinés. |
| **H-17** | Une galerie de portraits par personne remplace le portrait unique. |
| **H-18** | Saisie manuelle. Aucun formulaire, aucune fusion automatique de contributions en phase 1. |
| **H-19** | Le pivot est un champ déclaré, `meta.pivot`, **jamais déduit**. Une règle du genre « la personne la plus jeune » déplacerait le centre de l'arbre tout seul le jour d'une naissance. |
| **H-20** | `ancetre` **perd son rôle de cadrage** et devient une étiquette par branche, purement descriptive. Conséquence dans le code : le placement des nœuds détachés, qui s'ancre aujourd'hui sur l'ancêtre, a besoin d'un autre point d'appui. |
| **H-21** | Tout export de branche est une version partageable. **Il n'existe pas d'export complet**, et aucune option ne permet de le contourner. |
| **H-22** | Un seul fichier de données pour les quatre branches. Les exports sont des **sorties**, jamais des entrées : rien ne se ressaisit depuis un fichier exporté. |

### doc-v3 — couverture des sources (`D-003`)

| | |
|---|---|
| **H-23** | La chaîne d'océrisation **n'est pas une dépendance du générateur**. Elle vit dans `outils/`, avec ses propres besoins (poppler, tesseract) ; `Generer_Arbre.bat` et `Tester.bat` les ignorent, et H-10 tient. |
| **H-24** | **L'identité d'une page est son nom de fichier** : `Scans OCR/<doc>/p018.txt` *est* la page 18. Aucune table intermédiaire entre les scans et les pages — donc rien à désynchroniser. |
| **H-25** | Les erreurs du rapport de couverture **penchent du côté de l'alarme**. Toute ambiguïté se résout en « non intégrée », et une mention de source illisible est listée plutôt qu'ignorée. |
| **H-26** | Le partage du travail suit **la ligne des dépendances** : l'océrisation à Claude sur dellg5 parce qu'elle exige tesseract, le rapport à Qwen parce qu'il n'exige que Python. |
| **H-27** | Un numéro de page **déduit** l'est à partir du décalage établi par les numéros lus du même lot de scan — une preuve, pas une supposition — et il est marqué comme tel. Ni lu ni encadré, il reste inconnu. |
