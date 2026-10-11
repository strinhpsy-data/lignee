# Demande D-002 — L'arbre de Samuel

> Recopiée mot pour mot, selon la règle du protocole : toute nouvelle demande
> est transcrite avant d'être interprétée. Les interprétations sont plus bas,
> dans une section séparée, et elles ont été validées le 2026-10-11.

---

## D-002.1 — Les six spécifications

> « Quelques spécifications concernant le projet d'arbre généalogique et j'aimerais
> que tu vérifie sa structure pour que ce soit facile à implanter.
>
> 1. Je prévois que ce soit l'arbre généalogique de mon fils Samuel
> 2. Je veux qu'il puisse ajouter des individus dans le futur (ex. sa conjointe,
>    ses enfants, les parents de sa conjointe, etc.
> 3. L'arbre généalogique aura donc 4 branches "fortes": celle de ma mère,
>    Fernande Jean, celle de mon père Hieu-Duc Trinh, celle de la mère de ma
>    conjointe Valérie Gagné (et mère de Samuel), Justine Dionne, et celle du
>    père de Valérie, Richard Gagné.
> 4. Je ne sais pas ce qu'on fera pour les branches de la famille de Valérie,
>    mais pour les miennes, j'aimerais pour "exporter" une branche pour la
>    fournir à mes oncles, tantes, cousins, etc. et les inviter à consolider les
>    informations qu'ils ont et veulent partager à mettant à jour les
>    informations qu'ils détiennent et en les transmettant à ma mère (pour les
>    Jean) et à mon oncle (pour les Trinh)
> 5. Ce serait sympathique d'avoir les informations de santé qu'ils détiennent,
>    une inventaire de recette de cuisine, de photo, les moments importants de
>    leurs vies, ou ils sont enterrés et peut-être d'autres éléments sympathiques
>    à partager ou importants dans une vie.
> 6. Évidemment, ça ne sert à rien d'envoyer les informations de la famille
>    Trinh à la famille Jean et vice-versa. »

## D-002.2 — Sens d'« ascendance »

Réponse à une question de cadrage sur le sens de l'arbre :

> « Ascendance seule pour l'instant »

## D-002.3 — La frontière de l'export

Réponse à une question de cadrage sur ce que contient une branche exportée :

> « 1, mais avec les noms des enfants et des conjoints: par exemple Valérie
> figure dans l'arbre des Jean comme ma conjointe »

## D-002.4 — Ce que les parents versent

> « Elle met ce qu'elle. Elle peut ne rien mettre. Idem pour les recette de
> cuisine ou les photos »

## D-002.5 — Les deux sens

> « Est-il possible de faire l'arbre à la fois descendant et ascendant? »

## D-002.6 — Le pivot

> « Samuel reste centré à chaque ouverture de l'arbre »

## D-002.7 — Validation

> « Je confirme les validations demandées »

Les deux validations demandées portaient sur :

1. la relecture d'« ascendance » comme **graphe de parenté** et non comme chaîne
   d'ancêtres — sur les 60 personnes du fichier Jean, 7 sont des ancêtres directs
   de Sébastien et 53 sont des collatéraux ; un arbre d'ascendance stricte
   masquerait précisément les parents à qui la branche est destinée ;
2. la **règle de frontière** de l'export, telle qu'elle est écrite dans
   `docs/avant/07-branches-export.md`.

---

## Ce que ces demandes ne disent pas

À ne pas combler par déduction. Chacun de ces points est soit une question
ouverte dans `docs/apres/11-questions.md`, soit hors phase 1.

- **Le sort des branches Gagné et Dionne.** D-002.4 dit « je ne sais pas ce qu'on
  fera ». La phase 1 les accueille dans le modèle de données et les dessine ;
  elle ne décide pas si elles s'exportent ni vers qui.
- **Le chemin de retour des contributions.** Un parent reçoit un fichier HTML ;
  il ne peut pas l'éditer. Comment il renvoie ce qu'il a ajouté n'est pas tranché
  (`Q-02`).
- **Où vivent les recettes.** Sébastien a un projet distinct, « Livres de recette
  Famille Trinh ». La duplication est la seule réponse certainement fausse
  (`Q-01`).
- **Quels parents reçoivent quoi.** La liste nominative des destinataires est
  éditoriale. Le programme produit un fichier par branche ; il n'envoie rien.
