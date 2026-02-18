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

### Conditions

```text
si total > 0:
    afficher("positif")
sinon:
    afficher("nul ou negatif")
```

### Boucles

```text
soit somme = 0
pour i dans intervalle(5):
    somme = somme + i
afficher(somme)
```

### Fonctions

```text
fonction carre(x):
    retourner x * x

afficher(carre(6))
```

### Collections et slicing

```text
soit valeurs = [10, 20, 30, 40]
afficher(valeurs[1:3])
afficher(valeurs[::-1])
```

### Comprehensions

```text
soit carres = [x * x pour x dans intervalle(6)]
afficher(carres)
```

### Classes, imports, assertions

Le pipeline prend en charge:

- classes;
- imports;
- assertions;
- affectations chainees;
- deconstruction de tuples;
- parametres par defaut, `*args`, `**kwargs`;
- decorateurs;
- f-strings;
- chaines multilignes (triple quotes).

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

## 9. Bonnes pratiques

- Utiliser un seul style lexical par fichier (francais ou autre) pour garder le code lisible.
- Verifier les mots-cles disponibles via `:kw fr`.
- Activer `--show-python` au debug pour comprendre la transpilation.
- Ecrire des tests de bout en bout avec `ProgramExecutor` pour valider la semantique.

## 10. Documentation associee

- Guide usage: [USAGE.md](../USAGE.md)
- Reference technique: [README docs](README.md)
- Onboarding nouvelles langues: [language_onboarding.md](language_onboarding.md)

