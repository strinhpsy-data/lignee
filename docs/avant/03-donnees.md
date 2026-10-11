# 03 — Données

Un seul fichier d'entrée, en JSON, encodé en UTF-8. C'est la source unique : tout ce qui s'affiche en sort, et rien ne s'ajoute ailleurs.

## Vue d'ensemble

```json
{
  "meta":      { "titre": "…", "sous_titre": "…",
                 "pivot": "identifiant-de-personne",
                 "branches": [ … ],
                 "carte": { … } },
  "problemes": [ … ],
  "personnes": { "identifiant": { … } },
  "unions":    [ … ],
  "racines":   ["identifiant-d-union"],
  "detaches":  ["identifiant-de-personne"]
}
```

Les identifiants sont des chaînes libres, en minuscules, sans accent ni espace : `pierre-jean-1645`. **Ils ne changent jamais** — ils servent de nom de fichier pour les portraits (`photos/pierre-jean-1645.jpg`) et pour les pages produites.

## Une personne

```json
"pierre-jean-1645": {
  "prenom": "Pierre", "nom": "Jean", "sexe": "M",
  "surnom": "dit Godon",
  "variantes": ["Jehan"],
  "pays": "nf",
  "lignee": true,
  "ancetre": true,
  "lacune": "p6",
  "naissance":  { "texte": "…", "certitude": "attestee", "tri": 1645, "note": "…" },
  "bapteme":    { … },  "deces": { … },  "sepulture": { … },
  "metiers":   ["maréchal-ferrant"],
  "lieux":     ["La Rochelle"],
  "marquants": ["…"],
  "notes":     ["…"],
  "sections":  [ … ],
  "galerie":   [ { "fichier": "pierre-jean-1645-2.jpg", "legende": "…" } ],
  "sources":   ["Michel Jean, p. 7"]
}
```

| Champ | Sens |
|---|---|
| `pays` | `"fr"` resté en France, `"nf"` passé en Nouvelle-France. Détermine la couleur de l'anneau. |
| `lignee` | sur la chaîne d'ascendance directe. Anneau or, et cible du filtre « Lignée directe ». |
| `ancetre` | l'ancêtre fondateur d'une branche. **Étiquette descriptive seulement.** Depuis doc-v2, le cadrage d'ouverture appartient au pivot (H-20), et il y a autant d'ancêtres fondateurs que de branches. |
| `lacune` | renvoie à un `problemes[].id` : le rattachement de cette personne n'est pas documenté. Affichée détachée, en pointillé. |
| `marquants` | lignes courtes et narratives affichées sur la carte flottante. Trois ou quatre au plus. |
| `notes` | remarques n'appartenant à aucune rubrique. |
| `sources` | **obligatoire** : le contrôle `T-13` le vérifie. |
| `galerie` | portraits supplémentaires, **facultatif** (H-17). Voir « La galerie » plus bas. |

### Les faits datés

`naissance`, `bapteme`, `deces`, `sepulture` ont tous la même forme :

```json
{ "texte": "dimanche 19 février 1645, église Saint-Barthélémy, La Rochelle",
  "certitude": "attestee",
  "tri": 1645,
  "note": "Parrain : Pierre Jousmier, voiturier." }
```

`texte` s'affiche tel quel. `tri` est l'année employée pour calculer « 1645 – 1664 » sous le nom. `note` est le détail secondaire.

### Les niveaux de certitude

C'est le cœur de la méthode du projet. Le contrôle `T-12` refuse toute valeur hors de cette liste.

| Valeur | Sens | Affichage |
|---|---|---|
| `attestee` | la source le donne tel quel, sans réserve | aucune marque |
| `approximative` | « vers », « environ », « entre X et Y », « avant/après » | `approx.` |
| `deduite` | calculée, non écrite dans la source | `déduit` |
| `divergente` | la source se contredit elle-même | `divergent` |
| `incoherente` | contredit un autre fait établi | `incohérent` |
| `inconnue` | mentionnée mais non datée | `inconnu` |

**Seul `attestee` s'affiche sans marque.** C'est voulu : l'incertitude doit se voir au moment où on lit la donnée, pas dans une annexe.

## Une union

```json
{ "id": "u-ancetre",
  "conjoints": ["pierre-jean-1645", "francoise-favreau"],
  "lignee": true,
  "mariage": { "texte": "08-07-1668, église St-Sauveur, La Rochelle", "certitude": "attestee" },
  "contrat": { "texte": "22-01-1685, devant le notaire Paul Vachon" },
  "notes":   ["…"],
  "enfants": ["identifiant", "identifiant"] }
```

`conjoints` contient une ou deux personnes. `enfants` peut être vide : une union dont la descendance n'est pas documentée reste une union.

**Contraintes vérifiées :** toute personne citée existe (`T-05`), personne n'a deux couples de parents (`T-06`), personne n'est son propre parent (`T-07`), aucun cycle de filiation (`T-08`).

## Les points à vérifier

```json
{ "id": "p1",
  "type": "incoherence",
  "gravite": "forte",
  "personnes": ["marthe-joslain"],
  "pages": "5, 6",
  "description": "…" }
```

Les contradictions de la source **ne sont pas tranchées d'office** : elles sont consignées ici, s'affichent en entier sur la fiche des personnes visées, et attendent un arbitrage sur pièces.

