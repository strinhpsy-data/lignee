# Comment modifier les fiches : photos, dates, recettes, faits marquants

Deux chemins. **Sur votre poste, utilisez le premier.** Le second existe
pour la parenté, qui n'aura ni le projet ni Python.

---

## 1 · Sur dellg5 — le serveur local : on clique, c'est enregistré

**Double-cliquez `Serveur_Local.bat`.** Une fenêtre noire s'ouvre et affiche
une adresse ; le navigateur s'ouvre tout seul sur l'arbre de Samuel.

**Laissez la fenêtre noire ouverte.** C'est elle, le serveur. La fermer
arrête tout.

Depuis C-022, il n'y a plus rien à « enregistrer » : chaque geste est écrit
dans le projet, l'arbre se refait seul (une à deux secondes) et la page se
recharge au même endroit.

**Dans l'arbre**

- Cliquez un médaillon → la carte s'ouvre.
- **Cliquez le visage dans la carte** → choisissez une image → l'arbre se
  refait, la carte se rouvre avec la nouvelle photo. L'ancien portrait n'est
  pas effacé : il est rangé dans `photos/_anciens_portraits/`.
- « En savoir plus » ouvre la fiche complète.

**Dans la fiche**

- **Toute valeur se corrige en cliquant dessus** (ou sur le petit crayon ✎) :
  naissance, baptême, décès, sépulture — avec leur niveau de certitude et
  une note —, surnom, variantes du nom, métiers, lieux, notes, faits
  marquants, recettes, légendes des photos. `Entrée` enregistre, `Échap`
  annule.
- Les rubriques vides (« + métier », « + lieu », « + note »…) n'apparaissent
  que dans ce mode : elles sont là pour être remplies.
- **Photos** : « + Ajouter des photos », plusieurs d'un coup.
- **Recettes** : « + Ajouter une recette ».
- **Faits marquants** : « + Ajouter un fait marquant ». Un fait se rattache
  à **plusieurs personnes** (un mariage, une traversée, un déménagement) :
  il apparaît alors sur la fiche de chacune, et dans la carte de l'arbre.
- Une fiche modifiée prévient l'arbre ouvert dans l'autre onglet, qui se
  refait aussi.

> **Si rien n'est cliquable** et que le bas de page propose « Enregistrer
> mes ajouts », la page n'a pas été ouverte par le serveur — vous avez
> ouvert le fichier directement. Repassez par `http://127.0.0.1:8731/`.

### Le mode administrateur

Bouton **« Administrateur »** en haut à droite d'une fiche, avec le mot de
passe. Il permet :

- de **remplacer un fait attesté** quand la source a été mal lue ;
- de **corriger un prénom ou un nom** ;
- de **retirer** ce qui n'a pas sa place, même s'il vient des sources
  (fait, section, note, photo, fait marquant) ;
- de consulter l'**historique** de la fiche et d'y **restaurer** une valeur
  retirée ou remplacée.

Le mot de passe n'est écrit nulle part en clair : le projet n'en garde
qu'une empreinte, dans `outils/_admin.json` (hors de git). Pour le changer :
**`Changer_Mot_De_Passe_Admin.bat`**, puis relancez le serveur. La session
dure huit heures, ou jusqu'à « Administrateur · quitter ». La version
partageable ne contient aucune trace de ce mode.

### Rien ne se perd

Toute valeur remplacée ou retirée est consignée dans
`historique/genealogie_samuel.json`, hors des exports. Ce qu'on a soi-même
ajouté par l'interface se retire librement ; ce qui vient des sources ne se
retire qu'en mode administrateur. Une photo retirée est déplacée dans
`photos/_retirees/`, jamais effacée.

---

## 2 · Pour la parenté — le fichier d'ajouts

Un parent reçoit un export : un seul fichier HTML, qu'il ouvre par
double-clic. Pas de serveur, pas d'installation (interdit 4).

Chez lui, le bouton dit **« Enregistrer mes ajouts »** et **télécharge un
fichier** nommé `ajouts-<identifiant>.json`. Il vous le renvoie.

De votre côté : **glissez ce fichier sur `Appliquer_Ajouts.bat`.** Vous
pouvez en glisser plusieurs d'un coup. Puis `Generer_Arbre.bat`.

C'est exactement ce qui a été fait le 17 octobre avec vos cinq fichiers.

---

## Ce que le mécanisme refuse de faire

- **Écraser un fait attesté.** Une date tirée d'un acte de paroisse ne se
  fait pas remplacer par une saisie à la main — sauf en mode
  administrateur, et l'ancienne lecture reste dans l'historique.
- **Écraser une photo.** Par le fichier d'ajouts, un second portrait se
  range à côté ; par le serveur, l'ancien part dans
  `photos/_anciens_portraits/`. Jamais par-dessus.
- **Enregistrer du vide.** Une recette sans titre ni texte, une date vide :
  rien n'est écrit, et la valeur affichée reste la vraie.
- **Appliquer deux fois le même fichier.** L'empreinte SHA256 est retenue
  dans `photos/_ajouts_appliques.json`. Le 17 octobre, deux fichiers de
  Samuel étaient identiques : le second a été refusé tout seul.

## Pourquoi une seule page pour les deux chemins

La fiche constate comment elle a été ouverte et se comporte en conséquence.
Deux versions à maintenir divergeraient, et c'est celle qu'on teste le moins
qui partirait chez la parenté.
