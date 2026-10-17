# Arbre généalogique de Samuel — branche Jean

> Depuis le cadrage de la phase 1 (`doc-v2`), le projet est l'arbre de
> **Samuel**, autour de qui s'articulent quatre branches : Jean, Trinh,
> Dionne et Gagné. Le fichier de données actuel ne contient que la branche
> Jean ; les trois autres restent à saisir, et c'est un travail de
> transcription, pas de programmation.

> **Ce projet est mené sous le protocole de programmation conjointe v1.0.**
> La documentation de référence est dans `docs/avant/`. Ce LISEZMOI est le
> mode d'emploi pour l'utilisateur ; il ne fait pas autorité sur la
> spécification.
>
> | Pour savoir | Lire |
> |---|---|
> | ce qu'est le projet et ce qui est interdit | `docs/avant/01-fiche-projet.md` |
> | la machine, les dépendances, les pièges | `docs/avant/02-environnement.md` |
> | le format exact des données | `docs/avant/03-donnees.md` |
> | les écrans et leurs états | `docs/avant/04-parcours.md` |
> | l'apparence | `docs/avant/05-apparence.md` |
> | le plan par phases | `docs/avant/06-plan.md` |
> | les branches et l'envoi à la parenté | `docs/avant/07-branches-export.md` |
> | où en est le travail | `docs/apres/09-etat.md` |


## Le dossier

