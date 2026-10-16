# Demande D-004 — Lever l'interdit 4

## La demande, mot pour mot

> « Lève l'interdit 4. Je veux fonctionner avec un serveur local. »

## Ce que l'interdit 4 protégeait

> « **Aucun accès réseau** depuis le générateur ni depuis les pages produites.
> Tout doit fonctionner sur un poste hors ligne, et les fichiers produits
> doivent s'ouvrir sans connexion. »

Une seule phrase, mais **deux garanties distinctes**, et la demande n'en vise
qu'une :

| | Ce qui est protégé | La demande y touche ? |
|---|---|---|
| **A** | Le générateur ne va rien chercher dehors — ni police web, ni CDN, ni requête. C'est ce qui rend la sortie autonome. | **non** |
| **B** | Les pages produites s'ouvrent sans rien à côté. C'est ce qui fait qu'un double-clic suffit, chez n'importe qui, dans dix ans. | **oui, en partie** |

## Pourquoi je ne l'efface pas

La garantie **B** n'a pas été posée pour le confort de Sébastien : elle a été
posée pour **sa tante**. Un export de branche qui exigerait de lancer un
service avant de s'ouvrir serait cassé pour exactement les gens à qui il est
destiné — et ils n'auraient personne à appeler.

Or la demande porte sur le poste de travail, pas sur l'export. Sur sa propre
machine, Sébastien a le projet, les `.bat` et Python. Sa tante n'a qu'un
dossier reçu par courriel.

## Ce que devient l'interdit 4

> **4. Le générateur ne fait aucun appel réseau, et les fichiers produits
> s'ouvrent sans rien à côté.** Un serveur local — lié à `127.0.0.1`,
> lancé à la main, sur le poste de travail — est permis pour le confort de
> saisie. Mais **tout export de branche doit rester utilisable par double-clic,
> sans serveur, sans installation, hors ligne.** Une page qui ne fonctionne
> que servie est un défaut, pas une fonction.

## Ce qui en découle pour le code

**La même page doit marcher des deux façons.** Ouverte en `file://` elle rend
un fichier d'ajouts, comme aujourd'hui ; servie en `http://127.0.0.1` elle
écrit directement. C'est la page qui constate comment elle a été ouverte, et
non deux versions à maintenir — deux versions divergeraient, et c'est celle
qu'on teste le moins qui partirait chez la parenté.

**L'air-gap de Wilfred n'est pas entamé** : une écoute sur la boucle locale ne
sort pas de la machine. Le pare-feu en blocage sortant reste pertinent et
suffisant.

**Le serveur reste sous les mêmes interdits que le reste** : bibliothèque
standard seule, aucune suppression, écriture confinée à `photos/`.


---

## Reformulation du 2026-10-16, après objection

> « Ce n'est pas une bonne idée de me limiter pendant que je développe…
> L'interdit serait mieux servi en n'étant appliqué qu'aux exportations pour
> la famille »

Objection retenue. Ma première rédaction gardait l'en-tête « les fichiers
produits s'ouvrent sans rien à côté » et découpait le serveur local comme
une **exception tolérée**. C'était la mauvaise polarité : elle contraignait
le poste de travail, où la contrainte ne protège personne, et ne faisait de
l'export qu'un cas particulier.

La bonne rédaction attache l'interdit à **ce qui sort de la maison**. Sur son
poste, Sébastien utilise ce qu'il veut.

### Ce que la reformulation gagne, et que je n'avais pas vu

Une règle sur la *façon d'écrire* se tient par discipline : personne ne peut
l'éprouver, on ne peut que s'en souvenir. Une règle sur **une propriété de
l'export** s'éprouve par un contrôle.

D'où `T-37` : la version partageable est ouverte dans un navigateur **en
`file://`**, et doit se charger sans erreur, sans requête réseau, et offrir
le chemin de retour par fichier. L'interdit cesse d'être une consigne pour
devenir une mesure.
