# Passation — arbre généalogique — 17 octobre 2026

> Document de reprise pour Claude Code. Il couvre la séance 4 du 17 octobre
> (`C-017` à `C-020`), l'état du projet à la fin de cette séance, et ce qui
> attend. Le journal complet est dans `journal/` ; l'index y résume chaque
> intervention depuis le 11 octobre.

---

## 1 · Ce qu'il faut savoir avant de toucher à quoi que ce soit

**Le projet** : un générateur Python déterministe lit un JSON de généalogie et
produit **un seul fichier HTML autonome**, hors ligne, plus un dossier de
fiches individuelles. Rien d'autre. Pas de cadre applicatif, pas de base de
données, pas de dépendance réseau.

**La machine du projet est `dellg5`** (`C:\Projets\Arbre généalogique`).
Wilfred est un **prêt temporaire**, pour faire une partie de la programmation
avec Qwen et économiser des jetons. Le projet n'a pas vocation à y demeurer, et
aucune règle ne doit être dérivée de ses limites.

**L'arbre par défaut est celui de Samuel** (`genealogie_samuel.json`), depuis
`C-016`. L'objectif est d'y verser le plus d'informations possibles et de le
faire remonter jusqu'aux plus lointains ancêtres.

### Les six interdits

1. **Ne jamais inventer une donnée généalogique.** Un trou se consigne en
   « point à vérifier », il ne se comble pas. Un enfant inventé serait
   indétectable dans dix ans.
2. **Ne jamais supprimer un fichier.** Renommer, déplacer, signaler — jamais
   effacer. Les fiches orphelines sont signalées et laissées en place.
3. **Ne jamais modifier `tests/`.** Le contrat est scellé par empreinte SHA256
   (`outils/empreinte.py --poser`).
4. **Le générateur ne fait aucun appel réseau, et tout export destiné à la
   famille s'ouvre par double-clic, sans serveur, sans installation, hors
   ligne.** Reformulé le 16 octobre (`D-004`) : un serveur local sur le poste
   de travail n'est pas restreint. **La contrainte porte sur ce qui est
   exporté, pas sur l'environnement de développement.**
5. **Ne jamais déclarer terminé sans tests au vert.**
6. **Ne jamais laisser les données d'une branche entrer dans l'export d'une
   autre** — par règle de parcours, jamais par filtre après coup.

### Conventions de travail

- **Valider avant d'écrire, jamais après.** Un script de correctif qui écrit
  puis vérifie a déjà livré le fichier cassé (`C-012` / `C-013`). Tout patch
  Python finit par `ast.parse()` **avant** `write_text()`.
- **Toute intervention est journalisée** sous un code `C-xxx` dans
  `journal/<date>_Sxx.md`, inscrite dans `journal/INDEX.md`, et commitée avec
  ce code en tête du message.
- **Tout script déterministe est accompagné d'un `.bat` glisser-déposer.**
  Les `.bat` doivent être en **CRLF** : `cmd.exe` casse sur les étiquettes
  avec des fins de ligne Unix.
- **Niveaux de certitude** sur chaque fait : `attestee`, `approximative`,
  `deduite`, `divergente`, `incoherente`, `inconnue`. Seul `attestee`
  s'affiche sans marque.

---

## 2 · Ce que la séance 4 a fait

### `C-017` — Cinq contributions appliquées, portrait réparé, fratrie visible

Les cinq fichiers `ajouts-*.json` de Sébastien ont été appliqués. Deux
d'entre eux étaient **identiques au bit près** (`62e4d4dd4d17`) : le garde-fou
d'idempotence a refusé le second — premier essai réussi sur des données
réelles.

Deux correctifs :

- **Le portrait était choisi par hasard.** Les huit photos de Samuel se
  rangeaient en `.jpg`, son portrait en `.png`, et `trouver_photo` essaie
  `.jpg` d'abord : c'est l'ordre alphabétique des extensions qui désignait le
  visage. Le **nom nu de fichier est désormais réservé au portrait** ; une
  photo de galerie va toujours dans un emplacement numéroté.
- **La fratrie était invisible.** Un arbre ascendant ne remonte que par les
  ancêtres, et un frère n'en est pas : Vincent, les oncles Trịnh et les onze
  frères et soeurs de Fernande étaient dans les données et absents de l'écran.
  Le nœud montant porte maintenant sa fratrie, en ordre de naissance, le
  personnage de la lignée à son rang réel, et le trait vers l'enfant vise
  cette personne et non le milieu de la rangée.

### `C-018` — Le douzième enfant était à la page suivante

Sébastien a signalé l'absence de Paul-Émile Jean. Il n'était pas perdu :

```
p. 278, dernière entrée :  Fernande Jean, b. le 01-03-1948
p. 279, PREMIÈRE ligne  :  Jos. Paul-Émile Jean, b. le 22-07-1951
```

