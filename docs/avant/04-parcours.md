# 04 — Parcours et états

Deux produits : l'arbre, fichier unique, et une page par personne. Le lien « En savoir plus » mène de l'un à l'autre.

---

## A. L'arbre

### A1 — Ouverture

L'arbre s'ouvre cadré sur l'ancêtre, à une échelle lisible, et non ajusté à l'écran : à 60 personnes, un ajustement global rend les noms illisibles.

| État | Comportement attendu |
|---|---|
| normal | médaillons dessinés, lignée directe en or, vue centrée sur l'ancêtre |
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
