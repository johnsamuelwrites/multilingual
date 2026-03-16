# Interactive Playground

Try the **Multilingual Programming Language** directly in your browser — no installation required.

For zero-install, instant-load browser execution the canonical path is the
**prebuilt bundle flow**: compile ahead of time with `build-wasm-bundle`,
ship `module.wasm`, and load it with the generated `host_shim.js` — no
runtime download required.  Live demos using this approach are in
[`examples/browser`](../examples/browser/).

The interactive playground below uses [Pyodide](https://pyodide.org) for
live, in-browser compilation (the source → WAT step requires a Python
runtime).  If first-load size matters for your use case, prefer the
prebuilt bundle flow above.

## What you can do

- Write programs using keywords from any of the **17 supported languages**
  (English, French, Spanish, German, Hindi, Arabic, Bengali, Tamil, Chinese, Japanese,
  Italian, Portuguese, Polish, Dutch, Swedish, Danish, Finnish)
- Click **▶ Run** (or press **Ctrl+Enter**) to execute the code
- See the **output** produced by your program
- Inspect the **Generated Python** — the transpiled source code the interpreter produces
- Explore the **WAT / WASM** view to see the real WebAssembly Text (WAT) emitted by
  `WATCodeGenerator` and watch it execute natively in your browser via `wabt.js`
- Use the browser example and `build-wasm-bundle` when you want a minimal-JS,
  precompiled deployment path instead of live compilation

## Launch the playground

**[→ Open the Interactive Playground](playground.html)**

> **Note:** The first load takes a few seconds while the WASM runtime (Pyodide, ~12 MB)
> downloads and initialises. Subsequent visits are faster thanks to browser caching.

## Example: the same program in four languages

=== English
```python
let a = 10
let b = 3
print("Sum:", a + b)
for i in range(1, 5):
    print(i, "squared =", i * i)
```

=== Français
```python
soit a = 10
soit b = 3
afficher("Somme:", a + b)
pour i dans intervalle(1, 5):
    afficher(i, "au carré =", i * i)
```

=== Deutsch
```python
sei a = 10
sei b = 3
ausgeben("Summe:", a + b)
für i in bereich(1, 5):
    ausgeben(i, "Quadrat =", i * i)
```

=== 日本語
```python
変数 a = 10
変数 b = 3
表示("合計:", a + b)
毎 i 中 範囲(1, 5):
    表示(i, "の2乗 =", i * i)
```

All four programs produce identical output — the language layer is purely cosmetic.
