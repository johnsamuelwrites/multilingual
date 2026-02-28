# Backends WebAssembly et WAT (français)

Ce document explique comment visualiser et utiliser le code WebAssembly Text
(WAT) et le code Rust/Wasmtime générés à partir de programmes multilingues.

---

## 1. Vue d'ensemble des backends

Le pipeline multilingual dispose de trois backends de sortie :

| Backend | Description | Commande REPL | Drapeau CLI |
|---------|-------------|---------------|-------------|
| **Python** | Transpilation vers Python (backend par défaut) | `:python` | `--show-python` |
| **WAT** | WebAssembly Text Format — exécutable dans le navigateur via wabt.js | `:wat` | `--show-wat` |
| **Rust/Wasmtime** | Scaffold Rust pour compilation locale via Wasmtime | `:rust` | `--show-rust` |

---

## 2. Afficher le WAT dans le REPL

### Activer/désactiver l'affichage WAT

```bash
multilingual repl --lang fr
```

Dans le REPL :
```
> :wat
Show WAT: on
> déf carre(x):
...     retour x * x
[WAT]
(module
  (func $carre (param $x f64) (result f64)
    local.get $x
    local.get $x
    f64.mul)
  (export "carre" (func $carre)))
> :wat
Show WAT: off
```

### Activer WAT au démarrage

```bash
multilingual repl --lang fr --show-wat
```

---

## 3. Afficher le code Rust/Wasmtime dans le REPL

```bash
multilingual repl --lang fr --show-rust
```

Dans le REPL :
```
> :rust
Show Rust/Wasmtime: on
> déf carre(x):
...     retour x * x
[Rust/Wasmtime]
use wasmtime::*;

fn main() -> anyhow::Result<()> {
    let engine = Engine::default();
    let module = Module::from_file(&engine, "output.wasm")?;
    // ... scaffold de bridge Rust généré
    Ok(())
}
```

### Alias REPL

| Commande | Alias | Effet |
|----------|-------|-------|
| `:wat`   | `:wasm` | Bascule l'affichage WAT |
| `:rust`  | `:wasmtime` | Bascule l'affichage Rust/Wasmtime |

---

## 4. Afficher WAT depuis la ligne de commande

```bash
# Voir le Python généré
multilingual compile mon_programme.ml --lang fr

# Voir le WAT généré (via le REPL avec --show-wat)
multilingual repl --lang fr --show-wat
```

Pour générer du WAT depuis Python directement :

```python
from multilingualprogramming import ProgramExecutor
from multilingualprogramming.codegen.wat_generator import WATCodeGenerator

source = """
déf carre(x):
    retour x * x
"""

executor = ProgramExecutor(language="fr")
core = executor.to_core_ir(source)

wat = WATCodeGenerator().generate(core)
print(wat)
```

---

## 5. Playground interactif (navigateur)

Le playground en ligne (`docs/playground.html`) propose trois onglets :

- **Python** — code Python transpilé, exécuté côté serveur
- **WAT/WASM** — code WAT généré, exécuté dans le navigateur via
  `wabt.js` + `WebAssembly.instantiate()`
- **Rust/Wasmtime** — scaffold Rust pour compilation locale

Pour lancer le playground localement :

```bash
# Générer les fichiers docs/ staging
python stage_docs.py

# Démarrer un serveur HTTP simple
python -m http.server 8000 --directory docs/
# puis ouvrir http://localhost:8000/playground.html
```

---

## 6. Générer du WAT par programme

```python
from multilingualprogramming.codegen.wat_generator import WATCodeGenerator
from multilingualprogramming.codegen.executor import ProgramExecutor

source_fr = """
déf factorielle(n: entier) -> entier:
    si n <= 1:
        retour 1
    retour n * factorielle(n - 1)
"""

core = ProgramExecutor(language="fr").to_core_ir(source_fr)
wat_source = WATCodeGenerator().generate(core)
print(wat_source)
```

---

## 7. Générer le bridge Rust/Wasmtime par programme

```python
from multilingualprogramming.codegen.wasm_generator import WasmCodeGenerator
from multilingualprogramming.codegen.executor import ProgramExecutor

source_fr = """
déf somme_tableau(valeurs):
    retour somme(valeurs)
"""

core = ProgramExecutor(language="fr").to_core_ir(source_fr)
rust_source = WasmCodeGenerator().generate(core)
print(rust_source)
```

---

## 8. Limitations actuelles du backend WAT

| Limitation | Statut |
|------------|--------|
| Seuls les types numériques (`i32`, `f64`) et les chaînes simples sont supportés | Partiel |
| Les listes, dicts et classes Python ne sont pas compilables en WAT natif | Non supporté — utiliser le backend Python pour ces cas |
| La récursion profonde peut dépasser la pile WASM | Limiter la profondeur de récursion |
| Le backend Rust nécessite `rustc` avec la cible `wasm32-wasip1` | `rustup target add wasm32-wasip1` |

Pour les fonctions à dominante numérique (calcul scientifique, cryptographie,
traitement de signal), le backend WAT apporte des gains de performance
significatifs par rapport au backend Python.
