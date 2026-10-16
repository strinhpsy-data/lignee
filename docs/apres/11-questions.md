# 11 — Questions ouvertes

> C'est ici que vont les constats qu'on ne traite pas tout de suite :
> défaut d'apparence repéré en phase 0, fonction qui manque, doute sur une
> donnée. Rien ne se perd, et rien ne détourne la phase en cours.

Gabarit :

```markdown
### Q-01 — Titre court
- Soulevée par : Qwen / Claude / Sébastien
- Étape : E-xxx
- Question :
- Ce qui a été fait en attendant :
- Résolution : (à remplir une fois tranchée, avec la date)
```

---

### Q-01 — Où vivent les recettes de cuisine

- Soulevée par : Claude
- Étape : `C-005` (cadrage de la phase 1)
- Question : le point 5 de `D-002` demande un inventaire de recettes. Sébastien a
  par ailleurs un projet distinct, « Livres de recette Famille Trinh ». Trois
  possibilités : la généalogie porte les recettes ; elle porte une **référence**
  vers le livre (titre, de qui elle vient, où la trouver) ; ou les deux projets
  s'ignorent. **La duplication est la seule réponse certainement fausse** : deux
  copies d'une recette divergent, et personne ne sait plus laquelle est la bonne.
- Ce qui a été fait en attendant : rien. Le modèle de données accueille déjà une
  recette comme une section de type `texte` ou `liste`, et une référence comme une
  section `faits`. Aucun des deux chemins n'est fermé.
- Résolution :

### Q-02 — Comment un parent renvoie ce qu'il a ajouté

- Soulevée par : Claude
- Étape : `C-005`
- Question : un oncle reçoit un fichier HTML. Il ne peut pas l'éditer. `D-002`
  point 4 demande qu'il « mette à jour les informations qu'il détient » et les
  transmette à la mère de Sébastien ou à son oncle. Par quel support ? Papier
  imprimé, courriel libre, fichier texte joint à l'export ? H-18 ferme la porte à
  un formulaire pour la phase 1, mais il faut bien un chemin de retour.
- Ce qui a été fait en attendant : la page d'invitation nomme le destinataire
  (`meta.branches[].retour`) sans prescrire le support. C'est volontairement
  incomplet.
- Résolution :

### Q-03 — Un `.bat` par branche, ou un `.bat` qui demande

- Soulevée par : Claude
- Étape : `C-005`
- Question : quatre fichiers `Exporter_Jean.bat`, `Exporter_Trinh.bat`… ou un seul
  `Exporter_Branche.bat` qui demande laquelle ? Le premier est plus sûr — pas de
  saisie, donc pas de faute de saisie — mais il multiplie les fichiers à la racine
  et il faut en ajouter un à chaque nouvelle branche.
- Ce qui a été fait en attendant : noté dans `04-parcours.md`, section D, comme
  « à trancher à l'ouverture de la phase 2 ».
- Résolution :

### Q-04 — Les branches Dionne et Gagné s'exportent-elles

- Soulevée par : Sébastien, dans `D-002` point 4 : « Je ne sais pas ce qu'on fera
  pour les branches de la famille de Valérie »
- Étape : `C-005`
- Question : les deux branches du côté de Valérie n'ont pas de destinataire de
  retour désigné. Elles sont dans l'arbre ; sont-elles exportables ?
- Ce qui a été fait en attendant : `meta.branches[].retour` est **facultatif**.
  Une branche sans `retour` s'exporte mais ne porte pas de page d'invitation. La
  structure accueille les deux réponses sans être modifiée.
- Résolution :

### Q-05 — Tesseract et les packs de langue sur Wilfred

- Soulevée par : Sébastien — « normalement, Wilfred a tesseract mais il n'a
  probablement pas le pack de langage vietnamien et je ne sais pas pour le
  francais »
- Étape : `C-007`
- Question : l'état réel est **inconnu**, et les notes de suivi le confirment
  plutôt que de l'infirmer. Le 26 juin, « Installer les outils non-LLM
  (pdftotext, Tesseract+FR…) » : case non cochée. Le 1ᵉʳ juillet, l'étape
  « vérifier l'existant sur Wilfred » est marquée **non faite**, et le pack
  `fra` qualifié d'« indispensable ». La fenêtre de provisionnement s'est
  scellée le 5 juillet. Aucun document ne consigne un `tesseract --version`
  réussi là-bas ; le vietnamien n'y apparaît nulle part.
- Ce qui a été fait en attendant : l'océrisation a été faite sur dellg5, et le
  partage du travail ne dépend plus de la réponse (H-26). Trois commandes très
  courtes la donneront : `tesseract --version`, `tesseract --list-langs`,
  `pdftoppm -v`.
- Résolution :

### Q-06 — Les quatre lacunes du document vietnamien

- Soulevée par : Claude
- Étape : `C-007`
- Question : les pages 53, 54, 75 et 86 de *Gia phả họ Trịnh* n'apparaissent
  dans aucun scan. Mais elles tombent **exactement aux jointures de lots**, là
  où le document français montre des chevauchements, et le taux
  d'attestation vietnamien est faible — 43 numéros lus sur 98. Plusieurs pages
  voisines donnent un numéro lu qui diffère d'une unité du numéro déduit. Ces
  lacunes sont donc **à vérifier sur le papier**, pas établies.
- Ce qui a été fait en attendant : rien d'automatique. Le rapport de
  couverture doit porter cette réserve dans sa sortie plutôt que d'affirmer
  une lacune (`08-couverture.md`, § 6).
- Résolution :