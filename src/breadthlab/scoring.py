from __future__ import annotations
import numpy as np
import pandas as pd


def _clip01(series: pd.Series) -> pd.Series:
    return series.clip(0, 1)


def add_breadth_score(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    components = []
    for col in ["pct_above_20dma", "pct_above_50dma", "pct_above_200dma", "pct_advancing"]:
        if col in out:
            components.append(_clip01(out[col]))
    if "high_low_net" in out:
        scale = out["issues"].replace(0, np.nan)
        components.append(_clip01(0.5 + 2.5 * out["high_low_net"] / scale))
    if "rsp_spy_20d_change" in out:
        components.append(_clip01(0.5 + out["rsp_spy_20d_change"] * 10))
    if not components:
        raise ValueError("No breadth score components were available.")
    matrix = pd.concat(components, axis=1)
    out["breadth_score"] = matrix.mean(axis=1) * 100
    out["regime"] = pd.cut(
        out["breadth_score"],
        bins=[-np.inf, 35, 55, 70, np.inf],
        labels=["Bearish", "Fragile", "Bullish", "Strong bullish"],
    ).astype(str)
    out["score_change_5d"] = out["breadth_score"].diff(5)
    return out
