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

Les fichiers source du langage utilisent l'extension `.ml` (par exemple `bonjour.ml`).

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
multilingual repl --lang fr
# alternative dev/debug:
# python -m multilingualprogramming repl --lang fr
```

Afficher aussi le Python genere:

```bash
multilingual repl --lang fr --show-python
# alternative dev/debug:
# python -m multilingualprogramming repl --lang fr --show-python
```

Executer un fichier source (ex. `bonjour.ml`):

```text
afficher("Bonjour le monde")
```

```bash
multilingual run bonjour.ml --lang fr
# alternative dev/debug:
# python -m multilingualprogramming run bonjour.ml --lang fr
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
déf carre(x):
    retour x * x

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
    déf __init__(soi, depart):
        soi.valeur = depart

    déf incrementer(soi):
        soi.valeur = soi.valeur + 1
        retour soi.valeur

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
a = b = c = 7
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
déf decrire(nom, role="developpeur", *competences, **meta):
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
déf tracer(fn):
    déf wrapper(*args, **kwargs):
        afficher("appel de", fn.__name__)
        retour fn(*args, **kwargs)
    retour wrapper

@tracer
déf addition(a, b):
    retour a + b

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

déf saluer(nom: chaine) -> chaine:
    retour f"Bonjour {nom}"
```
Sortie attendue (exemple): `Bonjour Alice` pour `afficher(saluer("Alice"))`.
Note: les deux formes `chaine` et `chaîne` sont acceptees.

- litteraux d'ensemble (`set`):

```text
soit uniques = {1, 2, 2, 3}
afficher(uniques)
```
Sortie attendue: un ensemble contenant `1, 2, 3` (ordre non garanti).

- `avec` avec plusieurs gestionnaires de contexte:

```text
avec open("a.txt") comme a, open("b.txt") comme b:
    afficher(a.read(), b.read())
```
Sortie attendue: contenu des deux fichiers, avec fermeture des deux contextes.
Note: certains built-ins et methodes Python restent sous leur nom universel
(par exemple `open`, `read`).

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
importer asyncio

asynchrone déf telecharger(url: chaine) -> chaine:
    retour f"contenu simulé pour {url}"

asynchrone déf lire(url: chaine) -> chaine:
    retour attendre telecharger(url)

afficher(asyncio.run(lire("https://exemple.fr")))
```
Sortie attendue: `contenu simulé pour https://exemple.fr`.
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

Le fichier `examples/complete_features_fr.ml` montre un scenario couvrant
plusieurs capacites combinees dans un seul programme.

- import avance avec alias:

```text
importer math
depuis math importer sqrt comme root_fn
```

- boucle `tantque`:

```text
soit compteur = 0
tantque compteur < 2:
    compteur = compteur + 1
```

- logique booleenne localisee:

```text
soit drapeau_ok = Vrai et non Faux
affirmer drapeau_ok
```

- gestion d'exceptions (`essayer` / `sauf` / `finalement`):

```text
essayer:
    soit racine = root_fn(16)
sauf Exception comme erreur_geree:
    soit racine = 0
finalement:
    afficher(racine)
```

- test d'identite avec `Rien`:

```text
afficher(total_acc est Rien)
```

Pour reproduire exactement cet exemple:

```bash
multilingual run examples/complete_features_fr.ml --lang fr
# alternative dev/debug:
# python -m multilingualprogramming run examples/complete_features_fr.ml --lang fr
```

## 5. Commandes REPL utiles

- `:help` afficher l'aide
- `:language fr` forcer la langue francaise
- `:python` activer/desactiver l'affichage du Python genere
- `:wat` activer/desactiver l'affichage du code WAT (WebAssembly Text) genere (alias `:wasm`)
- `:rust` activer/desactiver l'affichage du bridge Rust/Wasmtime genere (alias `:wasmtime`)
- `:reset` vider l'etat de la session
- `:kw [XX]` lister les mots-cles
- `:ops [XX]` lister les symboles et operateurs
- `:q` quitter

Drapeaux de demarrage equivalents :

```bash
multilingual repl --lang fr --show-python   # afficher Python au demarrage
multilingual repl --lang fr --show-wat      # afficher WAT au demarrage
multilingual repl --lang fr --show-rust     # afficher Rust/Wasmtime au demarrage
```

## 6. Architecture technique (ce qui se passe en interne)

Le flux est identique pour toutes les langues:

1. `Lexer` tokenize le code source Unicode.
2. `Parser` construit un AST.
3. `lower_to_semantic_ir` produit un `IRProgram`.
4. `core.semantic_analyzer.SemanticAnalyzer` valide portees, symboles et coherence.
5. `PythonCodeGenerator` genere du Python executable.
6. `ProgramExecutor` lance l'execution avec les built-ins runtime.

Ce design permet d'ajouter des langues sans reecrire parser/codegen.

## 7. API Python utile

Points d'entree principaux:

```python
from multilingualprogramming import (
    Lexer,
    Parser,
    PythonCodeGenerator,
    ProgramExecutor,
    REPL,
    KeywordRegistry,
)

from multilingualprogramming.core.semantic_analyzer import SemanticAnalyzer
```

Signatures des constructeurs importants:

```python
# Lexer : source est le premier argument positionnel (pas un argument nommé)
lexer = Lexer(source_code, language="fr")   # correct
# lexer = Lexer(language="fr")              # TypeError — source manquant

# ProgramExecutor : language doit être passé à __init__, pas à transpile/execute
executor = ProgramExecutor(language="fr")
python_code = executor.transpile(source_code)   # correct
# executor = ProgramExecutor()
# executor.transpile(source_code, language="fr")  # TypeError
```

