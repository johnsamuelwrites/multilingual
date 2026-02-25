# Modules, packages et projets multi-fichiers (français)

Ce document explique comment structurer un projet multilingual en plusieurs
fichiers `.ml`, comment écrire des tests avec pytest, et comment intégrer le
projet à l'outillage Python standard.

---

## 1. Fichier unique vs projet multi-fichiers

Un script isolé s'exécute directement :

```bash
multilingual run mon_script.ml --lang fr
```

Un projet réel décompose le code en modules et packages, exactement comme en Python.

---

## 2. Structure d'un module simple

Un module est un fichier `.ml`.  Il est importé par son nom de fichier sans
l'extension.

```
projet/
├── utilitaires.ml      # module
└── principal.ml        # point d'entrée
```

`utilitaires.ml` :
```text
déf ajouter(a, b):
    retour a + b

déf doubler(x):
    retour x * 2
```

`principal.ml` :
```text
importer utilitaires
afficher(utilitaires.ajouter(3, 4))    # 7
afficher(utilitaires.doubler(5))       # 10
```

```bash
multilingual run projet/principal.ml --lang fr
```

---

## 3. Structure d'un package

Un package est un répertoire contenant un fichier `__init__.ml`.

```
projet/
├── principal.ml
└── moteur/
    ├── __init__.ml
    ├── calcul.ml
    └── tri.ml
```

`moteur/__init__.ml` :
```text
# Initialisé à l'import du package ; peut exposer des symboles publics.
depuis .calcul importer Calculatrice
```

`moteur/calcul.ml` :
```text
classe Calculatrice:
    déf additionner(soi, a, b):
        retour a + b
```

`moteur/tri.ml` :
```text
déf tri_bulles(liste_val):
    soit n = longueur(liste_val)
    pour i dans intervalle(n):
        pour j dans intervalle(0, n - i - 1):
            si liste_val[j] > liste_val[j + 1]:
                soit tmp = liste_val[j]
                liste_val[j] = liste_val[j + 1]
                liste_val[j + 1] = tmp
    retour liste_val
```

`principal.ml` :
```text
depuis moteur importer Calculatrice
depuis moteur.tri importer tri_bulles

soit calc = Calculatrice()
afficher(calc.additionner(10, 32))          # 42

afficher(tri_bulles([3, 1, 4, 1, 5, 9]))    # [1, 1, 3, 4, 5, 9]
```

```bash
multilingual run projet/principal.ml --lang fr
```

---

## 4. Imports absolus et relatifs

### Imports absolus (recommandés pour les projets installés)

```text
importer moteur.calcul
depuis moteur importer Calculatrice
depuis moteur.tri importer tri_bulles
```

### Imports relatifs (au sein d'un même package)

Les imports relatifs fonctionnent lorsque le fichier fait partie d'un package
(son répertoire contient un `__init__.ml`).

```text
# Dans moteur/tri.ml — importer depuis le même package
depuis . importer calcul

# Dans moteur/sous/avance.ml — importer depuis le package parent
depuis .. importer calcul
depuis ..tri importer tri_bulles
```

> **Limitation** : les imports relatifs ne fonctionnent pas dans un script
> exécuté directement s'il n'est pas à l'intérieur d'un package (pas de
> `__init__.ml` dans son répertoire).  C'est le même comportement que Python.

---

## 5. Détection automatique de la langue

Le hook d'import détecte automatiquement la langue de chaque fichier `.ml` à
partir de ses mots-clés.  Il n'est pas nécessaire de passer `--lang fr` pour
chaque module importé : la langue est inférée fichier par fichier.

Un projet peut donc mélanger des modules dans différentes langues humaines, du
moment que chaque fichier est cohérent en lui-même.

---

## 6. Packaging et installation

