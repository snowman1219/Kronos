# Marimo 実践例

> **注意**: PEP 723 inline メタデータ (`# /// script ... # ///`) は禁止。marimo の sandbox モードは uv workspace を解決できず起動失敗するため、依存はすべて workspace の `pyproject.toml` で管理する。

## 基本ノートブックの作成

### 最小構成テンプレート

```python
"""分析タイトル"""

# pyright: reportUndefinedVariable=false, reportMissingImports=false

import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    from pathlib import Path

    return (Path, mo, pd, px)


@app.cell
def _(mo):
    mo.md("""
    # 分析タイトル

    分析の目的と概要を記述。
    """)
    return


@app.cell
def _(Path, pd, mo):
    _path = Path("data/example.csv")
    df = pd.read_csv(_path)
    mo.md(f"データ: **{len(df)}** 行 x **{len(df.columns)}** 列")
    return (df,)


@app.cell
def _(df, px, mo):
    fig_distribution = px.histogram(df, x="value", title="分布")
    mo.ui.plotly(fig_distribution)
    return (fig_distribution,)


if __name__ == "__main__":
    app.run()
```

## アンチパターン対比

### NG: 同じ変数名の複数セル定義

marimo のリアクティブグラフでは、1つの変数は1つのセルでのみ定義できる。

```python
# ❌ NG — `result` が2つのセルで定義されている → MultipleDefinitionError
@app.cell
def _(pd):
    result = pd.read_csv("data/train.csv")
    return (result,)

@app.cell
def _(pd):
    result = pd.read_csv("data/test.csv")
    return (result,)
```

```python
# ✅ OK（方法1） — ユニークな変数名を使う
@app.cell
def _(pd):
    train_df = pd.read_csv("data/train.csv")
    return (train_df,)

@app.cell
def _(pd):
    test_df = pd.read_csv("data/test.csv")
    return (test_df,)
```

```python
# ✅ OK（方法2） — 公開不要なら _ プレフィックス（return しない）
@app.cell
def _(pd, mo):
    _result = pd.read_csv("data/train.csv")
    mo.md(f"訓練データ: {len(_result)} 行")
    return

@app.cell
def _(pd, mo):
    _result = pd.read_csv("data/test.csv")
    mo.md(f"テストデータ: {len(_result)} 行")
    return
```

### NG: 途中セルでの import

```python
# ❌ NG — セル2で新たに import している
@app.cell
def _():
    import marimo as mo
    return (mo,)

@app.cell
def _(mo):
    import numpy as np          # NG!
    from sklearn import metrics  # NG!
    _scores = np.array([0.9, 0.8, 0.7])
    mo.md(f"平均: {np.mean(_scores):.2f}")
    return
```

```python
# ✅ OK — 全 import を最初のセルに集約
@app.cell
def _():
    import marimo as mo
    import numpy as np
    from sklearn import metrics
    return (metrics, mo, np)

@app.cell
def _(mo, np):
    _scores = np.array([0.9, 0.8, 0.7])
    mo.md(f"平均: {np.mean(_scores):.2f}")
    return
```

### NG: 変数名の衝突（よくあるパターン）

```python
# ❌ NG — fig, df, result, chart などの汎用名を複数セルで使用
@app.cell
def _(px, df, mo):
    fig = px.box(df, y="feature_a")
    mo.ui.plotly(fig)
    return (fig,)

@app.cell
def _(px, df, mo):
    fig = px.box(df, y="feature_b")  # MultipleDefinitionError!
    mo.ui.plotly(fig)
    return (fig,)
```

```python
# ✅ OK — 内容を反映した命名
@app.cell
def _(px, df, mo):
    fig_feature_a = px.box(df, y="feature_a")
    mo.ui.plotly(fig_feature_a)
    return (fig_feature_a,)

@app.cell
def _(px, df, mo):
    fig_feature_b = px.box(df, y="feature_b")
    mo.ui.plotly(fig_feature_b)
    return (fig_feature_b,)
```

## Workspace パッケージの参照

`uv sync` 済みの venv から `uv run marimo edit ...` で起動するため、workspace 内の自作パッケージ (`motion_skeleton`, `motion_features` 等) はそのまま import できる。PEP 723 の `[tool.uv.sources]` や `dependencies` 宣言は不要:

```python
"""Workspace パッケージ利用例"""

# pyright: reportUndefinedVariable=false, reportMissingImports=false

import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    from pathlib import Path
    from motion_skeleton.config import ActionLabel
    from motion_skeleton.extraction import extract_skeleton
    from motion_features.extraction import extract_features

    return (ActionLabel, Path, extract_features, extract_skeleton, mo, pd, px)


if __name__ == "__main__":
    app.run()
```

## インタラクティブ UI の活用

### ドロップダウンでデータ切り替え

```python
@app.cell
def _(mo):
    video_selector = mo.ui.dropdown(
        options=["video01", "video02", "video03"],
        value="video01",
        label="動画選択",
    )
    video_selector
    return (video_selector,)


@app.cell
def _(video_selector, pd, Path, mo):
    _path = Path(f"outputs/predictions/{video_selector.value}.json")
    if _path.exists():
        prediction = pd.read_json(_path)
        mo.md(f"予測結果: **{len(prediction)}** セグメント")
    else:
        prediction = pd.DataFrame()
        mo.md("ファイルが見つかりません")
    return (prediction,)
```

### スライダーで閾値調整

```python
@app.cell
def _(mo):
    threshold_slider = mo.ui.slider(
        start=0.0, stop=180.0, step=1.0, value=130.0,
        label="膝角度閾値 (度)",
    )
    threshold_slider
    return (threshold_slider,)


@app.cell
def _(threshold_slider, df, mo):
    _filtered = df[df["knee_angle"] < threshold_slider.value]
    mo.md(f"閾値 {threshold_slider.value}° 以下: **{len(_filtered)}** フレーム ({len(_filtered)/len(df)*100:.1f}%)")
    return
```

### タブで複数ビューを整理

```python
@app.cell
def _(mo, fig_histogram, fig_scatter, fig_box):
    mo.ui.tabs({
        "分布": mo.ui.plotly(fig_histogram),
        "散布図": mo.ui.plotly(fig_scatter),
        "箱ひげ図": mo.ui.plotly(fig_box),
    })
    return
```

