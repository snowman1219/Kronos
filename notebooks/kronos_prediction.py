"""Kronos 動作確認 — 予測と可視化"""

# pyright: reportUndefinedVariable=false, reportMissingImports=false

import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import time as time_mod
    import torch
    import plotly.graph_objects as go
    from pathlib import Path
    from model import Kronos, KronosTokenizer, KronosPredictor

    return (
        Kronos,
        KronosPredictor,
        KronosTokenizer,
        Path,
        go,
        mo,
        pd,
        time_mod,
        torch,
    )


@app.cell
def _(mo):
    mo.md("""
    # Kronos 動作確認

    `NeoQuasar/Kronos-base` を使って5分足データの予測を行い、Ground Truth と比較する。

    - **トークナイザー**: `NeoQuasar/Kronos-Tokenizer-base`
    - **モデル**: `NeoQuasar/Kronos-base` (102.3M params)
    - **入力**: `tests/data/regression_input.csv` (5分足 OHLCV, 2500行)
    - **lookback**: 400, **pred_len**: 120
    """)
    return


@app.cell
def _(mo, torch):
    if torch.cuda.is_available():
        _name = torch.cuda.get_device_name(0)
        _mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
        device = "cuda:0"
        mo.md(f"**GPU 検出**: {_name} ({_mem:.1f} GB)")
    else:
        device = "cpu"
        mo.callout(mo.md("**GPU が見つかりません。CPU で実行します。**"), kind="warn")
    return (device,)


@app.cell
def _(Kronos, KronosPredictor, KronosTokenizer, device, mo):
    _tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
    _kronos_model = Kronos.from_pretrained("NeoQuasar/Kronos-base")
    predictor = KronosPredictor(_kronos_model, _tokenizer, device=device, max_context=512)
    mo.md("**モデル読み込み完了**")
    return (predictor,)


@app.cell
def _(Path, mo, pd):
    _raw = pd.read_csv(Path("tests/data/regression_input.csv"))
    _raw["timestamps"] = pd.to_datetime(_raw["timestamps"])

    _lookback = 400
    _pred_len = 120
    _start = len(_raw) - _lookback - _pred_len

    x_df = _raw.loc[_start:_start + _lookback - 1, ["open", "high", "low", "close", "volume", "amount"]].reset_index(drop=True)
    x_timestamps = _raw.loc[_start:_start + _lookback - 1, "timestamps"].reset_index(drop=True)
    y_timestamps = _raw.loc[_start + _lookback:_start + _lookback + _pred_len - 1, "timestamps"].reset_index(drop=True)
    gt_df = _raw.loc[_start + _lookback:_start + _lookback + _pred_len - 1, ["open", "high", "low", "close", "volume", "amount"]].reset_index(drop=True)
    context_df = _raw.loc[_start:_start + _lookback - 1, ["open", "high", "low", "close", "timestamps"]].reset_index(drop=True)
    pred_len = _pred_len

    mo.md(f"""
    **データ分割**

    | 区間 | 行数 | 期間 |
    |---|---|---|
    | Context (lookback) | {len(x_df)} | {x_timestamps.iloc[0]} ~ {x_timestamps.iloc[-1]} |
    | Prediction | {_pred_len} | {y_timestamps.iloc[0]} ~ {y_timestamps.iloc[-1]} |
    """)
    return context_df, gt_df, pred_len, x_df, x_timestamps, y_timestamps


@app.cell
def _(mo, pred_len, predictor, time_mod, x_df, x_timestamps, y_timestamps):
    _t0 = time_mod.time()
    pred_df = predictor.predict(
        df=x_df,
        x_timestamp=x_timestamps,
        y_timestamp=y_timestamps,
        pred_len=pred_len,
        T=1.0,
        top_p=0.9,
        sample_count=1,
    )
    _elapsed = time_mod.time() - _t0
    mo.md(f"**予測完了** — {_elapsed:.1f} 秒")
    return (pred_df,)


@app.cell
def _(context_df, go, gt_df, mo, pred_df, y_timestamps):
    fig_price = go.Figure()

    # Context (lookback) のローソク足
    fig_price.add_trace(go.Candlestick(
        x=context_df["timestamps"],
        open=context_df["open"],
        high=context_df["high"],
        low=context_df["low"],
        close=context_df["close"],
        name="Context",
        increasing_line_color="steelblue",
        decreasing_line_color="lightblue",
    ))

    # Ground Truth のローソク足
    fig_price.add_trace(go.Candlestick(
        x=y_timestamps,
        open=gt_df["open"],
        high=gt_df["high"],
        low=gt_df["low"],
        close=gt_df["close"],
        name="Ground Truth",
        increasing_line_color="green",
        decreasing_line_color="darkgreen",
    ))

    # Prediction のローソク足
    fig_price.add_trace(go.Candlestick(
        x=y_timestamps,
        open=pred_df["open"],
        high=pred_df["high"],
        low=pred_df["low"],
        close=pred_df["close"],
        name="Prediction",
        increasing_line_color="orangered",
        decreasing_line_color="salmon",
    ))

    fig_price.update_layout(
        title="Price — Ground Truth vs Prediction",
        xaxis_title="Timestamp",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        height=500,
    )

    mo.ui.plotly(fig_price)
    return


@app.cell
def _(go, gt_df, mo, pred_df, y_timestamps):
    fig_volume = go.Figure()

    fig_volume.add_trace(go.Bar(
        x=y_timestamps,
        y=gt_df["volume"],
        name="Ground Truth",
        marker_color="steelblue",
        opacity=0.7,
    ))

    fig_volume.add_trace(go.Bar(
        x=y_timestamps,
        y=pred_df["volume"],
        name="Prediction",
        marker_color="orangered",
        opacity=0.7,
    ))

    fig_volume.update_layout(
        title="Volume — Ground Truth vs Prediction",
        xaxis_title="Timestamp",
        yaxis_title="Volume",
        barmode="group",
        height=400,
    )

    mo.ui.plotly(fig_volume)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
