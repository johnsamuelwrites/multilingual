取込 math
から math 取込 sqrt として root_fn

変数 共有_カウンタ = 3

関数 増加_グローバル():
    大域 共有_カウンタ
    共有_カウンタ = 共有_カウンタ + 2
    戻る 共有_カウンタ

関数 作成_カウンタ(開始):
    変数 total = 開始
    関数 ステップ():
        非局所 total
        total = total + 1
        戻る total
    戻る ステップ

変数 次_カウンタ = 作成_カウンタ(5)
変数 最初_ステップ = 次_カウンタ()
変数 第二_ステップ = 次_カウンタ()

付き 開く("tmp_complete_en.txt", "w", encoding="utf-8") として 書込_ハンドル:
    書込_ハンドル.write("ok")

変数 ファイル_テキスト = ""
付き 開く("tmp_complete_en.txt", "r", encoding="utf-8") として 読込_ハンドル:
    ファイル_テキスト = 読込_ハンドル.read()

変数 ペア化_項目 = リスト(組み合わせ([1, 2, 3], [4, 5, 6]))
変数 ユニーク_値 = 集合([1, 1, 2, 3])
変数 固定_値 = タプル([10, 20, 30])
変数 最初_要素, *中央_要素, 最後_要素 = [1, 2, 3, 4]
変数 マージ_マップ = {**{"x": 1}, **{"y": 2}}

関数 ラベル_フォーマット関数(a, /, *, b):
    戻る f"{a}-{b:.1f}"

変数 ラベル_フォーマット = ラベル_フォーマット関数(7, b=3.5)
変数 種 = 0
変数 口髭_値 = (種 := 種 + 9)

クラス カウンタ_ボックス:
    関数 __init__(self, 開始_基底):
        self.値 = 開始_基底

クラス カウンタ_子ボックス(カウンタ_ボックス):
    関数 __init__(self, 開始_基底):
        親クラス(カウンタ_子ボックス, self).__init__(開始_基底)
        self.値 = self.値 + 1

関数 生成_三つ():
    毎 索引 中 範囲(3):
        生成 索引

変数 合計_生成 = 合計(生成_三つ())
変数 処理_済 = 偽

試行:
    もし 長さ(ユニーク_値) > 2:
        発生 ValueError("boom")
例外 ValueError として 処理_エラー:
    処理_済 = 真
最後に:
    変数 ルート_値 = 整数(root_fn(16))

変数 一時_値 = 99
削除 一時_値

変数 ループ_蓄積 = 0
毎 n 中 範囲(6):
    もし n == 0:
        パス
    もし n == 4:
        中断
    もし n % 2 == 0:
        続行
    ループ_蓄積 = ループ_蓄積 + n

変数 フラグ_正常 = 真 かつ ない 偽
断言 フラグ_正常

変数 子_ボックス = カウンタ_子ボックス(40)

表示(増加_グローバル())
表示(最初_ステップ, 第二_ステップ)
表示(ファイル_テキスト)
表示(長さ(ペア化_項目), 長さ(ユニーク_値), 固定_値[1])
表示(最初_要素, 中央_要素, 最後_要素)
表示(子_ボックス.値)
表示(合計_生成, ルート_値, 処理_済)
表示(マージ_マップ["x"] + マージ_マップ["y"], ラベル_フォーマット, 口髭_値)
表示(ループ_蓄積)
表示(共有_カウンタ は なし)

# Loop else clauses
変数 要素_発見 = 偽
毎 要素 中 範囲(3):
    もし 要素 == 10:
        要素_発見 = 真
        中断
でなければ:
    要素_発見 = "not_found"

変数 ループ_その他_値 = 0
間 ループ_その他_値 < 2:
    ループ_その他_値 = ループ_その他_値 + 1
でなければ:
    ループ_その他_値 = ループ_その他_値 + 10

# Starred unpacking variations
変数 a, *残り = [10, 20, 30, 40]
変数 *init, b = [10, 20, 30, 40]
変数 c, *中央, d = [10, 20, 30, 40]

# Set comprehension
変数 二乗_セット = {x * x 毎 x 中 範囲(5)}

# Extended builtins
変数 パワー_結果 = 累乗(2, 8)
変数 divmod_結果 = 商余り(17, 5)

# Yield from generator
関数 委任_生成器():
    生成 から 範囲(3)

変数 委任_済 = リスト(委任_生成器())

表示(要素_発見, ループ_その他_値)
表示(a, 残り, init, b, c, 中央, d)
表示(ソート済み(二乗_セット))
表示(パワー_結果, divmod_結果)
表示(委任_済)

