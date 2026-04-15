---
name: marimo
description: Marimo notebook guidelines for reactive Python notebooks. Enforces cell variable rules and import conventions.
---

# Marimo ノートブック運用規約

marimo はリアクティブな Python ノートブック。`.py` ファイルとして保存され、セル間の依存関係を自動追跡する。

## 必須ルール

### 1. ファイル構造

すべてのノートブックは以下の順序で構成する:

1. docstring（タイトル）
2. `# pyright: reportUndefinedVariable=false, reportMissingImports=false`
3. `import marimo` + `app = marimo.App(width="medium")`
4. `@app.cell` 定義（最初のセルに全 import を集約）
5. `if __name__ == "__main__": app.run()`

テンプレートは [実践例](./references/examples.md#最小構成テンプレート) を参照。

**PEP 723 inline メタデータ (`# /// script ... # ///`) は使用禁止**。marimo が検出すると sandbox モード (`uv run --isolated --no-project`) を提案するが、`--no-project` により workspace コンテキストが失われ `motion-skeleton` 等の `{ workspace = true }` 依存が解決できず起動失敗する。依存は workspace 全体の `pyproject.toml` で管理し、`uv sync` 済み venv で `uv run marimo edit ...` を起動する運用に統一する。

### 2. セル規約

- `@app.cell` デコレータ + 依存変数を引数で受け取る
- 公開する変数は `return (var1, var2)` タプルで返す
- 公開不要の変数は `_` プレフィックス

### 3. アンチパターン（禁止事項）

#### NG: 異なるセルで同じ変数名を使い回す

**これは最も頻発するエラーである。絶対に行ってはならない。**

同じ変数名が複数セルで定義されると `MultipleDefinitionError` が発生する。`fig`, `df`, `result`, `chart` 等の汎用名で特に起きやすい。

回避策: セルごとにユニークな名前（`fig_knee`, `fig_cog`）にするか、`_` プレフィックスでローカルにする。

NG/OK 対比例は [実践例](./references/examples.md#アンチパターン対比) を参照。

#### NG: 途中のセルで import する

**ライブラリの import は最初のセルにすべて集約する。** 2番目以降のセルで `import` を書いてはならない。

### 4. データパス

プロジェクトルートからの相対パスを使用（`uv run marimo edit` でルートから起動するため）。絶対パスや `..` は使わない。

## リファレンス

- [コマンド・API リファレンス](./references/commands.md) — CLI コマンド、UI コンポーネント、レイアウト
- [実践例](./references/examples.md) — テンプレート、アンチパターン対比、インタラクティブ UI 例

