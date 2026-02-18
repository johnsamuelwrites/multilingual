# Guide complet de programmation (francais)

Ce document presente la programmation avec `multilingual` en francais.
Il couvre les capacites du langage, le flux d'execution, les exemples pratiques, et les points d'extension.

## 1. Objectif du projet

`multilingual` permet d'ecrire du code dans plusieurs langues humaines, tout en conservant un modele semantique unique.

Concretement:

- vous ecrivez des mots-cles dans votre langue (ex. `soit`, `pour`, `dans`, `afficher`);
- le compilateur interne les mappe vers des concepts universels;
- le code est transpile en Python puis execute.

## 2. Installation et demarrage rapide

Depuis la racine du projet:

```bash
pip install -r requirements.txt
# ou
pip install .
```

### Exemples "Hello world" multilingues

```text
# Anglais
print("Hello world")

# Francais
afficher("Bonjour le monde")

```

Lancer le REPL en francais:

```bash
python -m multilingualprogramming repl --lang fr
```

Afficher aussi le Python genere:

```bash
python -m multilingualprogramming repl --lang fr --show-python
```

## 3. Capacites principales du langage

### Variables et affectation

```text
soit total = 0
soit nom = "Alice"
```
Sortie attendue: aucune sortie directe (variables initialisees).

### Conditions

```text
si total > 0:
    afficher("positif")
sinon:
    afficher("nul ou negatif")
```
Sortie attendue (si `total = 0`): `nul ou negatif`

### Boucles

```text
soit somme = 0
pour i dans intervalle(5):
    somme = somme + i
afficher(somme)
```
Sortie attendue: `10`

### Fonctions

```text
fonction carre(x):
    retourner x * x

afficher(carre(6))
```
Sortie attendue: `36`

### Collections et slicing

```text
soit valeurs = [10, 20, 30, 40]
afficher(valeurs[1:3])
afficher(valeurs[::-1])
```
Sortie attendue:
- `[20, 30]`
- `[40, 30, 20, 10]`

### Comprehensions

```text
soit carres = [x * x pour x dans intervalle(6)]
afficher(carres)
```
Sortie attendue: `[0, 1, 4, 9, 16, 25]`

### Classes, imports, assertions

Le pipeline prend en charge:

- classes (exemple):

```text
classe Compteur:
    fonction __init__(soi, depart):
        soi.valeur = depart

    fonction incrementer(soi):
        soi.valeur = soi.valeur + 1
        retourner soi.valeur

soit c = Compteur(10)
afficher(c.incrementer())
```
Sortie attendue: `11`

- imports (exemple):

```text
importer math
soit rayon = 3
soit surface = math.pi * rayon * rayon
afficher(surface)
```
Sortie attendue: environ `28.2743338823`

- assertions (exemple):

