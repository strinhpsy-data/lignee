# Comment ajouter des photos, des dates et des recettes

Deux chemins. **Sur votre poste, utilisez le premier.** Le second existe
pour la parenté, qui n'aura ni le projet ni Python.

---

## 1 · Sur dellg5 — le serveur local

**Double-cliquez `Serveur_Local.bat`.** Une fenêtre noire s'ouvre et affiche
une adresse ; le navigateur s'ouvre tout seul sur l'arbre de Samuel.

**Laissez la fenêtre noire ouverte.** C'est elle, le serveur. La fermer
arrête tout.

Ensuite, dans le navigateur :

1. Cliquez un médaillon → la fiche s'ouvre.
2. **Le portrait** : cliquez dans le rond de la photo. L'explorateur de
   fichiers s'ouvre, vous choisissez une image.
3. **La date de naissance** : le bouton « modifier » à côté des dates.
4. **Photos** et **Recettes** : les sections plus bas, avec leur bouton
   d'ajout.
5. En bas de la page, une barre apparaît dès que quelque chose a changé.
   Le bouton dit **« Enregistrer dans le projet »**.
6. Cliquez-le. C'est écrit sur le disque. Rien d'autre à faire.

> **Si le bouton dit « Enregistrer mes ajouts »** au lieu de « Enregistrer
> dans le projet », c'est que la page n'a pas été ouverte par le serveur —
> vous avez ouvert le fichier directement. Repassez par l'adresse
> `http://127.0.0.1:8731/`.

7. Quand vous avez fini : **`Generer_Arbre.bat`** pour que l'arbre
   affiche les nouveautés, puis fermez la fenêtre du serveur.

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
  fait pas remplacer par une saisie à la main.
- **Écraser une photo.** Un second portrait se range à côté, jamais
  par-dessus.
- **Appliquer deux fois le même fichier.** L'empreinte SHA256 est retenue
  dans `photos/_ajouts_appliques.json`. Le 17 octobre, deux fichiers de
  Samuel étaient identiques : le second a été refusé tout seul.

## Pourquoi une seule page pour les deux chemins

La fiche constate comment elle a été ouverte et se comporte en conséquence.
Deux versions à maintenir divergeraient, et c'est celle qu'on teste le moins
qui partirait chez la parenté.
