# 05 — Apparence

## Le registre

Un document d'archives, pas une application. Papier ancien plutôt qu'interface : fond crème, sérif, peu de couleurs, aucune animation décorative. La référence visuelle retenue est l'arbre à médaillons circulaires, anneaux colorés et noms dessous.

Ce qui est à éviter : les aplats de couleur vive, les ombres portées marquées, les coins très arrondis, les emoji, les dégradés. Rien qui datera dans cinq ans.

## Couleurs

Toutes les couleurs sont des variables sur `:root`, redéfinies pour le thème sombre. **Aucune couleur en dur dans le corps de la feuille de style** : un thème qui ne bascule qu'à moitié est pire que pas de thème du tout.

| Rôle | Clair | Sens |
|---|---|---|
| fond | `#f8f5ec` | crème |
| surface | `#fffdf7` | cartes, panneaux |
| encre | `#241f17` | texte |
| or | `#b4862c` | **lignée directe**, liens, accent |
| doré | `#b08a3e` | **resté en France** |
| vert | `#2f7d4f` | **passé en Nouvelle-France** |
| alerte | `#a8452a` | **donnée contestée**, confidentiel, sélection |

Les couleurs portent du sens ; elles ne décorent pas. Un anneau vert dit « cette personne a traversé l'Atlantique ». N'introduisez pas de couleur sans lui donner une signification, et inscrivez-la ici.

## Typographie

Pile sérif, sans aucun téléchargement : `"Iowan Old Style", "Palatino Linotype", Palatino, Georgia, "Times New Roman", serif`. Ne jamais ajouter de police web : le fichier doit s'ouvrir hors ligne.

Les dates emploient `font-variant-numeric: tabular-nums` pour s'aligner en colonne.

Les intitulés de rubrique sont en petites capitales espacées, gris, taille réduite. Le contenu est en taille normale, encre pleine. L'écart entre les deux porte la hiérarchie — pas le gras.

## Les médaillons

Cercle de 68 px, anneau de 3,2 px, 4,6 px pour la lignée directe, avec un halo clair. Sans portrait : disque neutre et initiales en sérif. **Les deux doivent avoir exactement la même taille et le même cadre** — on ajoute les portraits un par un sur des années, et l'arbre ne doit jamais avoir l'air à moitié fait.

Pastille rouge en haut à droite quand une donnée est contestée.

## Les liens de lieu

Or, souligné en pointillé, suivi d'une petite épingle en SVG masqué. Un lien doit se voir : un pointillé gris pâle est passé inaperçu une fois déjà, et l'utilisateur a cru la fonction absente.

## Largeur réduite

Sous 980 px : le sous-titre disparaît, le champ de recherche rétrécit, la légende et l'aide se cachent. L'arbre reste manipulable au doigt — `touch-action: none` sur la toile, et le déplacement passe par les événements de pointeur, jamais par la souris seule.

La fiche flottante ne déborde jamais : `max-width: calc(100vw - 24px)`, et elle bascule de côté quand elle manque de place.

## Impression

Pas traité en phase 0. Si cela vient, ce sera une feuille de style `@media print` séparée, et non une refonte.