Autres modules utiles:

- numeriques: `MPNumeral`, `UnicodeNumeral`, `RomanNumeral`, `ComplexNumeral`, `FractionNumeral`;
- date/heure: `MPDate`, `MPTime`, `MPDatetime`;
- inspection AST: `ASTPrinter`.

## 8. Exemple complet (francais)

```text
soit base = [1, 2, 3, 4, 5]
soit pairs = [x pour x dans base si x % 2 == 0]

déf moyenne(liste):
    retour somme(liste) / longueur(liste)

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

### Utilisation correcte de `ProgramExecutor`

`language` doit etre passe au constructeur (`__init__`), pas a `transpile()` ou `execute()`:

```python
# Correct
executor = ProgramExecutor(language="fr")
python_code = executor.transpile(source_code)
result = executor.execute(source_code)

# Incorrect — provoque un TypeError
executor = ProgramExecutor()
executor.transpile(source_code, language="fr")   # TypeError
```

## 11. Constructions IA natives, concurrence et observabilite

Cette section couvre les capacites avancees introduites dans Core 1.0 :
IA native, concurrence structuree, observabilite, placement distribue
et coordination d'agents.

### IA native

Les constructions IA s'utilisent dans les fonctions declarant `utilise ai` :

```text
fn resumer(texte: str) -> str utilise ai:
    retour requête @claude-sonnet: "Resumer : " + texte

fn raisonnement() utilise ai:
    soit r = réfléchir @claude-sonnet:
        Quelles sont les implications de la programmation IA ?
    afficher(r.conclusion)
```

Mots-cles IA disponibles en francais :

| Concept    | Francais        |
|------------|-----------------|
| prompt     | `requête`        |
| think      | `réfléchir`     |
| generate   | `générer`       |
| stream     | `diffuser`      |
| embed      | `incorporer`    |
| extract    | `extraire`      |
| classify   | `classifier`    |
| plan       | `planifier`     |
| transcribe | `transcrire`    |
| retrieve   | `récupérer`     |

Declarations d'agent et d'outil :

```text
@outil(description="Chercher sur le web")
fn recherche_web(requete: str) -> str utilise reseau:
    passer

@agent(modele=@claude-sonnet)
fn chercheur(question: str) -> str utilise ai, reseau:
    retour requête @claude-sonnet: question
```

### Concurrence structuree

```text
# Execution parallele — toutes les branches tournent simultanement
soit resultats = parallèle [
    requête @claude-sonnet: "Repondre A",
    requête @claude-sonnet: "Repondre B"
]

# Tache en arriere-plan — retourne immediatement un futur
soit tache = lancer operation_longue()

# Canal type — FIFO asynchrone entre taches
soit ch = canal()
```

Mots-cles de concurrence en francais :

| Concept  | Francais      |
|----------|---------------|
| parallel | `parallèle`   |
| spawn    | `lancer`      |
| channel  | `canal`       |
| send     | `envoyer`     |
| receive  | `recevoir`    |

### Observabilite

```text
fn surveille() utilise ai:
    # tracer — enregistre le temps ; la valeur passe sans modification
    soit res = tracer(requête @claude-sonnet: "Bonjour", "mon-label")

    # cout — retourne (valeur, InfoCout) avec le nombre de tokens
    soit reponse, info = cout(requête @claude-sonnet: "Qu'est-ce que l'IA ?")
    afficher(info)

    # expliquer — retourne (valeur, texte_explication)
    soit valeur, pourquoi = expliquer(reponse)
```

### Placement distribue

```text
@local
fn pretraiter(donnees: str) -> str:
    passer          # conseil : executer en local

@peripherique
fn classer_rapide(img: str) -> str utilise ai:
    passer          # conseil : executer a la peripherie

@nuage
@agent(modele=@claude-sonnet)
fn raisonnement_lourd(question: str) -> str utilise ai:
    passer          # conseil : executer dans le nuage
```

### Memoire et coordination d'agents

```text
fn avec_memoire() utilise ai:
    # Memoire de session (interface dict)
    soit faits = memoire("faits")
    faits["reponse"] = "Paris"

    # Persistante entre les executions
    soit cache = memoire("cache", scope="persistent")

@essaim(agents=[chercheur, redacteur, reviseur])
fn coordinateur(tache: str) -> str utilise ai:
    # Fan-out vers deux sous-agents simultanement
    soit brouillon, revue = parallèle [
        deleguer(redacteur, tache),
        deleguer(reviseur, tache)
    ]
    retour requête @claude-sonnet: "Fusionner : " + brouillon + "\n" + revue
```

Portees de memoire :
- `"session"` (defaut) — dict en memoire, perdu a la fin du processus
- `"persistent"` — sauvegarde JSON dans le repertoire courant
- `"shared"` — partage entre tous les agents d'un essaim

Exemple complet demontrant toutes ces constructions :

```bash
multilingual run examples/agent_fr.ml --lang fr
multilingual run examples/research_swarm_en.ml --lang en
```

## 10. Documentation associee

- **Mots-cles complets** (tous les mots-cles + alias built-ins): [mots_cles.md](mots_cles.md)
- **Modules et projets multi-fichiers** (packages, imports, tests): [modules.md](modules.md)
- **Backends WAT/WASM** (`:wat`, `:rust`, playground): [wasm.md](wasm.md)
- Guide usage: [USAGE.md](../_generated/USAGE.md)
- Reference technique: [README docs](../reference.md)
- Vue design (architecture + roadmap): [design.md](../design.md)
- Onboarding nouvelles langues: [language_onboarding.md](../language_onboarding.md)
