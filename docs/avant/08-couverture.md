# 08 — Couverture des sources paginées

Répond à la demande `D-003` : savoir quelles pages des documents sources sont
déjà entrées dans l'arbre, pour qu'un oubli se voie.

Deux outils, séparés sur la ligne des dépendances :

| | Outil | Besoins | Qui |
|---|---|---|---|
| océrisation | `outils/ocr_scans.py` | poppler, tesseract | Claude, sur dellg5 |
| rapport | **à écrire** | Python seul | **Qwen** |

**Ni l'un ni l'autre n'est une dépendance du générateur.** `Generer_Arbre.bat`
et `Tester.bat` ignorent tout de tesseract : H-10 tient.

---

## 1. Le principe qui gouverne tout le reste

Ce rapport sert à attraper un oubli. Ses erreurs doivent donc **pencher du
côté de l'alarme, jamais du côté du réconfort**.

Une page annoncée manquante à tort coûte une minute de vérification. Une page
annoncée intégrée à tort coûte précisément l'oubli dont on voulait se
protéger. **Toute ambiguïté se résout donc en « non intégrée ».** Une mention
de source qu'on ne sait pas lire n'est pas ignorée : elle est comptée comme
n'attribuant rien, et elle est listée.

C'est la même leçon que le clic mort de la séance 1 et que les fausses alarmes
de `C-006` : un signal auquel on ne croit plus ne sert à rien, et un signal
rassurant qui se trompe est pire que pas de signal.

## 2. Les quatre états d'une page

| État | Comment il se constate |
|---|---|
| **intégrée** | une donnée de l'arbre cite cette page de ce document |
| **numérisée, non intégrée** | `Scans OCR/<doc>/pNNN.txt` existe, aucune donnée ne la cite |
| **non numérisée** | aucun fichier pour cette page |
| **citée sans numérisation** | une donnée la cite, mais aucun fichier n'existe |

Le quatrième état n'est pas une erreur : Sébastien a pu transcrire du papier
sans scanner. Mais il peut aussi révéler une citation fautive, donc il se
montre.

**L'identité d'une page est son nom de fichier.** `p018.txt` *est* la page 18.
C'est pour cela que la chaîne d'océrisation nomme par numéro imprimé et non
par fichier de scan : la couverture devient alors une simple liste de
dossier, sans table intermédiaire à maintenir.

## 3. Lacune interne contre reste à faire

C'est la distinction qui rend le rapport utile au lieu de bavard.

- Pages 1-10 intégrées, 11-290 non : **ce n'est pas une lacune**, c'est
  l'avancement. Une ligne suffit.
- Pages 1-10 et 14-20 intégrées, 11-13 non : **c'est un oubli probable**, et
  ça doit se voir.

Même règle pour la numérisation. Une plage finale non numérisée est du travail
qui reste ; un trou au milieu d'une suite numérisée est une feuille sautée sur
la vitre du numériseur.

Un document dont `pages` vaut `null` ne produit aucune alarme de fin : on ne
sait pas où il s'arrête, et on ne le devine pas.

## 4. Lire les mentions de source

Les documents sont déclarés dans `Scans/_documents.json` (format en
`03-donnees.md`). Chacun porte une `citation` : la chaîne par laquelle il est
nommé dans les `sources` de l'arbre.

À reconnaître, après la citation du document :

```
p. 7      p.7      page 7      pp. 7-10      p. 7 à 10
p. 7, 10      p. 7 et 10
```

Tout le reste est **non attribué** et listé en fin de rapport. Une mention qui
nomme un document inconnu l'est aussi.

Attention aux diacritiques : la citation du document vietnamien est
`Gia phả họ Trịnh`. La comparaison se fait sur une forme repliée (accents
retirés, casse ignorée), comme le fait déjà la reconnaissance des toponymes
dans le générateur — mais le texte affiché garde ses diacritiques.

## 5. Ce que le rapport montre

