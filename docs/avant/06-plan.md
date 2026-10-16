# 06 — Plan par phases

Une phase est terminée quand **tous ses tests passent**, pas quand le code paraît juste.

Ils passent sur **dellg5**, la machine du projet. Si une étape a été codée sur Wilfred pendant le prêt, elle revient par le sas et c'est ici qu'elle est reçue : les contrôles navigateur n'y tournent pas, et un harnais à moitié exécuté ne reçoit rien.

---

## Comment Claude et Qwen se partagent une phase

L'empreinte de `tests/` interdit à Qwen de toucher au contrat. Ce n'est pas une
méfiance : c'est ce qui donne au projet sa méthode, et elle vaut d'être nommée.

1. **Claude pose les contrôles** d'une étape, avant qu'une ligne de code existe.
   Ils échouent — c'est normal, c'est même la preuve qu'ils mesurent quelque chose.
2. Claude rescelle l'empreinte et transmet le dépôt.
3. **Qwen rend les contrôles verts** sans pouvoir les modifier.
4. Un contrôle qui semble faux donne une `Q-xx`, jamais une retouche.

Le test précède donc le code **par construction**, et non par discipline. C'est
l'inverse de ce qui s'est passé à la séance 1, où un test écrit après coup est
passé au vert sur un arbre dont les médaillons ne répondaient plus au clic.

---

## Phase 0 — Mise sous protocole

**Ce qui est livré.** Le programme d'aujourd'hui, inchangé, mais sous harnais : dépôt git vivant, journal ouvert, contrat scellé, environnement constaté.

**Pourquoi cette phase existe.** Elle prouve que la boucle tourne — écrire, exécuter, voir, commiter — avant qu'on lui confie quoi que ce soit. Si elle échoue, le problème est dans l'outillage, pas dans le code généalogique, et on le saura tout de suite.

**Tests qui doivent passer :** `T-01` à `T-28` sur les deux jeux d'exemple. `T-29` à `T-34` passent ou s'affichent `SAUTE` selon que Playwright est présent.

**Travail attendu de Qwen :**

1. `git --version`, `git status`, version de Python, présence de Pillow et de Playwright. Consigner en `E-001.1`.
2. Compléter le tableau « À constater au démarrage » de `02-environnement.md`.
3. Lire `docs/avant/` en entier, puis écrire sa reformulation en `E-001.2`.
4. Lancer `Tester.bat`. Consigner la sortie entière.
5. Si tout est vert : commit, et la phase 0 est terminée.
6. Si un contrôle échoue : c'est que l'environnement de Wilfred diffère de celui où le contrat a été écrit. Diagnostiquer, corriger **le code et non le test**, trois tentatives au plus, puis `B-xx`.

**Interdit propre à cette phase.** Aucune amélioration, même évidente. Un défaut d'apparence repéré, une fonction qui manque, une ligne qu'on écrirait autrement : tout cela va dans `docs/apres/11-questions.md` sous un `Q-xx`. On ne mélange jamais une migration et une amélioration — quand quelque chose casse, on ne sait plus laquelle des deux en est la cause.

**Prérequis non rempli à ce jour :** Git n'est pas installé sur Wilfred. Sans lui,
Qwen peut travailler mais ne laisse aucune trace exploitable. C'est le premier
`B-xx` à déclarer si rien n'a changé.

---

## Phase 1 — L'arbre de Samuel

**Cadrée le 2026-10-11** à partir de la demande `D-002`. Aucune étape ne commence
avant que la phase 0 soit verte sur Wilfred.

**Ce qui est livré.** L'arbre s'ouvre centré sur Samuel, se lit vers le haut
comme vers le bas, et sait à quelle branche chaque personne appartient.

**Le constat qui fixe le travail.** Douze endroits du code parcourent les
enfants ; **aucun** ne parcourt les parents. En revanche, l'index inverse existe
déjà — `unionParente` côté navigateur, `union_parente` côté Python. Le lien de
filiation est donc déjà là dans les deux sens ; ce qui manque, c'est de le
parcourir.

### Étape 1.1 — Le pivot

`meta.pivot` désigne une personne. L'arbre s'ouvre cadré sur elle. Rien d'autre
ne change : aucun nouveau parcours, aucune nouvelle vue.

C'est volontairement la plus petite modification de comportement possible. Elle
sert à éprouver la boucle sur un vrai changement, pas à livrer une fonction.

*Candidats de tests :* le champ absent laisse le comportement actuel ; le champ
désignant une personne inexistante **arrête la génération** avec un code non nul ;
le champ valide déplace le cadrage d'ouverture.

### Étape 1.2 — Monter

Un parcours vers le haut, miroir de `construire`, qui prend les conjoints de
`unionParente[id]` là où l'autre prend les enfants.

**Le point délicat est l'ensemble `vu`.** Il faut un ensemble **par direction** :
une personne atteinte en montant ne doit pas empêcher de la dessiner en
descendant. Avec un seul ensemble, le lien disparaît sans erreur, sans message,
et le dessin paraît correct.

*Candidats de tests :* l'ascendance d'une personne à deux parents connus dessine
les deux ; un parent inconnu ne laisse pas de nœud vide ; une personne atteignable
dans les deux sens — mariage entre cousins, fréquent en Nouvelle-France — est
dessinée dans les deux.

### Étape 1.3 — Le sablier