Pour rendre le package importable depuis n'importe où (y compris les tests),
créez un `pyproject.toml` à la racine :

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "mon-projet"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["multilingualprogramming"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
"*" = ["*.ml"]
```

Structure recommandée pour un projet installable :

```
mon-projet/
├── pyproject.toml
├── src/
│   └── monprojet/
│       ├── __init__.ml
│       ├── module_a.ml
│       └── module_b.ml
└── tests/
    ├── conftest.py
    ├── test_module_a.py
    └── test_module_b.py
```

Installation en mode développement :

```bash
pip install -e .
```

Après installation, les imports absolus fonctionnent depuis partout :

```text
depuis monprojet importer module_a
```

---

## 7. Tests avec pytest

### Approche recommandée : ProgramExecutor dans des fichiers `.py`

pytest ne collecte pas les fichiers `.ml` directement.  Les tests s'écrivent en
Python en utilisant `ProgramExecutor` pour exécuter du code multilingual :

```python
# tests/test_calcul.py
import pytest
from multilingualprogramming import ProgramExecutor

def run_fr(code: str) -> str:
    """Exécute du code français et retourne la sortie capturée."""
    result = ProgramExecutor(language="fr").execute(code)
    assert result.success, f"Erreur d'exécution : {result.errors}"
    return result.output.strip()

def test_addition():
    assert run_fr("""
déf ajouter(a, b):
    retour a + b
afficher(ajouter(3, 4))
""") == "7"

def test_comprehension():
    assert run_fr("""
soit carres = [x * x pour x dans intervalle(5)]
afficher(carres)
""") == "[0, 1, 4, 9, 16]"

def test_classe():
    assert run_fr("""
classe Compteur:
    déf __init__(soi, debut):
        soi.val = debut
    déf incrementer(soi):
        soi.val += 1
        retour soi.val

soit c = Compteur(10)
afficher(c.incrementer())
afficher(c.incrementer())
""") == "11\n12"
```

```bash
python -m pytest tests/test_calcul.py -v
```

### Exécuter un fichier `.ml` entier depuis un test

```python
from pathlib import Path
from multilingualprogramming import ProgramExecutor

def test_fichier_complet():
    source = Path("src/monprojet/module_a.ml").read_text(encoding="utf-8")
    result = ProgramExecutor(language="fr").execute(source)
    assert result.success
    assert "résultat attendu" in result.output
```

### Utiliser `-m` pour tester un module individuellement

```bash
# Transpiler et afficher le Python généré (utile pour déboguer)
python -m multilingualprogramming compile src/monprojet/module_a.ml --lang fr

# Exécuter directement
python -m multilingualprogramming run src/monprojet/module_a.ml --lang fr
```

### conftest.py partagé

```python
# tests/conftest.py
import pytest
from multilingualprogramming import ProgramExecutor

@pytest.fixture
def executeur_fr():
    """Fixture : exécuteur français avec sortie capturée."""
    return ProgramExecutor(language="fr")

@pytest.fixture
def run_fr(executeur_fr):
    """Fixture : fonction helper run_fr(code) -> str."""
    def _run(code: str) -> str:
        result = executeur_fr.execute(code)
        assert result.success, result.errors
        return result.output.strip()
    return _run
```

Utilisation dans un test :

```python
def test_avec_fixture(run_fr):
    assert run_fr("afficher(2 + 2)") == "4"
```

---

## 8. Débogage

### Voir le Python généré

```bash
# En ligne de commande
multilingual compile mon_fichier.ml --lang fr

# Dans le REPL
multilingual repl --lang fr --show-python
```

### Messages d'erreur

Les erreurs de syntaxe indiquent la ligne et la colonne dans le fichier `.ml` :

```
ParseError: Lexer error at line 5, column 3: Identifiant attendu, obtenu 'tantque'
```

Les erreurs sémantiques (variable non définie, etc.) sont également localisées.

Les erreurs d'exécution affichent le type d'exception Python correspondant :

```
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

Activer `--show-python` pour voir le code Python exact qui a levé l'erreur.

---

## 9. Limitations connues

| Limitation | Contournement |
|------------|---------------|
| Les imports relatifs nécessitent d'être dans un package (`__init__.ml` présent) | Utiliser des imports absolus pour les scripts autonomes |
| pytest ne collecte pas les `.ml` directement | Écrire les tests en Python avec `ProgramExecutor` |
| `__slots__`, metaclasses, `typing.Protocol` | Utiliser les équivalents Python via `importer` |
| Les fichiers `.ml` ne sont pas inclus automatiquement dans les wheels | Ajouter `"*.ml"` dans `package-data` dans `pyproject.toml` |
