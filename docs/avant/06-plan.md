# 06 — Plan par phases

Une phase est terminée quand **tous ses tests passent sur Wilfred**, pas quand le code paraît juste.

---

## Phase 0 — Mise sous protocole

**Ce qui est livré.** Le programme d'aujourd'hui, inchangé, mais sous harnais : dépôt git vivant, journal ouvert, contrat scellé, environnement constaté.

**Pourquoi cette phase existe.** Elle prouve que la boucle tourne — écrire, exécuter, voir, commiter — avant qu'on lui confie quoi que ce soit. Si elle échoue, le problème est dans l'outillage, pas dans le code généalogique, et on le saura tout de suite.

**Tests qui doivent passer :** `T-01` à `T-28` sur les deux jeux d'exemple. `T-29` à `T-34` passent ou s'affichent `SAUTE` selon que Playwright est présent.

**Travail attendu de Qwen :**

1. `git --version`, `git status`, version de Python, présence de Pillow et de Playwright. Consigner en `E-001.1`.
2. Compléter le tableau « À constater au démarrage » de `02-environnement.md`.
3. Lire `docs/avant/` en entier, puis écrire sa reformulation en `E-001.2`.
4. Lancer `Tester.bat`. Consigner la sortie entière.
5. Si tout est vert : commit, et la phase 0 est terminée.
6. Si un contrôle échoue : c'est que l'environnement de Wilfred diffère de celui où le contrat a été écrit. Diagnostiquer, corriger **le code et non le test**, trois tentatives au plus, puis `B-xx`.

**Interdit propre à cette phase.** Aucune amélioration, même évidente. Un défaut d'apparence repéré, une fonction qui manque, une ligne qu'on écrirait autrement : tout cela va dans `docs/apres/11-questions.md` sous un `Q-xx`. On ne mélange jamais une migration et une amélioration — quand quelque chose casse, on ne sait plus laquelle des deux en est la cause.

---

## Phase 1 — Les générations manquantes

**À cadrer avec Claude avant d'être lancée.** Le livre source descend jusqu'à la 10ᵉ génération ; l'extrait transcrit s'arrête à la 3ᵉ. Il manque le chaînon entre Pierre Jean et Michel Pierre Jean.

Ce qui relève du code : accueillir un arbre nettement plus grand sans que la disposition devienne illisible, et sans que la génération s'éternise.

Ce qui n'en relève pas : la transcription elle-même. Elle reste éditoriale.

**Candidats de tests :** disposition sur plusieurs centaines de personnes ; temps de génération borné ; repli lisible quand une fratrie compte plus de dix enfants.

---

## Phase 2 — Reprise des scans

**À cadrer.** Le dossier `Scans` contient le PDF d'origine et `Scans OCR` est vide. Une chaîne de reprise produirait du texte exploitable à partir des pages numérisées.

Attention : trois pages du PDF d'origine étaient numérisées à l'envers. Une chaîne qui ne détecte pas l'orientation produira du texte inventé avec aplomb.

---

## Phase 3 — Impression

**À cadrer.** Une planche grand format, et une fiche imprimable par personne.

---

## Règle commune à toutes les phases

Aucune phase ne commence avant que la précédente soit verte **sur Wilfred**. On ne construit pas sur un étage qui n'a pas été reçu.