| Élément | Rôle |
|---|---|
| `genealogie_jean.json` | **Les données.** Le seul fichier à modifier à la main. |
| `photos/` | **Les portraits.** Déposez-y les images ; rien d'autre à faire. |
| `src/generer_arbre.py` | Le générateur. Ne contient aucune donnée. |
| `Generer_Arbre.bat` | Double-clic (ou glisser-déposer d'un `.json`) pour tout régénérer. |
| `Tester.bat` | Passe les 36 contrôles du contrat de vérification. |
| `Generer_Version_Partageable.bat` | Produit une copie **sans les sections confidentielles**. |
| `arbre_jean.html` | **L'arbre.** Autonome, hors ligne. |
| `arbre_jean_fiches/` | **Une page complète par personne**, régénérée à chaque passage. |
| `exemple_fiche_dense.json` | Gabarit de démonstration : tous les types de sections. |

Gardez `arbre_jean.html` et `arbre_jean_fiches/` côte à côte : le lien « En savoir plus » de chaque fiche pointe vers ce dossier.

Les données, les photos et l'affichage sont séparés. Vous corrigez une date ou vous ajoutez une photo, vous double-cliquez le `.bat`, l'arbre se refait. Vous ne touchez jamais au code.

## Ajouter une photo

Déposez l'image dans `photos/` en la nommant d'après l'identifiant de la personne :

```
photos/pierre-jean-1645.jpg
photos/suzanne-herault.jpg
```

La liste complète des noms de fichiers attendus, avec le nom de chaque personne en regard, se régénère à chaque exécution dans `photos/_noms_de_fichiers.txt`.

Formats acceptés : jpg, jpeg, png, webp, gif, bmp, tif. L'image est **recadrée en carré centré et réduite à 420 px** avant d'être intégrée — inutile de la préparer vous-même, et le HTML reste léger. Rien n'est envoyé nulle part : l'image est encodée dans le fichier.

Une personne sans photo reçoit un **médaillon à initiales**, dans le même cadre coloré. Les deux cohabitent sans rupture visuelle : vous pouvez ajouter les portraits un par un, au fil de vos trouvailles.

## Les deux vues de l'arbre

**Portraits** — médaillons ronds, générations en rangées, lecture de haut en bas. C'est la vue d'apparat, celle qu'on imprime ou qu'on montre.

**Cartes** — rectangles, lecture de gauche à droite. Plus dense, plus lisible quand une branche compte beaucoup de monde : chaque carte montre en plus le métier ou le lieu principal.

Les deux lisent les mêmes données ; le bouton en haut bascule de l'une à l'autre.

## La fiche, et la page complète

Le clic sur un médaillon ouvre une **carte flottante** collée à lui. Elle tient en un écran et ne montre que l'essentiel :

- portrait, nom, dates, surnom ;
- une poignée de lignes : naissance, décès, métier, lieu, union, parents, enfants ;
- les **faits marquants** — les trois ou quatre choses qui se racontent ;
- **toutes les incohérences qui concernent cette personne**, en entier, avec leur type et leur page. Elles sont sur la carte et non reléguées à la page complète : une donnée contestée doit se voir au moment où on la lit, pas après.

En bas, **« En savoir plus → »** ouvre dans un nouvel onglet la **page complète** de la personne, dans `arbre_jean_fiches/`. C'est là que va tout ce qui déborde : la synthèse entière, les notes, toutes les sections versées, les relations (parents, fratrie, unions, enfants — tous cliquables d'une page à l'autre), les points à vérifier et les sources. Un sommaire se tient dans la marge gauche sur les écrans larges. Le compteur à droite du lien vous dit ce qui vous attend : « 1 section · 17 événements ».

Autrement dit : la carte répond à « qui est-ce ? », la page répond à « raconte-moi tout ». Vous versez autant que vous voulez sans jamais encombrer l'arbre.

Les pages se régénèrent entièrement à chaque exécution — ne les modifiez pas à la main, tout passe par le JSON.

## Se servir de l'arbre

- **Glisser** pour déplacer, **molette** pour zoomer, **Recadrer** pour tout revoir.
- **Lignée directe** estompe tout sauf la chaîne d'ascendance.
- **Problèmes** liste les huit points que la source laisse ouverts.
- Pastille rouge sur un médaillon = au moins une donnée contestée.
- Anneau or = lignée directe. Anneau doré clair = resté en France. Anneau vert = passé en Nouvelle-France. Anneau pointillé = rattachement non documenté.
- Touche `/` pour chercher dans l'arbre, `Échap` pour refermer, bouton `◐` pour clair / sombre.

## Les lieux cliquables

Les noms de lieux sont cliquables **partout où ils apparaissent** : dans la rubrique Lieux, mais aussi à l'intérieur des dates, des faits marquants, des notes, des incohérences et des sections. Ils s'affichent en or, soulignés en pointillé, suivis d'une petite épingle.

La requête ne part **jamais** du texte brut, pour deux raisons : les chaînes contiennent des dates entre parenthèses, et beaucoup de toponymes existent des deux côtés de l'Atlantique — « Champlain », « Gentilly », « Beauport », « Montréal » tomberaient en France une fois sur deux. Tout passe donc par deux tables, dans `meta.carte` du JSON.

**`lieux`** — correspondance exacte, pour la rubrique Lieux : la chaîne entière est remplacée par une requête propre.

```json
"carte": {
  "actif": true,
  "service": "https://www.google.com/maps/search/?api=1&query=",
  "lieux": {
    "Beauport (juillet 1671)": "Beauport, Québec, QC, Canada",
    "Petit Fétilly, paroisse Saint-Maurice, Aunis": "Fétilly, La Rochelle, France",
    "la Grande Anse": ""
  }
}
```

**`toponymes`** — noms reconnus **à l'intérieur des textes libres**. C'est ce qui rend « Cap-de-la-Madeleine » cliquable au milieu d'un fait marquant, ou « Écoyeux » au milieu d'une date.

```json
"toponymes": {
  "Cap-de-la-Madeleine": "Cap-de-la-Madeleine, Trois-Rivières, Québec, Canada",
  "Champlain":           "Champlain, Québec, Canada",
  "Nouvelle-France":     ""
}
```

Les noms les plus longs sont essayés d'abord, pour que « rivière Champlain » ne devienne pas la ville de Champlain. Seule la **première occurrence** de chaque nom dans un même bloc reçoit un lien : un paragraphe qui répète « Écoyeux » quatre fois n'en porte qu'un, sans quoi le texte deviendrait illisible.

Règles communes aux deux tables :

- Une entrée **vide** désactive le lien. C'est le cas pour « Nouvelle-France », « Canada » et « France » — ce ne sont pas des points sur une carte — et ce sera le cas des adresses de personnes vivantes.
- Dans `lieux`, une chaîne **absente de la table** reçoit tout de même un lien, construit sur son texte parenthèses retirées. Dans `toponymes`, rien n'est deviné : un nom non déclaré n'est jamais reconnu.
- `"actif": false` coupe tous les liens d'un coup.
- `service` se remplace par un autre fournisseur, par exemple `https://www.openstreetmap.org/search?query=`.
- Une entrée de chronologie accepte aussi un champ `"lieu"`, rendu en lien.

Les 33 lieux et les 41 toponymes du corpus actuel sont renseignés. Deux restent volontairement sans lien, et `meta.carte.incertains` dit pourquoi : « la Grande Anse », dont plusieurs lieux portent le nom au Québec, et « St-Mathieu », que la source ne précise pas — les abréviations du livre orientent vers le Bas-Saint-Laurent, mais ce n'est écrit nulle part.

**Ce que le lien révèle.** Cliquer envoie la requête à Google. Pour des ancêtres du XVIIᵉ siècle c'est sans conséquence ; le jour où vous verserez des adresses de personnes vivantes, mettez-les à `""`, ou coupez `actif`. **Les sections confidentielles ne sont jamais parcourues** : une adresse privée n'a pas à devenir une requête Google par simple effet de bord.

## Modifier les données

```json
"identifiant-unique": {
  "prenom": "Pierre", "nom": "Jean", "sexe": "M",
  "lignee": true,            // sur la lignée directe
  "ancetre": true,           // l'ancêtre canadien
  "pays": "nf",              // "fr" = resté en France, "nf" = passé en Nouvelle-France
  "naissance": { "texte": "...", "certitude": "attestee", "tri": 1645 },
  "bapteme": { }, "deces": { }, "sepulture": { },
  "metiers": [], "lieux": [], "notes": [], "sources": []
}
```

Les unions sont déclarées à part :

```json
{ "id": "u-ancetre",
  "conjoints": ["pierre-jean-1645", "francoise-favreau"],
  "lignee": true,
  "mariage": { "texte": "08-07-1668, église St-Sauveur, La Rochelle", "certitude": "attestee" },
  "contrat": { "texte": "..." },
  "enfants": ["identifiant", "identifiant"] }
```

## Verser autant d'information qu'on veut

Deux champs pour cela.

**`marquants`** — les lignes courtes qui s'affichent sur la carte flottante. C'est l'endroit pour ce qui se raconte : un exploit, une condamnation, un naufrage, une invention. Trois ou quatre suffisent.

```json
"marquants": [
  "Expulsé de Nouvelle-France par le Conseil Souverain le 18 juin 1664 — il revint cinq ans plus tard.",
  "Le seul des quatre frères à transmettre intact le patronyme JEAN."
]
```

**`sections`** — tout le reste, affiché sur la page complète : récits, chronologies, inventaires, et jusqu'à un dossier médical. Six types :

```json
"sections": [
  { "titre": "Récit de vie", "type": "texte",
    "intro": "ligne d'introduction, facultative",
    "contenu": ["premier paragraphe", "deuxième paragraphe"] },

  { "titre": "Documents retrouvés", "type": "liste",
    "contenu": ["acte de baptême", "brevet d'enseignement"],
    "source": "inventaire d'octobre 2026" },

  { "titre": "Repères", "type": "faits",
    "contenu": [ { "q": "Scolarité", "r": "École normale, brevet A",
                   "note": "à confirmer", "certitude": "approximative" } ] },

  { "titre": "Chronologie", "type": "chrono",
    "contenu": [ { "date": "1952", "titre": "Naissance", "detail": "Québec." } ] },

  { "titre": "Adresses", "type": "tableau",
    "contenu": { "colonnes": ["Période", "Adresse"],
                 "lignes": [["1952 – 1970", "Limoilou"]] } },

  { "titre": "Dossier médical", "type": "texte", "prive": true,
    "contenu": ["…"] }
]
```

Ouvrez `exemple_fiche_dense.json` avec le `.bat` : il contient un personnage fictif qui exerce les six types, dont deux sections confidentielles.

## Les sections confidentielles

Une section marquée `"prive": true` reçoit trois protections, dans cet ordre :

1. **Elle n'apparaît jamais sur la carte flottante** — seulement sur la page complète. Un bandeau « Contient du confidentiel » prévient dès la carte.
2. **Son contenu est voilé** sur la page : il faut un clic délibéré pour l'afficher.
3. **`Generer_Version_Partageable.bat` produit `arbre_jean_partage.html` et son dossier `arbre_jean_partage_fiches/`, d'où ces sections sont physiquement absentes.** Ce n'est pas un masquage d'affichage : le texte n'est pas dans les fichiers. C'est ce couple-là qu'on envoie à la parenté.

Quand le générateur produit la version complète et qu'elle contient du confidentiel, il vous le dit en clair dans la fenêtre noire.

### Ce que les trois protections ne font pas

Elles protègent du regard accidentel, pas d'un lecteur déterminé. `arbre_jean.html` reste **un fichier texte en clair** : n'importe qui l'ouvrant dans un éditeur lit tout, voile compris. Si vous y versez un dossier médical, trois conséquences :

- Le fichier devient un document de santé. Il n'a rien à faire dans un dossier synchronisé vers un nuage, ni sur une clé qui circule.
- Rangez l'ensemble du dossier dans un conteneur chiffré (BitLocker, VeraCrypt) plutôt que dans Documents.
- **N'envoyez jamais la version complète.** Prenez l'habitude de générer la version partageable et de ne transmettre que celle-là — y compris à la famille proche.

Un dernier point, de méthode plutôt que de technique : les personnes vivantes autres que vous n'ont pas consenti à figurer dans un fichier qui circule. Le marquage `prive` est aussi fait pour ça.

**Valeurs de `certitude`** — c'est le cœur de la méthode :

| Valeur | Sens |
|---|---|
| `attestee` | la source donne la donnée telle quelle, sans réserve |
| `approximative` | « vers », « environ », « entre X et Y », « avant/après » |
| `deduite` | calculée, non écrite dans la source (ex. une naissance tirée d'un âge au décès) |
| `divergente` | la source se contredit elle-même |
| `incoherente` | la donnée contredit un autre fait établi |
| `inconnue` | mentionnée mais non datée |

Seul `attestee` s'affiche sans marque ; tout le reste porte une étiquette visible. C'est voulu — une généalogie se corrompt par les certitudes empruntées.

Si le `.bat` signale une erreur de syntaxe, il indique la ligne et la colonne fautives.

## État actuel

60 personnes, 16 unions, 3 générations complètes, 8 points à vérifier, aucun portrait pour l'instant. Une seule fiche est étoffée : celle de Pierre Jean, dont le parcours a été remonté en chronologie de 17 entrées à partir des pages 7 et 10 — sans qu'aucun événement soit ajouté.

**Ce qui manque et qui bloque la suite :** les générations 4 et 5, c'est-à-dire le chaînon entre Pierre Jean (baptisé à La Rochelle en 1645) et Michel Pierre Jean, colon-défricheur de St-Mathieu, à qui le livre est consacré. L'extrait fourni s'arrête avant. Le livre complet fait au moins 247 pages et descend jusqu'à la 10ᵉ génération.

## Deux façons d'ouvrir l'arbre

**Par double-clic** sur `arbre_samuel.html` : tout se consulte, et les fiches
rendent un fichier d'ajouts à déposer sur `Appliquer_Ajouts.bat`. C'est le
mode qui voyage — un parent à qui vous envoyez une branche n'a rien à
installer.

**Par `Serveur_Local.bat`** : la même page, servie sur `127.0.0.1`, se
modifie sur place. Dans l'arbre, un clic sur le visage d'une carte change la
photo ; dans une fiche, un clic sur n'importe quelle valeur la corrige —
dates, lieux, métiers, notes, photos, recettes, faits marquants. Chaque
geste est écrit aussitôt et l'arbre se refait seul. Un mode
**administrateur** (bouton en haut de la fiche, mot de passe posé par
`Changer_Mot_De_Passe_Admin.bat`) remplace un fait attesté ou retire ce qui
n'a pas sa place ; tout reste dans `historique/` et se restaure. Mode
d'emploi complet : `docs/COMMENT-AJOUTER.md`. Fermez la fenêtre noire pour
arrêter le serveur.

C'est la **même page** dans les deux cas : elle constate comment elle a été
ouverte. Il n'y a pas deux versions à maintenir, donc pas de version qu'on
teste moins et qui parte chez la parenté.

Le serveur n'écoute que sur `127.0.0.1` : rien d'autre que votre ordinateur
ne peut l'atteindre, et l'air-gap de Wilfred n'en est pas entamé.

## Ce qui change en phase 1

Cadré le 2026-10-11, pas encore codé. Quatre choses, dans cet ordre :

1. **L'arbre s'ouvrira centré sur Samuel**, et non plus sur l'ancêtre canadien.
2. **Il se lira dans les deux sens** — l'ascendance au-dessus, la descendance
   en dessous. Aujourd'hui il ne descend que vers le bas.
3. **Chaque personne saura à quelle branche elle appartient**, par calcul et
   non par étiquette posée à la main.
4. **Une branche pourra être détachée** en un dossier autonome à remettre à
   la parenté. Les sections confidentielles en sont retirées physiquement, et
   il n'existe aucune façon de produire un export qui les contienne.

Une personne d'une autre famille — un conjoint — apparaît dans l'export
**par son nom seulement** : pas de dates, pas de page, et ses propres parents
ne sont jamais atteints. C'est pourquoi l'export Jean ne peut pas contenir de
données Trinh : elles n'y entrent jamais, plutôt que d'en être retirées.

## Source

Julienne Jean, *Michel Jean*, révisé en 06-2016, pages 1 à 10.
L'auteure s'appuie notamment sur Lucie Jean-Haffner, *Les quatre frères Jean — de La Rochelle à Québec* (1989), et sur un article de Gérard Lebel, C.Ss.R., paru dans la *Revue Ste-Anne* de mai 1994.

Rien dans ces données ne provient d'une recherche extérieure : tout est tiré de l'extrait, et ce qui en est déduit est marqué comme tel.

---

## Les sources numérisées

Les deux documents sources sont océrisés depuis le 2026-10-16 :

| Document | Langue | Pages | Numéros attestés |
|---|---|---|---|
| *Michel Jean*, Julienne Jean | français | **1 à 290**, sans lacune | 269 / 290 |
| *Gia phả họ Trịnh*, Huỳnh Công Chánh | vietnamien | 5 à 106 | 43 / 98 |

Le texte est dans `Scans OCR`, **une page par fichier, nommée par son numéro
imprimé** : `michel-jean/p018.txt` est la page 18 du livre. Pour retrouver un
passage, il suffit donc de connaître sa page.

Le livre de Julienne Jean fait au moins 290 pages, et non 247 comme l'indiquait
ce fichier : 247 était un plancher. Les vingt-huit lots de numérisation se
chaînent bout à bout sans trou, ce qui est une preuve de complétude plutôt
qu'une impression.

**Deux points à vérifier sur le papier** : s'il y a quelque chose après la page
290 du livre français ; et les pages 53, 54, 75 et 86 du document vietnamien,
qui n'apparaissent dans aucun scan — mais dont l'absence n'est pas certaine,
les numéros de ce document se lisant mal.

Pour relancer l'océrisation après avoir ajouté des scans :

    python outils/ocr_scans.py --ocr        (reprend où elle s'est arrêtée)
    python outils/ocr_scans.py --resoudre   (renomme les pages, rapide)

Cet outil a besoin de tesseract et de poppler. **Le reste du projet, non** :
l'arbre se génère et les tests passent sans eux.