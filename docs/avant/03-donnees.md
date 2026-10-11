# 03 — Données

Un seul fichier d'entrée, en JSON, encodé en UTF-8. C'est la source unique : tout ce qui s'affiche en sort, et rien ne s'ajoute ailleurs.

## Vue d'ensemble

```json
{
  "meta":      { "titre": "…", "sous_titre": "…", "carte": { … } },
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
  "sources":   ["Michel Jean, p. 7"]
}
```

| Champ | Sens |
|---|---|
| `pays` | `"fr"` resté en France, `"nf"` passé en Nouvelle-France. Détermine la couleur de l'anneau. |
| `lignee` | sur la chaîne d'ascendance directe. Anneau or, et cible du filtre « Lignée directe ». |
| `ancetre` | l'ancêtre canadien. Un seul par arbre. Sert de point de cadrage à l'ouverture. |
| `lacune` | renvoie à un `problemes[].id` : le rattachement de cette personne n'est pas documenté. Affichée détachée, en pointillé. |
| `marquants` | lignes courtes et narratives affichées sur la carte flottante. Trois ou quatre au plus. |
| `notes` | remarques n'appartenant à aucune rubrique. |
| `sources` | **obligatoire** : le contrôle `T-13` le vérifie. |

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

## Jeux d'exemple

Les tests tournent sur `tests/donnees/`, jamais sur les données réelles (H-04).

- **`exemple_fiche_dense.json`** — trois personnages fictifs, les six types de sections, deux sections confidentielles. Éprouve la richesse d'une fiche.
- **`exemple_formes.json`** — huit personnes, formes particulières : personne sans parents, personne à deux unions, enfant mort en bas âge, nœud détaché, lieu sans lien, date de certitude inconnue. Éprouve la disposition de l'arbre.

Un nouveau cas de figure appelle **un ajout à ces jeux**, pas une modification des données réelles.