```text
soit resultat = somme([1, 2, 3])
affirmer resultat == 6
afficher("test ok")
```
Sortie attendue: `test ok` (sinon erreur d'assertion si la condition est fausse).

- autres capacites avancees:

- affectations chainees (exemple):

```text
soit a = b = c = 7
afficher(a, b, c)
```
Sortie attendue: `7 7 7`

- deconstruction de tuples (exemple):

```text
soit point = (4, 9)
soit x, y = point
afficher(x, y)
```
Sortie attendue: `4 9`

- parametres par defaut, `*args`, `**kwargs` (exemple):

```text
fonction decrire(nom, role="developpeur", *competences, **meta):
    afficher("Nom:", nom)
    afficher("Role:", role)
    afficher("Competences:", competences)
    afficher("Meta:", meta)

decrire("Nina", "ingenieure", "python", "tests", equipe="plateforme", senior=True)
```
Sortie attendue (exemple):
- `Nom: Nina`
- `Role: ingenieure`
- `Competences: ('python', 'tests')`
- `Meta: {'equipe': 'plateforme', 'senior': True}`

- decorateurs (exemple):

```text
fonction tracer(fn):
    fonction wrapper(*args, **kwargs):
        afficher("appel de", fn.__name__)
        retourner fn(*args, **kwargs)
    retourner wrapper

@tracer
fonction addition(a, b):
    retourner a + b

afficher(addition(2, 5))
```
Sortie attendue:
- `appel de addition`
- `7`

- f-strings (exemple):

```text
soit nom = "Amina"
soit score = 95
afficher(f"{nom} a obtenu {score}%")
```
Sortie attendue: `Amina a obtenu 95%`

- chaines multilignes / triple quotes (exemple):

```text
soit message = """Ligne 1
Ligne 2
Ligne 3"""
afficher(message)
```
Sortie attendue:
`Ligne 1`
`Ligne 2`
`Ligne 3`

### Nouvelles syntaxes (mise a jour)

- annotations de type (variables, parametres, retour):

```text
soit age: entier = 42

def saluer(nom: chaine) -> chaine:
    retourner f"Bonjour {nom}"
```
Sortie attendue (exemple): `Bonjour Alice` pour `afficher(saluer("Alice"))`.

- litteraux d'ensemble (`set`):

```text
soit uniques = {1, 2, 2, 3}
afficher(uniques)
```
Sortie attendue: un ensemble contenant `1, 2, 3` (ordre non garanti).

- `with` avec plusieurs gestionnaires de contexte:

```text
with ouvrir("a.txt") as a, ouvrir("b.txt") as b:
    afficher(a.lire(), b.lire())
```
Sortie attendue: contenu des deux fichiers, avec fermeture des deux contextes.

- depliage de dictionnaires:

```text
soit base = {"langue": "fr", "niveau": "intermediaire"}
soit extra = {"niveau": "avance", "theme": "tests"}
soit profil = {**base, **extra}
afficher(profil)
```
Sortie attendue: `{'langue': 'fr', 'niveau': 'avance', 'theme': 'tests'}`.

- litteraux numeriques hex/octal/binaire et notation scientifique:

```text
soit hexa = 0xFF
soit octal = 0o77
soit binaire = 0b1010
soit petit = 1.5e-3
afficher(hexa, octal, binaire, petit)
```
Sortie attendue: `255 63 10 0.0015`.

- programmation asynchrone (`async` / `await`):

```text
asynchrone def lire(url: chaine) -> chaine:
    retourner attendre telecharger(url)
```
Note: `attendre` (`await`) est valide uniquement dans une fonction asynchrone.

- operateur walrus (`:=`):

```text
soit resultat = (n := 10) + 5
afficher(n, resultat)
```
Sortie attendue: `10 15`.

## 4. Alias francais des built-ins

Certains built-ins universels ont des alias localises.
Exemples frequents:

- `intervalle(...)` pour `range(...)`
- `longueur(...)` pour `len(...)`
- `somme(...)` pour `sum(...)`
- `afficher(...)` pour l'affichage

Les noms universels Python restent utilisables en parallele.

## 5. Commandes REPL utiles

- `:help` afficher l'aide
- `:language fr` forcer la langue francaise
- `:python` activer/desactiver l'affichage du Python genere
- `:reset` vider l'etat de la session
- `:kw [XX]` lister les mots-cles
- `:ops [XX]` lister les symboles et operateurs
- `:q` quitter

## 6. Architecture technique (ce qui se passe en interne)

Le flux est identique pour toutes les langues:

1. `Lexer` tokenize le code source Unicode.
2. `Parser` construit un AST.
3. `SemanticAnalyzer` valide portees, symboles et coherence.
4. `PythonCodeGenerator` genere du Python executable.
5. `ProgramExecutor` lance l'execution avec les built-ins runtime.

Ce design permet d'ajouter des langues sans reecrire parser/codegen.

## 7. API Python utile

Points d'entree principaux:

```python
from multilingualprogramming import (
    Lexer,
    Parser,
    SemanticAnalyzer,
    PythonCodeGenerator,
    ProgramExecutor,
    REPL,
    KeywordRegistry,
)
```

Autres modules utiles:

- numeriques: `MPNumeral`, `UnicodeNumeral`, `RomanNumeral`, `ComplexNumeral`, `FractionNumeral`;
- date/heure: `MPDate`, `MPTime`, `MPDatetime`;
- inspection AST: `ASTPrinter`.

## 8. Exemple complet (francais)

```text
soit base = [1, 2, 3, 4, 5]
soit pairs = [x pour x dans base si x % 2 == 0]

fonction moyenne(liste):
    retourner somme(liste) / longueur(liste)

si longueur(pairs) > 0:
    afficher("Pairs:", pairs)
    afficher("Moyenne:", moyenne(pairs))
sinon:
    afficher("Aucune valeur paire")
```
Sortie attendue:
- `Pairs: [2, 4]`
- `Moyenne: 3.0`

## 9. Bonnes pratiques

- Utiliser un seul style lexical par fichier (francais ou autre) pour garder le code lisible.
- Verifier les mots-cles disponibles via `:kw fr`.
- Activer `--show-python` au debug pour comprendre la transpilation.
- Ecrire des tests de bout en bout avec `ProgramExecutor` pour valider la semantique.

## 10. Documentation associee

- Guide usage: [USAGE.md](../USAGE.md)
- Reference technique: [README docs](README.md)
- Onboarding nouvelles langues: [language_onboarding.md](language_onboarding.md)