Une sortie texte, écrite dans `Scans OCR/_couverture.txt`, qu'un
`Rapport_Couverture.bat` produit puis ouvre dans l'éditeur par défaut.
Sébastien ne tape aucune commande et ne lit rien dans une fenêtre qui se
referme.

Par document :

```
MICHEL JEAN — Julienne Jean, rév. 06-2016
  pages déclarées : 290 (déduite)

  intégrées        :  10   (1-10)
  numérisées       : 290   (1-290)
  non numérisées   :   0

  LACUNES INTERNES — probablement des oublis
    numérisation : aucune
    intégration  : aucune

  Reste à intégrer : 11-290  (280 pages)

  Pages dont le numéro n'est pas attesté — à prendre avec réserve
    déduites    :   9   (p. 10, 42, 136, …)
    incohérentes:  12
    doublons    :   7   (jointures de lots, sans conséquence)
    inconnues   :   1   (couverture)
```

Et, en fin de rapport, les mentions de source non attribuées, s'il y en a.

**Les niveaux de certitude de l'océrisation doivent remonter dans le
rapport.** Une page nommée par déduction peut être mal nommée, et une page mal
nommée fait mentir la couverture. Le rapport ne les cache pas derrière un
chiffre global.

## 6. Pourquoi ce chapitre existe — le cas vietnamien

Les deux documents ont été océrisés le 2026-10-16. Les résultats ne se
ressemblent pas, et c'est instructif.

*Michel Jean* : 290 pages nommées, 269 attestées sur 290, et les **28 lots se
chaînent sans aucune lacune**, avec seulement sept pages en double aux
jointures. Vingt-huit décalages ajustés indépendamment qui se raccordent bout
à bout : ce n'est pas un hasard, c'est une preuve de complétude.

*Gia phả họ Trịnh* : 98 pages nommées, **43 attestées seulement**, 41 déduites,
14 incohérentes, 11 inconnues. Quatre lacunes apparentes — p. 53, 54, 75, 86.

Mais ces quatre lacunes tombent **exactement aux jointures de lots**, là où le
document français montre des chevauchements. Et plusieurs pages voisines
donnent un numéro lu qui diffère d'une unité du numéro déduit (p. 52 lit
« 54 », p. 55 lit « 56 », p. 84 lit « 86 »). Les pages vietnamiennes sont des
tableaux larges, pas de la prose : le numéro n'y est pas toujours au même
endroit, et l'heuristique des bords y est moins sûre.

**Donc le rapport doit dire « à vérifier sur le papier », et non « il manque
quatre pages ».** Un document dont moins de la moitié des numéros sont
attestés ne permet pas d'affirmer une lacune. Le rapport porte cette réserve
dans sa sortie, document par document, en fonction du taux d'attestation.

## 7. Candidats de tests

Sur des jeux d'exemple, jamais sur les données réelles (H-04). Il faudra un
faux `Scans OCR/` d'exemple, avec quelques `pNNN.txt` vides.

| Ce qui est éprouvé |
|---|
| page présente et citée → **intégrée** |
| page présente, non citée → **numérisée, non intégrée** |
| page absente, non citée → **non numérisée** |
| page citée, absente → **citée sans numérisation** |
| `pp. 7-10` compte quatre pages |
| une mention illisible est **listée**, et ne rend aucune page intégrée |
| une mention nommant un document inconnu est listée de même |
| un trou interne figure dans les lacunes ; une plage finale n'y figure pas |
| un document à `pages: null` ne produit aucune alarme de fin |
| la comparaison des citations ignore accents et casse |
| un document faiblement attesté porte sa réserve dans la sortie |

Le sixième est **le contrôle le plus important du lot** : c'est lui qui
garantit la propriété du § 1. Il se code en donnant une source volontairement
tordue — `"Michel Jean, vers la page sept"` — et en vérifiant qu'aucune page
n'en devient intégrée.