La liste des douze enfants franchit la fin de page, et le relevé s'est arrêté
avec la page. **La veille, l'écart 12 contre 11 avait été traité comme une
lacune de la source ; c'en était une du relevé.** Leçon consignée : *un compte
annoncé qui ne tombe pas juste désigne la page suivante avant de désigner un
enfant disparu.* Le point `p9` n'est pas effacé — il passe en « lacune
comblée » et garde la trace de l'erreur.

**Et un défaut d'affichage antérieur, révélé au passage** : le contrôle
navigateur écoute désormais **la console** et non plus seulement `pageerror`.
Il a montré `translate(NaN, 695.89)` sur la vue entière. `ancNode` se cherche
dans `n.enfants` au complet alors que `placerV` ne descend que par `enf(n)`,
les niveaux ouverts ; l'ancêtre marqué (`pierre-jean-1645`) se trouve neuf
générations au-dessus de la profondeur ouverte, donc jamais placé, donc sans
pivot. En arbre montant, la vue s'ouvre désormais sur **le pivot** — ce que la
demande d'origine voulait dire : « Samuel reste centré à chaque ouverture ».

### `C-019` — Le serveur ouvrait la mauvaise généalogie

```python
arbres = sorted(RACINE.glob("arbre_*.html"))   # -> arbre_jean.html
```

`Serveur_Local.bat` ouvrait **`arbre_jean.html`** — le premier arbre du projet,
et l'arbre par défaut jusqu'au 16 octobre seulement. On arrivait sur la
mauvaise généalogie, sans message. Corrigé : l'arbre par défaut d'abord, sinon
le plus récemment généré. `docs/COMMENT-AJOUTER.md` documente les deux chemins
de contribution.

### `C-020` — `Generer_Arbre.bat` ne montrait pas son résultat

Le `.bat` fabriquait le fichier et s'arrêtait là : on appuyait sur une touche,
la fenêtre se fermait, l'écran était comme avant. Il ouvre maintenant ce qu'il
produit — par le serveur local s'il tourne, sinon le fichier, en disant la
différence. Les six `.bat` sont passés en CRLF.

**Deux fois dans la même journée, un tri alphabétique a choisi à la place de
l'intention** : l'ordre des extensions pour le portrait, l'ordre des noms pour
l'arbre servi. *Un tri n'est pas une préférence ; là où il en faut une, il faut
l'écrire.*

---

## 3 · État à la fin de la séance

```
genealogie_samuel.json   107 personnes · 33 unions · 17 points à vérifier
branches déclarées       jean (bleu) · trinh (vert) · gagne (violet)
tests/contrat.py         51 réussis · 0 échoués · 5 sautés (Playwright absent)
git                      21 commits, HEAD = 4c44334 [C-020]
Scans OCR                3,5 Mo — 290 pages océrisées, 2 documents
transcription            1,7 Mo — 4 143 personnes lues par l'analyseur
```

**La lignée Jean est complète sur 13 générations**, de Vivien Jean (vers 1580,
région de La Rochelle) jusqu'à Samuel. Le chaînon manquant a été trouvé le
16 octobre : l'acte de mariage de 1742, transcrit mot pour mot à la page 22,
établit la filiation de la 3ᵉ vers la 2ᵉ génération.

**Les deux livres se confirment l'un l'autre en s'écorchant** : le livre des
Jean écrit « Sébastien Trink » et « Hieu Duc Trink » ; le livre des Trịnh écrit
« Fernance Jeanne ». Ces erreurs sont conservées dans le champ `variantes` —
ce sont elles, la clé de rapprochement.

---

## 4 · Défauts ouverts — à traiter en premier

Trouvés en fin de séance, **non corrigés**. Sébastien a produit deux fichiers
de contribution vides en explorant les fiches (`ajouts-trinh-tan-tai-1941.json`
et `ajouts-truong-thi-kha.json`, 140 octets chacun, aucun contenu). Ils sont
**en attente d'application** — ne pas les appliquer : ils n'ajouteraient rien
tout en étant marqués comme appliqués.

### D-1 · « modifier » ouvre une boîte vide et efface la valeur affichée

`src/generer_arbre.py`, `demanderFait()` :

```js
i.value = AJOUTS.faits[cle] || "";          // <- toujours vide au premier clic
...
if(v) AJOUTS.faits[cle]=v; else delete AJOUTS.faits[cle];
dd.textContent = v || "—";                  // <- efface la date affichée
```

`AJOUTS.faits` ne contient que les ajouts **en attente**, jamais la valeur
actuelle issue des données. Au premier clic sur « modifier », la boîte s'ouvre
donc **vide** alors que la fiche affiche une date réelle. Si on valide sans
rien saisir, rien n'est enregistré **et la date affichée devient « — »**.
La fiche ment sur les données jusqu'au rechargement.

