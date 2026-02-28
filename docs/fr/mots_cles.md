# Référence complète des mots-clés et alias (français)

Ce document liste exhaustivement tous les mots-clés du langage et les alias
français des fonctions intégrées.  Il sert de référence rapide lors du
développement d'un projet multilingue en français.

---

## 1. Mots-clés du langage

### Déclarations et définitions

| Concept Python | Mot-clé français | Notes |
|----------------|------------------|-------|
| `def`          | `déf`            | Définition de fonction |
| `class`        | `classe`         | Définition de classe |
| `return`       | `retour`         | Retour de valeur |
| `yield`        | `produire`       | Générateur (voir §3) |
| `yield from`   | `produire depuis`| Délégation de générateur |
| `lambda`       | `lambda`         | Fonction anonyme (inchangé) |
| `pass`         | `passer`         | Instruction vide |
| `del`          | `supprimer`      | Suppression de variable/élément |

### Structures de contrôle

| Concept Python  | Mot-clé français | Notes |
|-----------------|------------------|-------|
| `if`            | `si`             | |
| `elif`          | `sinon si`       | Aussi : `sinonsi` |
| `else`          | `sinon`          | |
| `for`           | `pour`           | Aussi : `pour chaque` |
| `while`         | `tantque`        | |
| `break`         | `arrêter`        | |
| `continue`      | `continuer`      | |
| `match`         | `selon`          | Filtrage par motif (Python 3.10+) |
| `case`          | `cas`            | |
| `case _:`       | `cas défaut:`    | Aussi : `cas defaut:` |
| `with`          | `avec`           | Gestionnaire de contexte |
| `as`            | `comme`          | Alias (import, with, except) |
| `in`            | `dans`           | Appartenance / itération |
| `assert`        | `affirmer`       | Assertion |

### Importation

| Concept Python        | Mot-clé français        |
|-----------------------|-------------------------|
| `import X`            | `importer X`            |
| `import X as Y`       | `importer X comme Y`    |
| `from X import Y`     | `depuis X importer Y`   |
| `from X import Y as Z`| `depuis X importer Y comme Z` |
| `from . import Y`     | `depuis . importer Y`   |
| `from .. import Y`    | `depuis .. importer Y`  |
| `from .sub import Y`  | `depuis .sous importer Y` |

### Gestion d'exceptions

| Concept Python | Mot-clé français |
|----------------|------------------|
| `try`          | `essayer`        |
| `except`       | `sauf`           |
| `except E as e`| `sauf E comme e` |
| `finally`      | `finalement`     |
| `raise`        | `lever`          |
| `raise X from Y` | `lever X depuis Y` |

### Programmation asynchrone

| Concept Python | Mot-clé français |
|----------------|------------------|
| `async def`    | `asynchrone déf` |
| `await`        | `attendre`       |

### Variables et portée

| Concept Python | Mot-clé français | Notes |
|----------------|------------------|-------|
| (assignment)   | `soit`           | Déclaration optionnelle |
| `global`       | `global`         | Inchangé |
| `nonlocal`     | `nonlocale`      | |

### Valeurs littérales et opérateurs logiques

| Concept Python | Mot-clé français |
|----------------|------------------|
| `True`         | `Vrai`           |
| `False`        | `Faux`           |
| `None`         | `Rien`           |
| `and`          | `et`             |
| `or`           | `ou`             |
| `not`          | `non`            |
| `is`           | `est`            |
| `is not`       | `n'est pas`      |
| `not in`       | `pas dans`       |

### Annotations de types

| Type Python | Annotation française |
|-------------|----------------------|
| `int`       | `entier`             |
| `float`     | `flottant`           |
| `str`       | `chaine` / `chaîne`  |
| `bool`      | `booléen`            |
| `list`      | `liste`              |
| `dict`      | `dico`               |

---

## 2. Alias français des fonctions intégrées

Les noms Python universels restent utilisables en parallèle.

### Entrées / sorties

| Python    | Français                          |
|-----------|-----------------------------------|
| `print`   | `afficher`                        |
| `input`   | `saisir` / `entrée` / `entrer`    |
| `open`    | `ouvrir`                          |

### Collections et itération