Les deux moitiés autour du pivot, le pivot dessiné **une seule fois**.

**Le piège est la moitié basse vide.** Samuel n'a pas de descendance : un sablier
naïf réserve l'espace quand même et ouvre l'arbre sur un grand blanc. La
disposition doit s'affaisser — Samuel se retrouve alors au pied de l'arbre, et le
sablier n'apparaît visuellement que le jour où il aura des enfants.

*Candidats de tests :* un pivot sans descendance ne produit **aucun espace vide**
sous lui ; le pivot n'est dessiné qu'une fois ; un pivot avec descendance produit
les deux moitiés.

### Étape 1.4 — Les branches

`meta.branches`, la vérification que chaque tête est un grand-parent du pivot, et
le calcul d'appartenance décrit dans `07-branches-export.md`.

Cette étape consomme `ancetre` (H-20) : il perd son rôle de cadrage, déjà reporté
sur le pivot à l'étape 1.1, et devient une étiquette par branche. **Attention** :
le placement des nœuds détachés s'ancre aujourd'hui sur l'ancêtre et aura besoin
d'un autre point d'appui.

*Candidats de tests :* voir `07-branches-export.md`, section 8.

### Étape 1.5 — La galerie

Plusieurs portraits par personne (H-17), là où il n'y en a qu'un aujourd'hui. Le
médaillon en montre un ; la page complète les montre tous.

*Candidats de tests :* une personne sans portrait garde exactement le même cadre
et la même taille qu'une personne qui en a plusieurs — l'arbre ne doit jamais
avoir l'air à moitié fait ; un fichier de portrait absent ne fait pas échouer la
génération.

---

## Phase 2 — Le rapport de couverture

**Cadrée le 2026-10-16** à partir de la demande `D-003`. Spécification
complète dans `08-couverture.md`.

**Elle ne dépend pas de la phase 1.** Aucun fichier commun : le rapport lit
`Scans/_documents.json`, le contenu de `Scans OCR/` et les `sources` du
fichier de données. Il ne touche ni au générateur, ni à la disposition, ni au
modèle de données. La règle de succession des phases ne s'applique donc pas
entre 1 et 2.

**C'est même le meilleur premier vrai travail de Qwen**, et pour une raison
matérielle : il n'exige que Python et la bibliothèque standard. Tout le reste
de ce chantier — l'océrisation — demande poppler et tesseract, dont la
présence sur Wilfred n'est pas établie (`Q-05`).

**Déjà fait, du côté de Claude :** les 407 pages des deux documents sont
océrisées et nommées par numéro de page imprimé dans `Scans OCR/`, avec un
inventaire traçable dans `_inventaire.json`. Il reste à écrire le rapport.

**Candidats de tests :** `08-couverture.md`, section 7. Le contrôle décisif
est celui qui donne une mention de source volontairement tordue et vérifie
qu'aucune page n'en devient « intégrée ».

---

## Phase 3 — L'export de branche

**À ouvrir quand la phase 1 est verte.** Spécification complète dans
`07-branches-export.md`.

Séparée de la phase 1 pour une raison précise : c'est la seule partie du projet
où un défaut **sort de la maison**. Un arbre mal dessiné se corrige ; un fichier
envoyé à douze parents ne se rappelle pas. Elle mérite sa propre phase, ses
propres tests et sa propre relecture.

---

## Phase 4 — Les générations manquantes

**À cadrer avec Claude.** C'était la phase 1 de doc-v1, et sa matière première
existe désormais : les 290 pages de *Michel Jean* sont océrisées. Le chaînon
entre Pierre Jean et Michel Pierre Jean est dans ce texte.

Ce qui relève du code : accueillir un arbre nettement plus grand sans que la
disposition devienne illisible, et sans que la génération s'éternise.

Ce qui n'en relève pas : la transcription elle-même. Elle reste éditoriale, et
le rapport de couverture de la phase 2 est précisément l'instrument qui dira
où elle en est.

**Candidats de tests :** disposition sur plusieurs centaines de personnes ;
temps de génération borné ; repli lisible quand une fratrie compte plus de dix
enfants.

---

## Phase retirée — Reprise des scans

C'était la phase 2 de doc-v1 : « une chaîne de reprise produirait du texte
exploitable à partir des pages numérisées ». **Faite le 2026-10-16** par
`outils/ocr_scans.py`, hors phase, parce qu'elle exigeait des outils absents
de Wilfred.

L'avertissement qu'elle portait s'est vérifié : « trois pages du PDF d'origine
étaient numérisées à l'envers ; une chaîne qui ne détecte pas l'orientation
produira du texte inventé avec aplomb. » Une quatrième page à l'envers a été
trouvée dans le document vietnamien. La chaîne interroge donc l'orientation de
**chaque** page, et pas du lot.

---

## Phase 5 — Impression

**À cadrer.** Une planche grand format, et une fiche imprimable par personne.

---

## Règle commune à toutes les phases

Aucune phase ne commence avant que la précédente soit verte **sur dellg5**, contrôles navigateur compris. On ne construit pas sur un étage qui n'a pas été reçu — et un étage dont la moitié des contrôles ont été sautés n'a pas été reçu.

Et à l'intérieur d'une phase, aucune étape ne commence avant que la précédente
soit verte. Les étapes de la phase 1 sont ordonnées : le cadrage avant le
parcours, le parcours avant le sablier, le sablier avant les branches.