*Correctif : pré-remplir avec la valeur affichée, et ne jamais remplacer
l'affichage par « — » quand la saisie est vide — restaurer la valeur d'origine.*

### D-2 · Une recette vide compte comme un ajout et ne peut pas être retirée

Reproduit au navigateur :

```
clic « + Ajouter une recette »
  -> AJOUTS.recettes = [{titre:"", texte:""}]
  -> barre : « 1 ajout en attente »
  -> aucun bouton de suppression n'existe dans la fiche
```

Le seul moyen de faire disparaître la barre est d'enregistrer — ce qui produit
un fichier de contribution sans rien d'utilisable. C'est vraisemblablement ce
qui s'est passé pour les deux fichiers vides.

*Correctif : un bouton de retrait par recette, et ne compter une recette que
si son titre ou son texte n'est pas vide.*

### D-3 · `Generer_Arbre.bat` n'a pas été exécuté

Réécrit en `C-020`, **relu ligne à ligne mais jamais lancé** : l'atelier
disponible sur dellg5 est un shell Linux, `cmd.exe` n'y existe pas. Deux
défauts y ont été trouvés à la relecture (fins de ligne LF, et une détection
de Python sans parenthèses où `cmd` coupe sur `&&` avant d'évaluer le `if`,
ce qui écrasait `py -3` par `python`). Le premier double-clic de Sébastien est
le test.

---

## 5 · Travaux en attente

| Quoi | Où en est-ce |
|---|---|
| Les douze enfants de Johnny Jean, les seize de Michel Jean | dans l'OCR, pas versés |
| Le reste des 290 pages océrisées | analyseur écrit, versement partiel |
| Branches **Dionne** et **Gagné** (côté Valérie) | vides |
| Rapport de couverture des pages (phase 2) | spécifié, non écrit — première tâche idéale pour Qwen |
| `Q-01` où vivent les recettes | ouverte — ne pas dupliquer le projet « Livres de recette Famille Trinh » |
| `Q-03` forme du `.bat` d'export | ouverte |
| `Q-04` les branches Dionne/Gagné font-elles l'objet d'un export | ouverte |
| `Q-06` quatre lacunes vietnamiennes (p. 53, 54, 75, 86) | à vérifier, jamais établies |
| `_essai_a_jeter/` à la racine | à jeter par Sébastien (interdit 2) |
| `arbre_samuel_fiches/dien-thi-tran.html` | fiche orpheline, signalée, laissée en place |

---

## 6 · Comment lancer les choses

```
Serveur_Local.bat          serveur sur 127.0.0.1:8731, ouvre l'arbre de Samuel
                           -> laisser la fenêtre ouverte ; c'est le serveur
Generer_Arbre.bat          régénère, puis ouvre (par le serveur s'il tourne)
Generer_Arbre.bat <json>   glisser-déposer : génère depuis un autre jeu
Appliquer_Ajouts.bat       glisser-déposer un ou plusieurs ajouts-*.json
Generer_Version_Partageable.bat   export expurgé pour la famille
Tester.bat                 contrat complet
Collecter_Panne.bat        archive de diagnostic
```

**Le libellé du bouton d'une fiche est le voyant :** « Enregistrer **dans le
projet** » = servie par le serveur, l'écriture est directe. « Enregistrer **mes
ajouts** » = ouverte en `file://`, elle rendra un fichier à glisser sur
`Appliquer_Ajouts.bat`. C'est **une seule page** qui constate comment elle a
été ouverte : deux versions divergeraient, et c'est celle qu'on teste le moins
qui partirait chez la parenté.

### Ce que le mécanisme d'ajouts refuse

- écraser un fait **attesté** par une saisie à la main ;
- écraser une photo — un second portrait se range à côté ;
- appliquer deux fois le même fichier — l'empreinte SHA256 est retenue dans
  `photos/_ajouts_appliques.json`.

---

## 7 · Pièges rencontrés, à ne pas refaire

- **Les règles CSS de branche doivent être déclarées après `.puce.directe`**,
  sinon elles sont écrasées à spécificité égale. L'erreur s'est produite trois
  fois ; l'arbre s'affiche entièrement doré.
- **Un test de navigateur qui clique à côté ment.** Deux fois un contrôle a
  rapporté « le bouton ne fait rien » alors que `elementFromPoint` renvoyait
  `null` : c'était le test qui était faux, pas le code. Utiliser de vrais clics
  de souris, jamais des événements synthétiques.
- **Écouter la console, pas seulement `pageerror`.** `translate(NaN)` ne lève
  aucune erreur de script : la page s'affiche, simplement décalée.
- **Un processus d'arrière-plan ne survit pas à un appel de shell distant.**
  Les passes longues (OCR) doivent être reprenables et tourner au premier plan.
- **Doublon n'est pas incohérence.** Sur dix-neuf « incohérences » de l'OCR,
  sept étaient des doublons de joints de lot avec des chiffres corrects.
