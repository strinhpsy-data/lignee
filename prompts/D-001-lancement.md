# Mission — Arbre généalogique Jean — protocole v1.0 — D-001

Tu es le développeur de ce projet. Tu travailles seul, sans supervision immédiate, possiblement toute la nuit. Ce prompt est la demande `D-001`.

Le projet existe déjà et il fonctionne. Ta première mission n'est pas de l'améliorer : c'est de le mettre sous harnais sans rien y changer.

## Interdits absolus

1. **Ne jamais modifier quoi que ce soit dans `tests/`.** Une empreinte le détecte. Si un test te semble faux, inscris une `Q-xx` dans `docs/apres/11-questions.md` et continue ailleurs.
2. **Ne jamais supprimer de fichier.** Aucun, sous aucun prétexte.
3. **Ne jamais inventer une donnée généalogique.** Pas de date, pas de lieu, pas de filiation qui ne figure dans une source citée.
4. **Aucun accès réseau** depuis le générateur ni depuis les pages produites.
5. **Ne jamais te déclarer terminé sans avoir lancé `Tester.bat` et obtenu tous les contrôles au vert.**

## Démarrage

1. Exécute `git --version`, puis `git status`, puis `python --version`. Vérifie aussi la présence de Pillow et de Playwright :
   `python -c "import PIL; print(PIL.__version__)"`
   `python -c "import playwright; print('ok')"`
   Journalise l'ensemble en `E-001.1`, avec les sorties exactes.
2. Reporte ces valeurs dans le tableau « À constater au démarrage » de `docs/avant/02-environnement.md`, et dans `docs/apres/09-etat.md`.
3. Lis `docs/avant/` en entier, dans l'ordre des numéros.
4. Écris dans le journal **ta propre reformulation** du projet en `E-001.2` : ce que fait le programme, ce qu'on te demande, ce que tu t'interdis. Si elle contredit la documentation, inscris une `Q-xx` et poursuis sur les parties non touchées. N'attends pas de réponse.

## Méthode

- Suis `docs/avant/06-plan.md`, phase par phase. **Tu n'es chargé que de la phase 0.**
- Une étape = une entrée de journal = un commit dont le message commence par son code : `[E-001.3] Constate l'environnement de Wilfred`.
- Sépare toujours **les faits** (commande, code de sortie, sortie brute) de **tes déclarations** (intention, constat). Le gabarit de la section 6 du protocole impose cette séparation : respecte-la, c'est elle qui rend ton travail vérifiable.
- Sortie de plus de 50 lignes : mets-la entière dans `journal/sorties/<code>.txt` et garde dans l'entrée les 20 premières et 30 dernières lignes.
- Toute nouvelle demande de Sébastien : recopie-la **mot pour mot** sous un nouveau `D-xxx` avant d'agir.
- Tout écart par rapport à la spécification : `X-xx` dans `docs/apres/10-ecarts.md`.

## Blocage

Après **trois** tentatives infructueuses sur un même contrôle, ou si tu tournes en rond : inscris un `B-xx` avec le test en échec, tes tentatives, ta dernière sortie, ton hypothèse, et **ce que tu n'as pas essayé**. Puis passe à une partie non bloquée, ou arrête.

Ne t'acharne pas. Trois tentatives, c'est la limite, et la déclarer n'est pas un échec : c'est ce qui permet à Claude de reprendre vite.

## Particularités de ce projet

**La phase 0 ne change aucun comportement.** À la fin, `Generer_Arbre.bat` doit produire exactement les mêmes fichiers qu'avant. Si tu repères un défaut, une maladresse ou une amélioration évidente : `Q-xx`, et tu continues. On ne mélange jamais une migration et une amélioration — sinon, quand quelque chose casse, on ne sait plus laquelle des deux en est la cause.

**Les contrôles navigateur peuvent légitimement s'afficher `SAUTE`.** Si Playwright n'est pas installé sur Wilfred, `T-29` à `T-34` sont sautés et le contrat peut quand même atteindre le vert. Ce n'est pas un échec à corriger. N'installe rien : la machine est hors réseau.

**Si Git manque**, tu peux travailler mais pas commiter, donc ne laisser aucune trace exploitable. Déclare-le en `B-xx` dès la première séance et signale-le clairement.

**Les données réelles ne sont pas dans le dépôt.** `genealogie_jean.json` et `photos/` sont au `.gitignore` : ils existent sur le disque mais ne sont pas versionnés, et c'est voulu. Les contrôles tournent sur `tests/donnees/`. Ne cherche pas à les versionner.

**`Generer_Arbre.bat` échouera au premier essai**, avec `fichier introuvable`.
C'est normal : les données réelles ne sont pas dans le dépôt. La phase 0 n'en a
pas besoin — `Tester.bat` tourne sur `tests/donnees/`. Ne cherche pas à
reconstituer le fichier manquant, et surtout n'en invente pas le contenu.

**Deux pièges déjà rencontrés sur cette chaîne**, documentés dans `02-environnement.md` : la suppression de fichier est refusée sur les dossiers connectés ; et un HTML bien formé peut avoir un JavaScript mort, que seul un **vrai** clic détecte.

## Fin de séance

Mets à jour `journal/INDEX.md` et `docs/apres/09-etat.md`, puis fais un commit final.

Si la phase 0 est verte, dis-le explicitement dans `09-etat.md` : c'est ce qui permettra d'ouvrir la phase 1.
