# Demande D-003 — Couverture des sources paginées

> Recopiée mot pour mot. Les constats et les décisions sont plus bas, dans
> des sections séparées.

---

## D-003.1 — La demande

> « J'aimerais que tu ajoutes , au script pour Qwen coder, une fonction pour
> mémoriser les pages (les 2 documents principaux sont paginés) qui ont été
> scannées et intégrées à l'arbre généalogique, au cas ou j'en omettrais ;
> Qwen coder pourrait alors me signaler mes manques probables.
>
> Aussi, la version océrisée du PDF, devrait être déposée dans le répertoire
> "Scans OCR" »

## D-003.2 — Sur tesseract à Wilfred

> « Vérifie dans ces markdown: normalement, Wilfred a tesseract mais il n'a
> probablement pas le pack de langage vietnamien et je ne sais pas pour le
> francais »

---

## Ce que la reconnaissance a établi, le 2026-10-16

Rien de ce qui suit n'était connu quand la demande a été formulée. Chaque
ligne est mesurée, pas supposée.

**Le dossier `Scans` contient 38 PDF et 407 pages**, là où il n'en contenait
qu'un seul de 11 pages le 11 octobre. Les noms de fichiers sont des
horodatages de numériseur : **ils ne portent aucune information de page ni de
document**. C'est tout le problème.

**Aucun des 38 PDF n'a de couche de texte.** `pdftotext` rend zéro caractère
sur les trois fichiers éprouvés. Une vraie océrisation est donc nécessaire ;
il n'y a rien à extraire.

**Les deux documents sont identifiés**, par océrisation de la première page
de chacun des 38 fichiers :

| | Document | Langue | Fichiers | Pages |
|---|---|---|---|---|
| `michel-jean` | *Michel Jean*, Julienne Jean, rév. 06-2016 | français | 28 | 298 |
| `gia-pha-ho-trinh` | *Gia phả họ Trịnh*, Huỳnh Công Chánh, 1993-2004 | **vietnamien** | 10 | 109 |

Le second n'avait jamais été mentionné dans le projet. C'est une généalogie
du clan Trịnh, rédigée en vietnamien, qui couvre la branche paternelle.

**Les numéros de page imprimés se lisent.** Éprouvé : page physique 10 d'un
fichier → imprimé **18** ; page 2 d'un autre → **240**, sa page 8 → **246** ;
page 2 du vietnamien → **98**. Le dernier fichier vietnamien finit par
« HẾT » — fin.

**Au moins un fichier est numérisé à l'envers** (`20261015073446964`), dans le
document vietnamien. Le piège de l'orientation s'est donc présenté deux fois
dans ce projet : trois pages du PDF d'origine en octobre, et celui-ci.

**Un précédent chiffré, tiré du projet Sirois** : `extraire_ancres.py` avait
produit « 638 ancres, 468 numéros fiables », soit **73 %**. Un numéro de page
sur quatre sera illisible. La déduction par encadrement n'est donc pas un cas
limite : c'est le chemin principal.

---

## Sur tesseract à Wilfred — ce que disent vos notes

Vérifié à la demande de Sébastien, dans les documents de suivi Wilfred.

- **26 juin**, § « À faire avant de sceller (PAS encore fait) » :
  « Installer les outils non-LLM (pdftotext, Tesseract+FR, FFmpeg,
  Faster-Whisper) » — case **non cochée**.
- **1ᵉʳ juillet**, § « Provisionnement outillage média/document — AVANT
  scellement (**à faire**) » : l'étape préalable « *vérifier l'existant sur
  Wilfred* » est marquée **non faite**, et le pack `fra` est qualifié
  d'« indispensable pour l'OCR de documents en français ».
- **5 juillet** : « La fenêtre de provisionnement est scellée. »

**Aucun document ne consigne un `tesseract --version` réussi sur Wilfred.**
Le pack vietnamien, lui, n'y figure nulle part — il n'a jamais été envisagé.
L'état réel est donc inconnu, et il le restera jusqu'à ce que la commande soit
lancée là-bas. C'est une `Q-xx`, pas une hypothèse.

## Qui fait quoi, et pourquoi

Deux règles écrites par Sébastien tranchent, et elles vont dans le même sens.

**La règle de tri** (`Wilfred_2026-07-01`) : « contenu clinique → Wilfred
(air-gappé, chiffré) ; contenu *éligible en ligne* (livre Sirois publié,
admin, code sans donnée patient) → Dell. » La généalogie est de la seconde
catégorie, exactement comme le livre Sirois — dont la chaîne vit sur le Dell
pour cette raison précise.

**La doctrine du codeur local** (`REPRISE_DEVELOPPEMENT_LOCAL`, § 6) : « le
rôle d'un codeur local sur Wilfred est celui d'un **mécanicien de bord** :
petits ajustements de configuration, corrections ciblées […] Le développement
lourd se fait sur le poste connecté et revient par le sas. »

Océriser 407 pages en deux langues n'est pas du mécanicien de bord. Et la
règle du projet veut qu'une phase ne soit verte que si ses tests passent sur
Wilfred : une chaîne que Qwen ne peut pas exécuter, il ne peut pas la tester.

**Donc :**

| | Qui | Où |
|---|---|---|
| chaîne d'océrisation | Claude | dellg5, `outils/ocr_scans.py` |
| rapport de couverture | **Qwen** | Wilfred, Python seul |

Le découpage suit la ligne des dépendances, pas une répartition de confort :
l'océrisation a besoin de poppler et de tesseract, le rapport n'a besoin de
rien.
