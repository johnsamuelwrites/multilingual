# セマンティック検索 — Multilingual 1.0 コア
# embed + nearest + ~= でベクトル検索を示す

observe var クエリ: str = ""
observe var 結果: str = ""

fn 検索する(質問: str) -> str uses ai:
    let ベクトル = embed @text-embedding-3: 質問
    let 最近傍 = nearest(ベクトル, 知識ベース, top_k=3)
    let 回答 = generate @claude-sonnet: 最近傍 |> format_context
    return 回答

fn 意図を分類する(入力: str) -> str uses ai:
    if 入力 ~= "こんにちは":
        return "greeting"
    if 入力 ~= "ありがとう":
        return "gratitude"
    return "other"

canvas 検索ビュー {
    observe 結果
}
