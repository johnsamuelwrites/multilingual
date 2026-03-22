# Interactive Playground

Try **Multilingual 1.0** directly in your browser — no installation required.

Multilingual is the only AI programming platform where the same agent logic,
reactive UI, and semantic search pipeline is idiomatic in any of 17 human
languages.

## What you can do

- Write programs using keywords from any of the **17 supported languages**
  (English, French, Spanish, German, Hindi, Arabic, Bengali, Tamil, Chinese,
  Japanese, Italian, Portuguese, Polish, Dutch, Swedish, Danish, Finnish)
- Use **Core 1.0** language features: `fn`, `|>`, `?`, `~=`, `observe var`,
  `@agent`, `@tool`, `prompt`, `think`, `stream`, `embed`
- Click **▶ Run** (or press **Ctrl+Enter**) to execute the code
- Inspect the **Semantic IR** — the typed intermediate representation that
  drives all backends
- Explore the **Generated Python** and **WAT / WASM** views

## Deployment models

### Live playground (Pyodide)

Ideal for exploration, teaching, and instant feedback. First load takes a few
seconds while the WASM runtime (~12 MB) initializes. Subsequent visits are
fast thanks to browser caching.

**[→ Open the Interactive Playground](playground.html)**

### Prebuilt bundle (ahead-of-time)

For production web apps, compile ahead of time with `build-wasm-bundle`, ship
`module.wasm`, and load it with the generated `host_shim.js` — no runtime
download required.

```
multilingual build-wasm-bundle my_app.ml --out-dir dist/wasm
```

Live demos using this approach are in [`examples/browser`](../../examples/browser/).

## Core 1.0 example: the same agent in three languages

=== English
```
fn summarize(text: str) -> str uses ai:
    let result = think @claude-sonnet:
        Summarize the following in one sentence.
        text: text
    return result.conclusion

@agent(model=@claude-sonnet)
fn research_agent(query: str) -> str uses ai, net:
    let answer = summarize(query)
    return answer
```

=== Français
```
fn résumer(texte: str) -> str utilise ai:
    soit résultat = réfléchir @claude-sonnet:
        Résumer en une phrase.
        texte: texte
    retourner résultat.conclusion

@agent(modèle=@claude-sonnet)
fn agent_recherche(requête: str) -> str utilise ai, réseau:
    soit réponse = résumer(requête)
    retourner réponse
```

=== 日本語
```
関数 要約する(テキスト: str) -> str 使う ai:
    変数 結果 = 考える @claude-sonnet:
        一文で要約する。
        テキスト: テキスト
    返す 結果.結論

@エージェント(モデル=@claude-sonnet)
関数 調査エージェント(クエリ: str) -> str 使う ai, ネット:
    変数 回答 = 要約する(クエリ)
    返す 回答
```

All three programs have identical semantics — the surface language is purely cosmetic.

## Reactive counter example

```
observe var count: int = 0

fn increment():
    count = count + 1

canvas counter_view {
    observe count
}

on count.change:
    render counter_view with count
```

## Semantic matching example

```
fn classify_intent(input: str) -> str:
    if input ~= "hello":
        return "greeting"
    if input ~= "thank you":
        return "gratitude"
    return "other"
```

## Classic multilingual example

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