`type` est libre et sert d'étiquette : `incoherence`, `divergence`, `lacune`, `deduction`, `ambiguite`. `gravite` vaut `forte`, `moyenne` ou `faible` et ne change que la couleur.

## Les sections

Un tableau `sections` par personne accueille tout ce qui déborde du cadre généalogique. Chaque section se replie et porte son nombre d'entrées.

| `type` | `contenu` |
|---|---|
| `texte` | chaîne, ou liste de paragraphes |
| `liste` | liste de chaînes |
| `faits` | liste de `{ q, r, note?, certitude? }` |
| `chrono` | liste de `{ date, titre, detail?, lieu? }` |
| `tableau` | `{ colonnes: [...], lignes: [[...]] }` |

Champs communs : `titre`, `intro`, `source`, `ouvert`, et `prive`.

**`"prive": true`** signale une section confidentielle. Elle n'apparaît jamais sur la carte flottante, elle est voilée sur la page complète, et `Generer_Version_Partageable.bat` la **retire physiquement** du fichier produit. Le contrôle `T-27` le vérifie en cherchant le texte dans la sortie : s'il le trouve, le contrôle échoue.

## La table cartographique

```json
"carte": {
  "actif": true,
  "service": "https://www.google.com/maps/search/?api=1&query=",
  "lieux":      { "Beauport (juillet 1671)": "Beauport, Québec, QC, Canada" },
  "toponymes":  { "Cap-de-la-Madeleine": "Cap-de-la-Madeleine, Trois-Rivières, Québec, Canada",
                  "Nouvelle-France": "" }
}
```

`lieux` : correspondance exacte pour la rubrique Lieux. `toponymes` : noms reconnus à l'intérieur des textes libres, les plus longs essayés d'abord, une seule occurrence par bloc.

**Une valeur vide désactive le lien.** La requête ne part jamais du texte brut : il contient des dates entre parenthèses, et « Champlain », « Gentilly » ou « Beauport » existent des deux côtés de l'Atlantique.

## Le pivot et les branches

Ajoutés par doc-v2. Ils répondent aux points 1 et 3 de la demande `D-002`.

```json
"meta": {
  "pivot": "samuel-trinh",
  "branches": [
    { "id": "jean",   "tete": "fernande-jean",  "titre": "Famille Jean",
      "retour": "Fernande Jean" },
    { "id": "trinh",  "tete": "hieu-duc-trinh", "titre": "Famille Trinh",
      "retour": "l'oncle de Sébastien" },
    { "id": "dionne", "tete": "justine-dionne", "titre": "Famille Dionne" },
    { "id": "gagne",  "tete": "richard-gagne",  "titre": "Famille Gagné" }
  ]
}
```

`pivot` est la personne sur laquelle l'arbre s'ouvre, et le point de rencontre
des deux sens de lecture. **C'est un champ déclaré, jamais déduit** (H-19) : une
règle du genre « la personne la plus jeune » déplacerait le centre de l'arbre
toute seule le jour d'une naissance, sans que personne l'ait demandé.

`branches` déclare les quatre têtes. Chacune doit être un **grand-parent du
pivot**, et cela se vérifie à la génération : une déclaration non contrôlée est
une donnée comme une autre. `retour` est facultatif — sans lui, pas de page
d'invitation.

**L'appartenance à une branche ne s'écrit jamais sur une personne** (H-13). Elle
se calcule, à chaque génération, selon les trois règles de parcours de
`07-branches-export.md`. Un champ `"branche"` posé à la main se tairait le jour
où une filiation est corrigée — et il y en aura, le fichier contient déjà huit
contradictions de source.

**Un seul fichier pour les quatre branches** (H-22). Les exports sont des
sorties ; rien ne se ressaisit depuis un fichier exporté.

## La galerie

Un portrait principal : `photos/<identifiant>.jpg`, comme aujourd'hui. C'est lui
qui s'affiche sur le médaillon.

Les portraits supplémentaires suivent la même convention de nom, numérotés :
`photos/<identifiant>-2.jpg`, `-3.jpg`, et ainsi de suite. Ils sont **découverts
automatiquement** ; rien à déclarer. C'est voulu : un parent qui envoie trois
photos n'a pas à éditer un fichier JSON, et les identifiants, eux, ne changent
jamais.

Le champ `galerie` ne sert qu'à **légender** une photo, ou à en forcer l'ordre.
Une photo sans légende n'a pas besoin d'y figurer.

Un fichier déclaré mais absent ne fait pas échouer la génération : il est
signalé, comme une fiche orpheline.

## Jeux d'exemple

Les tests tournent sur `tests/donnees/`, jamais sur les données réelles (H-04).

- **`exemple_fiche_dense.json`** — trois personnages fictifs, les six types de sections, deux sections confidentielles. Éprouve la richesse d'une fiche.
- **`exemple_formes.json`** — huit personnes, formes particulières : personne sans parents, personne à deux unions, enfant mort en bas âge, nœud détaché, lieu sans lien, date de certitude inconnue. Éprouve la disposition de l'arbre.

Un nouveau cas de figure appelle **un ajout à ces jeux**, pas une modification des données réelles.
