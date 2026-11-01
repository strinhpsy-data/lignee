# D-005 — Reprise à froid

> **À coller tel quel au début d'une nouvelle conversation.**
> Écrit le 1er novembre 2026, au moment de supprimer la conversation
> précédente. Tout ce qu'elle contenait est dans le dépôt.

---

## Le prompt

```
Projet : arbre généalogique familial, sur dellg5, dans
C:\Projets\Arbre généalogique (dossier connecté).

Avant de répondre ou de proposer quoi que ce soit, lis dans cet ordre :

  1. journal/INDEX.md          — une ligne par intervention, C-001 à C-029
  2. docs/PASSATION-2026-10-17.md  — interdits, conventions, pièges
  3. journal/<la dernière séance>  — ce qui vient d'être fait
  4. docs/RECHERCHE-SOURCES-EXTERNES.md — si la question touche aux
                                   sources extérieures aux deux livres

Puis dis-moi en trois lignes où en est le projet, et attends ma demande.

Ne touche à rien avant d'avoir lu. Les six interdits sont dans la
passation ; le premier est : ne jamais inventer une donnée généalogique.
```

---

## L'état au 1er novembre 2026

```
genealogie_samuel.json   2 359 personnes · 698 unions · 101 points à vérifier
tests/contrat.py         tout au vert
git                      30 commits
```

**Les deux sources papier sont relevées en entier.**

- *Julienne Jean, généalogie de la famille Jean* (rév. 06-2016) — 290 pages
- *Huỳnh Công Chánh, Gia phả họ Trịnh* (1993-2004) — pages 5 à 106, « HẾT »

La lignée Jean va de Vivien Jean (vers 1580, près de La Rochelle) à Samuel,
treize générations. La lignée Trịnh va de Trịnh Viết Bổn (vers 1750, Thanh
Tuyền, Bình Dương) à Samuel, dix générations.

---

## Ce qui attend

### Tout de suite, et gratuit

**Le *Bulletin des recherches historiques* d'octobre 1949**, sur BAnQ
numérique : une quinzaine de pages sur Pierre Jean et Françoise Favreau,
jamais lues. Le meilleur rapport entre l'effort et le gain.
Voir `docs/RECHERCHE-SOURCES-EXTERNES.md`, section 6.

### À trancher — point `x5`

L'arbre ne citait que les deux livres jusqu'au 1er novembre. Depuis, il
porte huit notes tirées de bases en ligne, sous la forme
`<base>, <identifiant>, consulté le <date>`, **en notes seulement, jamais en
faits attestés**. La convention est à confirmer ou à changer avant d'en
verser davantage.

### Points à vérifier ouverts, par ordre d'intérêt

| Point | Quoi | Ce qui le fermerait |
|---|---|---|
| `x1` | Guillaume Jean, « 7 ou 25 janvier 1654 » — serait naissance + baptême | registre d'Écoyeux (St-Vivien) |
| `x2` | Vivien Jean, mort le 4 ou le 5 avril 1664 — le 4 serait l'inhumation | registre de St-Vivien |
| `x3` | Pierre Jean dit Pierret n'a pas de naissance au livre | PRDH-IGD ou LAFRANCE |
| `x4` | Prinseau : Marie-Madeleine ou Anne-Madeleine | acte de mariage, 01-06-1700, Québec |
| `tp3` | Trịnh Văn Vận « né 1845, mort 1817 » — le livre se trompe, pas l'OCR | l'original |
| `tp4` | « 9e année de Tự Đức = 1861 » — c'est 1856 | — |
| — | Nom de la IIIe génération Trịnh : NHẤNG, NHẬN ou Nhãn | l'original |
| — | Trương Mỹ Dung, p. 52 : fille ou petite-fille, non rattachée | l'original |

### Chantiers non commencés

- **Branches Dionne et Gagné** (côté Valérie Gagné) : vides.
- **Rapport de couverture des pages** (phase 2) : spécifié, jamais écrit.
- **Écrire au comité du clan Trịnh** — Trịnh Văn Hiền, 26 Trần Quang Khải,
  Tân Định, district 1, Hô Chi Minh-Ville. Le livre demande lui-même à être
  corrigé et complété. C'est la seule source qui puisse encore répondre.

---

## Deux choses à savoir sur l'environnement

**Le disque E: ne se monte pas** dans le shell distant. `E:\LIGNÉE` contient
une copie de `Scans` et `Scans OCR`, à jour au 23 octobre. Le projet et ses
outils travaillent sur C: ; E: restera figé. Si les numérisations doivent
vivre sur E:, il faut ajouter une clé `"dossier"` dans
`Scans/_documents.json` et la faire respecter par `trouver_pdf()` — ce n'est
pas fait.

**Les noms de fichiers de `Scans OCR/gia-pha-ho-trinh/` suivent encore
l'ancienne numérotation**, celle qui a glissé là où le numériseur avait
retourné des feuilles. Les citations de l'arbre portent les bons numéros.
**En cas de doute, c'est l'arbre qui fait foi, pas le nom du fichier.** Les
quatre pages renumérisées le 23 octobre sont dans le sous-dossier
`_pages-51-52-83-84/` pour cette raison.

---

## Les deux leçons que le projet a payées cher

**Un compte annoncé qui ne tombe pas juste désigne la page suivante avant de
désigner un enfant disparu.** (18 octobre : le douzième enfant de Fortunat
Jean ouvrait la page 279.)

**Quand un fichier dérivé et l'image se contredisent, c'est l'image qui a
raison.** (22 octobre : quatre pages déclarées manquantes ne l'étaient pas ;
j'avais cru `_inventaire.json` au lieu de lire le folio imprimé.)

Et la règle de méthode qui en découle : **valider avant d'écrire, jamais
après.** Tout correctif Python finit par `ast.parse()` avant
`write_text()`.