# Numeric literals
変数 juurokushin_su = 0xFF
変数 hasshin_su = 0o17
変数 nishin_su = 0b1010
変数 kagaku_hyouki_su = 1.5e3

# Augmented assignments
変数 zoufuku_chi = 10
zoufuku_chi += 5
zoufuku_chi -= 2
zoufuku_chi *= 3
zoufuku_chi //= 4
zoufuku_chi %= 3

# Bitwise operators
変数 bitto_seki = 0b1010 & 0b1100
変数 bitto_wa = 0b1010 | 0b0101
変数 bitto_xor = 0b1010 ^ 0b1111
変数 hidari_shifuto = 1 << 3
変数 migi_shifuto = 64 >> 2

# Chained assignment
変数 rensa_kou = rensa_otsu = rensa_hei = 0

# Type annotations
変数 gata_tsuki_chi: int = 99

関数 chuushaku_kansuu(x: int, y: float) -> str:
    戻る str(x + y)

# Ternary expression
変数 sankou_chi = "yes" もし gata_tsuki_chi > 0 でなければ "no"

# Default params, *args, **kwargs
関数 fukusu_hiki_suu(base, extra=1, *args, **kwargs):
    戻る base + extra + sum(args)
変数 fukusu_kekka = fukusu_hiki_suu(10, 2, 3, 4, key=5)

# Lambda
変数 nijou_kansuu = ラムダ x: x * x

# List/dict comprehensions かつ generator expression
変数 risuto_naihou = [x * 2 毎 x 中 range(4)]
変数 jisho_naihou = {str(k): k * k 毎 k 中 range(3)}
変数 seisei_naihou = list(x + 1 毎 x 中 range(3))
変数 ireko_naihou = [i + j 毎 i 中 range(2) 毎 j 中 range(2)]
変数 shibori_naihou = [x 毎 x 中 range(6) もし x % 2 == 0]

# 試行/例外/でなければ
変数 shikou_soreigai = 0
試行:
    shikou_soreigai = int("7")
例外 ValueError:
    shikou_soreigai = -1
でなければ:
    shikou_soreigai += 1

# Exception chaining
変数 rensa_reigai = 偽
試行:
    試行:
        発生 ValueError("v")
    例外 ValueError として ve:
        発生 RuntimeError("r") から ve
例外 RuntimeError:
    rensa_reigai = 真

# Multiple 例外 handlers
変数 fukusu_reigai = 0
試行:
    発生 TypeError("t")
例外 ValueError:
    fukusu_reigai = 1
例外 TypeError:
    fukusu_reigai = 2

# Match/場合 付き 既定
変数 icchi_chi = 2
変数 icchi_kekka = "other"
照合 icchi_chi:
    場合 1:
        icchi_kekka = "one"
    場合 2:
        icchi_kekka = "two"
    既定:
        icchi_kekka = "既定"

# Decorator
関数 baika_ki(func):
    関数 tsutsumi(*args, **kwargs):
        戻る func(*args, **kwargs) * 2
    戻る tsutsumi

@baika_ki
関数 juu():
    戻る 10

変数 soushoku_kekka = juu()

# Multiple inheritance, static/クラス methods, property
クラス KongoClass:
    関数 kongo(self):
        戻る 1

クラス KiteiNi:
    関数 __init__(self, start):
        self.value = start

クラス KetsugoClass(KiteiNi, KongoClass):
    @staticmethod
    関数 raberu():
        戻る "combined"
    @classmethod
    関数 kochiku(cls, v):
        戻る cls(v)
    @property
    関数 baika_shosei(self):
        戻る self.value * 2

変数 ketsugo_obj = KetsugoClass.kochiku(3)
変数 shosei_chi = ketsugo_obj.baika_shosei

# Docstring
関数 bunsho_tsuki():
    """Has a docstring."""
    戻る 真

print(juurokushin_su, hasshin_su, nishin_su, kagaku_hyouki_su)
print(zoufuku_chi, bitto_seki, bitto_wa, bitto_xor, hidari_shifuto, migi_shifuto)
print(rensa_kou, rensa_otsu, rensa_hei)
print(gata_tsuki_chi, chuushaku_kansuu(3, 1.5), sankou_chi)
print(fukusu_kekka, nijou_kansuu(5))
print(risuto_naihou, jisho_naihou, seisei_naihou)
print(ireko_naihou, shibori_naihou)
print(shikou_soreigai, rensa_reigai, fukusu_reigai)
print(icchi_kekka, soushoku_kekka, shosei_chi)
print(bunsho_tsuki())
