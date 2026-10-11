# 07 — Branches et export

Ce document répond aux points 3, 4 et 6 de la demande `D-002`. Il décrit **ce
qu'est une branche**, **ce que contient une branche exportée**, et **pourquoi
les familles ne se recoupent pas**.

---

## 1. Une branche n'est pas un champ

Il serait tentant d'écrire `"branche": "jean"` sur chaque personne. C'est à
éviter, pour une raison qui se vérifie : le jour où une filiation est corrigée —
et il y en aura, le fichier contient déjà huit contradictions de source — la
personne change de branche et son étiquette, elle, ne change pas. On obtient
alors un fichier qui se contredit sans qu'aucun contrôle ne le voie.

**La branche est donc toujours calculée**, à chaque génération, à partir des
liens de filiation. Rien à maintenir, rien à désynchroniser.

## 2. Les quatre têtes de branche

Elles sont **déclarées** dans `meta.branches`, et **vérifiées** à la génération.

```json
"branches": [
  { "id": "jean",   "tete": "fernande-jean",   "titre": "Famille Jean",
    "retour": "Fernande Jean" },
  { "id": "trinh",  "tete": "hieu-duc-trinh",  "titre": "Famille Trinh",
    "retour": "l'oncle de Sébastien" },
  { "id": "dionne", "tete": "justine-dionne",  "titre": "Famille Dionne" },
  { "id": "gagne",  "tete": "richard-gagne",   "titre": "Famille Gagné" }
]
```

Déclarées et non déduites, pour la même raison que le pivot : une règle du genre
« les quatre personnes à la deuxième génération au-dessus du pivot » se tairait
le jour où une de ces quatre personnes manque, ou le jour où le pivot change.

Vérifiées, parce qu'une déclaration non contrôlée est une donnée comme une autre :
chaque `tete` doit être un **grand-parent du pivot**, atteignable en remontant
exactement deux générations. Sinon, la génération s'arrête.

`retour` est le nom de la personne à qui les parents renvoient ce qu'ils ont
ajouté. Absent, l'invitation ne s'affiche pas : les branches Dionne et Gagné
n'ont pas de destinataire décidé (`D-002`, point 4).

## 3. Le calcul, en trois règles

Pour une tête de branche `b` :

1. **On monte par le sang.** On remonte de `b` vers ses parents, puis vers les
   leurs, aussi loin que les données vont. Cela donne l'ensemble des ancêtres
   `A`, qui contient `b`.
2. **On descend librement.** Tout descendant d'un membre de `A` appartient à la
   branche. C'est ce qui fait entrer les oncles, tantes, cousins et petits-cousins
   — ceux à qui le fichier est destiné.
3. **On ajoute les conjoints, on ne remonte jamais depuis eux.** Le conjoint
   d'un membre entre dans la branche ; ses propres parents, non.

La troisième règle est la plus importante des trois, et c'est elle qui règle le
point 6 de la demande.

## 4. Pourquoi les familles ne se recoupent pas

Le point 6 dit : « ça ne sert à rien d'envoyer les informations de la famille
Trinh à la famille Jean et vice-versa. »

On pourrait le traiter par un filtre appliqué après coup — construire l'arbre
complet, puis retirer ce qui ne va pas. **Ce serait la mauvaise façon**, parce
qu'un filtre s'oublie : il suffit d'un nouveau mode d'affichage qui court-circuite
le filtre pour que les données traversent.

La règle 3 le rend structurel. Dans l'export Jean :

- Fernande Jean est une tête de branche : elle et ses ancêtres y sont.
- Sébastien est son fils, donc descendant d'un ancêtre : il y est en entier.
- Hieu-Duc Trinh est le conjoint de Fernande : il y figure, **et le parcours
  s'arrête à lui**. Ses parents ne sont jamais atteints, donc jamais écrits.
- Valérie Gagné est la conjointe de Sébastien : même chose.
- Samuel est le fils de Sébastien, donc descendant : il y est en entier.

Aucune donnée Trinh n'est retirée de l'export Jean. Elle n'y entre jamais. La
différence compte le jour où quelqu'un ajoute une fonction sans relire ce
document.

## 5. La frontière

Une personne qui entre dans une branche uniquement comme conjointe, et dont
l'ascendance n'en fait pas partie, est un **nœud de frontière**.

| | Membre | Nœud de frontière |
|---|---|---|
| prénom, nom, surnom | oui | **oui** |
| le lien d'union | oui | oui |
| dates, lieux, métiers | oui | non |
| portrait | oui | non |
| faits marquants, notes, sections | oui | non |
| page complète dans `*_fiches/` | oui | **aucune** |
| ses parents | oui | **jamais atteints** |

Le test d'appartenance est le seul critère : si une personne est membre par le
sang **et** conjointe — ce qui arrive avec un mariage entre cousins, fréquent en
Nouvelle-France — elle n'est pas un nœud de frontière. Elle figure en entier.

Visuellement, le nœud de frontière est un médaillon sans portrait, au trait
interrompu, sans anneau de pays : il se lit comme « quelqu'un d'une autre
famille », et non comme « quelqu'un dont on n'a pas la photo ».

## 6. Un export est toujours une version partageable

**Il n'existe pas d'export de branche complet.** Toute branche exportée passe par
le même retrait physique des sections `prive` que
`Generer_Version_Partageable.bat`, sans exception et sans option pour le
contourner. Le mécanisme existe déjà et le contrôle `T-27` l'éprouve en cherchant
le texte confidentiel dans la sortie.

La raison est simple : un export part de la machine de Sébastien et ne revient
pas. Une option « export complet » serait utilisée un soir de fatigue.

## 7. L'invitation

Chaque export porte une page d'invitation, produite depuis `meta.branches`, qui
dit trois choses et pas davantage :

1. ce que le fichier contient et d'où il vient ;
2. à qui renvoyer ce qu'on souhaite ajouter — la valeur de `retour` ;
3. que **tout est facultatif**. Reprise de `D-002.4` : un parent met ce qu'il
   veut, il peut ne rien mettre, et cela vaut aussi pour les photos et les
   recettes.

Le programme **n'envoie rien**. Il produit un fichier ; Sébastien le transmet.
Aucun accès réseau, ici comme ailleurs (interdit 4).

Ce que l'invitation ne fait pas : réclamer. Le point 5 de la demande énumère des
choses agréables à recevoir — santé, recettes, photos, moments de vie, lieu de
sépulture. Ce sont des rubriques offertes, vides, et une rubrique vide ne
s'affiche pas comme un manque.

## 8. Candidats de tests

À coder quand la phase 1 s'ouvrira, pas avant — la phase 0 doit passer au vert
sur Wilfred d'abord, et on ne mélange pas une migration et une amélioration.

| Ce qui est éprouvé |
|---|
| chaque `tete` déclarée est bien un grand-parent du pivot |
| un nœud de frontière n'a **aucune** page dans le dossier des fiches |
| dans l'export Jean, aucun identifiant de l'ascendance Trinh n'apparaît |
| un export de branche ne contient aucun texte de section `prive` |
| une personne appartenant à deux branches figure en entier dans les deux |
| le parcours ne remonte jamais depuis un conjoint (propriété du parcours) |
| une branche sans `retour` ne produit pas de page d'invitation |
