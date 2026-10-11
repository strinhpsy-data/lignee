# 04 — Parcours et états

Trois produits : l'arbre, fichier unique ; une page par personne ; et, à partir
de la phase 2, un export par branche. Le lien « En savoir plus » mène du premier
au deuxième.

---

## A. L'arbre

### A1 — Ouverture

L'arbre s'ouvre cadré sur **le pivot** — Samuel —, à une échelle lisible, et non ajusté à l'écran : à 60 personnes, un ajustement global rend les noms illisibles. À quatre branches, il le rendrait absurde.

Jusqu'à doc-v1, le cadrage se faisait sur l'ancêtre canadien. Il appartient désormais au pivot (H-19, H-20) : « Samuel reste centré à chaque ouverture de l'arbre » (`D-002.6`).

| État | Comportement attendu |
|---|---|
| normal | médaillons dessinés, lignée directe en or, **vue centrée sur le pivot** |
| pivot absent du fichier | comportement de doc-v1 : cadrage sur l'ancêtre. Aucune erreur. |
| pivot désignant un inconnu | **la génération s'arrête**, code non nul, identifiant fautif nommé |
| données vides | aucune personne : la page s'ouvre sans erreur JavaScript et n'affiche rien d'autre que la barre du haut |
| erreur | aucune : les données sont validées à la génération, pas au chargement |

Contrôles : `T-29` (aucune erreur JavaScript), `T-30` (médaillons dessinés).

### A2 — Déplacement et zoom

Glisser déplace, la molette zoome au curseur, `Recadrer` ajuste tout.

**Le seuil de glissement est le point délicat.** En deçà de quatre pixels, c'est un clic ; au-delà, un glissement. Sans ce seuil, un tremblement de la main transforme un clic en déplacement et la fiche ne s'ouvre jamais.

**Ne jamais employer `setPointerCapture` sur la toile.** La capture détourne l'événement de clic vers la toile, et les médaillons cessent de répondre. Ce défaut est déjà survenu ; le commentaire est dans le code.

Contrôle : `T-33` (un glissement referme la fiche).

### A3 — Clic sur un médaillon

Une carte flottante s'ouvre, collée au médaillon, et bascule de côté si elle déborde de l'écran.

Elle contient : portrait ou monogramme, nom, dates, surnom ; les étiquettes de pays et de lignée ; naissance, décès, métier, lieu, union, parents, enfants — les noms étant cliquables ; les faits marquants ; **toutes les incohérences qui visent cette personne, en entier** ; et en bas « En savoir plus » avec le compte de ce qui attend.

| État | Comportement attendu |
|---|---|
| personne complète | toutes les rubriques |
| personne vide | nom et étiquettes seulement ; aucune rubrique vide affichée |
| sans portrait | monogramme à initiales, même cadre, même taille |
| avec confidentiel | bandeau « Confidentiel » ; le contenu n'apparaît pas sur la carte |

Contrôles : `T-31` (un clic réel ouvre la fiche), `T-32` (le lien existe), `T-32b` (il mène à un fichier existant).

**Le clic doit être éprouvé par un vrai clic de souris.** Un événement simulé contourne précisément les mécanismes qui cassent le clic, et passe au vert sur un arbre mort.

### A4 — Recherche, filtre, bascules

La recherche filtre les médaillons et affiche un compte. « Lignée directe » estompe tout le reste. « Problèmes » ouvre le relevé. « Portraits / Cartes » change de vue sans perdre la sélection. Le bouton de thème bascule clair et sombre.

| État | Comportement attendu |
|---|---|
| recherche sans résultat | tous les médaillons estompés, compte à zéro, aucune erreur |
| recherche vidée | tout revient, y compris si un filtre était actif |

---

## B. La page d'une personne

Ouverte dans un nouvel onglet depuis « En savoir plus ». Fichier autonome dans `arbre_*_fiches/`.

Structure : bandeau de retour vers l'arbre ; portrait, nom, dates, étiquettes ; sommaire en marge sur écran large ; puis Synthèse, Faits marquants, Notes, les sections versées, Relations, À vérifier, Source.

| État | Comportement attendu |
|---|---|
| personne complète | toutes les rubriques, sommaire garni |
| personne vide | synthèse réduite, sommaire court ; la page s'ouvre quand même |
| section confidentielle | repliée **et** voilée ; deux gestes délibérés pour l'afficher |
| version partageable | la section n'existe pas dans le fichier |

**Les relations sont des liens entre pages.** Parents, fratrie, conjoints, enfants mènent chacun à leur propre page. Le contrôle `T-24` vérifie qu'aucun ne pointe dans le vide.

### A5 — Le sablier

Phase 1, étape 1.3. L'ascendance monte au-dessus du pivot, la descendance descend
en dessous, et le pivot est dessiné **une seule fois**, à la taille.

| État | Comportement attendu |
|---|---|
| pivot sans descendance | **aucun espace vide sous lui** : la disposition s'affaisse et le pivot se retrouve au pied de l'arbre |
| pivot avec descendance | les deux moitiés, le pivot au centre |
| personne atteignable dans les deux sens | dessinée dans les deux ; un ensemble `vu` **par direction** |
| parent inconnu | aucun nœud vide, aucune case en attente |

Le troisième cas est celui qui casse silencieusement. Avec un seul ensemble `vu`,
une personne atteinte en montant n'est plus dessinée en descendant : le lien
disparaît sans erreur, sans message, et le dessin paraît correct. C'est le même
genre de défaut que le clic mort de la séance 1 — invisible à la relecture,
visible seulement à l'épreuve.

---

## C. La génération

| État | Comportement attendu |
|---|---|
| succès | compte des personnes, unions, sections, fiches, portraits intégrés |
| JSON mal formé | ligne et colonne fautives, puis arrêt avec un code non nul |
| fichier absent | message clair, code non nul |
| fiche orpheline | **signalée, jamais supprimée**, l'utilisateur décide |
| confidentiel présent | avertissement explicite en fin de génération |

Contrôles : `T-17` (sortie sans erreur), `T-19` (aucune suppression), `T-02` et `T-03` (lecture et forme du JSON).

---

## D. L'export d'une branche

Phase 2. Spécification complète dans `07-branches-export.md` ; ici, seulement ce
que l'utilisateur voit.

Un `.bat` par branche, ou un `.bat` qui demande laquelle — à trancher à
l'ouverture de la phase 2. Dans les deux cas Sébastien ne tape aucune commande.

| État | Comportement attendu |
|---|---|
| succès | un dossier par branche, nommé sans ambiguïté, avec son arbre, ses fiches et sa page d'invitation |
| tête de branche absente des données | **arrêt**, code non nul, branche nommée |
| tête qui n'est pas un grand-parent du pivot | **arrêt**, code non nul |
| branche sans `retour` | export produit, **sans** page d'invitation |
| section `prive` présente | retirée physiquement, et la génération le dit en clair |

**Ce que l'utilisateur doit pouvoir vérifier d'un coup d'œil avant d'envoyer :**
le nom de la branche, le nombre de personnes, le nombre de nœuds de frontière, et
une ligne explicite confirmant qu'aucune section confidentielle ne subsiste. Un
export se relit avant de partir, et il ne se rappelle pas.

Le programme n'envoie rien.
