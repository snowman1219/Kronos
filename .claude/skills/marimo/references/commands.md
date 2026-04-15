# Marimo コマンドリファレンス

> notebook に PEP 723 inline メタデータを含めない運用のため、`uv run marimo edit` は sandbox モードを提案せず、`uv sync` 済みの project venv でそのまま起動する。workspace パッケージもそのまま解決される。

## CLI コマンド

### uv run marimo edit — ノートブック編集

ブラウザで marimo エディタを開く。

```bash
# 既存ノートブックを編集
uv run marimo edit notebooks/exp001/01_analysis.py

# ポート指定
uv run marimo edit notebooks/exp001/01_analysis.py --port 8080

# ホスト指定（外部アクセス許可）
uv run marimo edit notebooks/exp001/01_analysis.py --host 0.0.0.0
```

### uv run marimo run — スクリプト実行

ノートブックをアプリとしてブラウザで実行（編集不可）。

```bash
uv run marimo run notebooks/exp001/01_analysis.py
```

### uv run marimo new — 新規作成

新しいノートブックファイルを作成。

```bash
uv run marimo new notebooks/exp002/01_new_analysis.py
```

### uv run marimo export — エクスポート

```bash
# HTML にエクスポート
uv run marimo export html notebooks/exp001/01_analysis.py -o output.html

# ipynb にエクスポート
uv run marimo export ipynb notebooks/exp001/01_analysis.py -o output.ipynb

# Markdown にエクスポート
uv run marimo export md notebooks/exp001/01_analysis.py -o output.md
```

### uv run marimo convert — 変換

Jupyter ノートブックを marimo に変換。

```bash
uv run marimo convert notebook.ipynb -o notebook.py
```

## 主要 API

### marimo as mo

#### Markdown 表示

```python
# 基本
mo.md("# タイトル")

# f-string で変数埋め込み
mo.md(f"データ件数: **{len(df)}** 行")

# 複数行
mo.md("""
# セクション見出し

- 項目1
- 項目2

| 列A | 列B |
|-----|-----|
| 1   | 2   |
""")
```

#### UI コンポーネント

```python
# ドロップダウン
dropdown = mo.ui.dropdown(
    options=["option_a", "option_b", "option_c"],
    value="option_a",
    label="選択してください",
)

# スライダー
slider = mo.ui.slider(start=0, stop=100, step=1, value=50, label="閾値")

# チェックボックス
checkbox = mo.ui.checkbox(value=True, label="フィルタ有効")

# テキスト入力
text = mo.ui.text(value="default", label="入力")

# 数値入力
number = mo.ui.number(start=0, stop=100, step=0.1, value=50.0, label="値")

# ラジオボタン
radio = mo.ui.radio(
    options=["A", "B", "C"],
    value="A",
    label="モード選択",
)

# マルチセレクト
multiselect = mo.ui.multiselect(
    options=["feat1", "feat2", "feat3"],
    label="特徴量選択",
)

# ファイルブラウザ
file_browser = mo.ui.file_browser(
    initial_path="data/",
    filetypes=[".csv", ".json"],
)

# テーブル（データフレーム表示 + 行選択）
table = mo.ui.table(df, selection="multi")
```

#### 可視化

```python
# Plotly グラフ表示
mo.ui.plotly(fig)

# matplotlib グラフ表示
mo.ui.matplotlib(fig)

# Altair グラフ表示
mo.ui.altair(chart)
```

#### レイアウト

```python
# 水平配置
mo.hstack([element1, element2, element3])

# 垂直配置
mo.vstack([element1, element2])

# タブ
mo.ui.tabs({
    "タブ1": content1,
    "タブ2": content2,
})

# アコーディオン
mo.ui.accordion({
    "セクション1": content1,
    "セクション2": content2,
})

# 条件付き表示
mo.stop(not condition, mo.md("条件を満たしていません"))
```

#### 状態管理

```python
# UI 値の取得（他セルで参照）
selected = dropdown.value    # 選択された値
slider_val = slider.value    # スライダーの値
checked = checkbox.value     # True/False

# バッチ更新
mo.ui.batch(
    name=mo.ui.text(label="名前"),
    age=mo.ui.number(start=0, stop=120, label="年齢"),
)
```