| Python       | Français                            |
|--------------|-------------------------------------|
| `range`      | `intervalle`                        |
| `len`        | `longueur`                          |
| `sum`        | `somme`                             |
| `min`        | `minimum`                           |
| `max`        | `maximum`                           |
| `sorted`     | `trier` / `trié`                    |
| `reversed`   | `inverser` / `inversé`              |
| `enumerate`  | `énumérer` / `enumerer`             |
| `zip`        | `fusionner` / `apparier`            |
| `map`        | `appliquer`                         |
| `filter`     | `filtrer`                           |
| `list`       | `liste`                             |
| `set`        | `ensemble`                          |
| `frozenset`  | `ensemble_gelé` / `ensemble_gele`   |
| `tuple`      | `nuplet` / `tuplet`                 |
| `dict`       | `dico`                              |
| `iter`       | `itérateur` / `iterateur`           |
| `next`       | `suivant` / `prochain`              |

### Mathématiques et conversion

| Python    | Français                        |
|-----------|---------------------------------|
| `abs`     | `valeurabsolue`                 |
| `round`   | `arrondir`                      |
| `pow`     | `puissance`                     |
| `divmod`  | `divmod`                        |

### Introspection et types

| Python        | Français                                    |
|---------------|---------------------------------------------|
| `type`        | `type_de`                                   |
| `isinstance`  | `est_instance`                              |
| `issubclass`  | `est_sous_classe`                           |
| `callable`    | `appelable`                                 |
| `repr`        | `représentation` / `representation`         |
| `dir`         | `répertoire` / `repertoire`                 |
| `hasattr`     | `a_attribut`                                |
| `getattr`     | `obtenir_attribut`                          |
| `setattr`     | `définir_attribut` / `definir_attribut`     |
| `delattr`     | `supprimer_attribut`                        |
| `hash`        | `hachage`                                   |

### Chaînes de caractères

| Python | Français                      |
|--------|-------------------------------|
| `chr`  | `caractère` / `caractere`     |
| `ord`  | `ordinal`                     |
| `format` | `formater`                  |

### Divers

| Python  | Français                    |
|---------|-----------------------------|
| `any`   | `un_quelconque`             |
| `all`   | `tous`                      |
| `bytes` | `octets`                    |
| `super` | `superieur` / `superclasse` |

---

## 3. Générateurs (`produire`)

```text
déf compter(n):
    soit i = 0
    tantque i < n:
        produire i
        i = i + 1

pour valeur dans compter(3):
    afficher(valeur)
```
Sortie : `0` `1` `2`

Délégation avec `produire depuis` :

```text
déf gen_pair():
    produire depuis intervalle(0, 10, 2)

afficher(liste(gen_pair()))
```
Sortie : `[0, 2, 4, 6, 8]`

---

## 4. Filtrage par motif (`selon` / `cas` / `défaut`)

```text
déf decrire(valeur):
    selon valeur:
        cas 1:
            afficher("un")
        cas 2:
            afficher("deux")
        cas défaut:
            afficher("autre")

decrire(1)
decrire(2)
decrire(99)
```
Sortie : `un` `deux` `autre`

Avec capture de variable et garde :

```text
déf classer(n: entier):
    selon n:
        cas x si x < 0:
            afficher("négatif", x)
        cas 0:
            afficher("zéro")
        cas x:
            afficher("positif", x)

classer(-3)
classer(0)
classer(7)
```
Sortie : `négatif -3` `zéro` `positif 7`

---

## 5. Décorateurs de classe

Les décorateurs standard Python s'utilisent sans traduction :

```text
classe Cercle:
    déf __init__(soi, rayon: flottant):
        soi._rayon = rayon

    @property
    déf rayon(soi) -> flottant:
        retour soi._rayon

    @staticmethod
    déf unite() -> "Cercle":
        retour Cercle(1.0)

    @classmethod
    déf depuis_diametre(cls, d: flottant) -> "Cercle":
        retour cls(d / 2)
```

---

## 6. Vérification rapide dans le REPL

Pour lister les mots-clés disponibles en français :

```bash
multilingual repl --lang fr
# puis dans le REPL :
:kw fr
:ops fr
```
