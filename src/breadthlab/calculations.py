from __future__ import annotations
import numpy as np
import pandas as pd


def calculate_security_features(prices: pd.DataFrame) -> pd.DataFrame:
    required = {"date", "symbol", "close"}
    missing = required - set(prices.columns)

    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df = prices.sort_values(["symbol", "date"]).copy()
    g = df.groupby("symbol", group_keys=False)

    df["prev_close"] = g["close"].shift(1)
    df["daily_return"] = df["close"] / df["prev_close"] - 1

    df["advance"] = (df["close"] > df["prev_close"]).astype("int8")
    df["decline"] = (df["close"] < df["prev_close"]).astype("int8")
    df["unchanged"] = (df["close"] == df["prev_close"]).astype("int8")

    for window in (20, 50, 200):
        ma = g["close"].transform(
            lambda s, w=window: s.rolling(w, min_periods=w).mean()
        )
        df[f"above_{window}dma"] = (
            df["close"] > ma
        ).where(ma.notna())

    rolling_high = g["close"].transform(
        lambda s: s.shift(1).rolling(252, min_periods=200).max()
    )

    rolling_low = g["close"].transform(
        lambda s: s.shift(1).rolling(252, min_periods=200).min()
    )

    df["new_52w_high"] = (
        df["close"] > rolling_high
    ).where(rolling_high.notna())

    df["new_52w_low"] = (
        df["close"] < rolling_low
    ).where(rolling_low.notna())

    return df


def calculate_daily_breadth(features: pd.DataFrame) -> pd.DataFrame:
    agg = features.groupby("date").agg(
        issues=("symbol", "nunique"),
        advances=("advance", "sum"),
        declines=("decline", "sum"),
        unchanged=("unchanged", "sum"),
        mean_return=("daily_return", "mean"),
        median_return=("daily_return", "median"),
        pct_above_20dma=("above_20dma", "mean"),
        pct_above_50dma=("above_50dma", "mean"),
        pct_above_200dma=("above_200dma", "mean"),
        new_52w_highs=("new_52w_high", "sum"),
        new_52w_lows=("new_52w_low", "sum"),
    ).reset_index()
    agg["ad_net"] = agg["advances"] - agg["declines"]
    agg["ad_ratio"] = agg["advances"] / agg["declines"].replace(0, np.nan)
    agg["ad_line"] = agg["ad_net"].cumsum()
    agg["high_low_net"] = agg["new_52w_highs"] - agg["new_52w_lows"]
    agg["high_low_line"] = agg["high_low_net"].cumsum()
    agg["pct_advancing"] = agg["advances"] / agg["issues"]
    agg["pct_declining"] = agg["declines"] / agg["issues"]
    return agg.sort_values("date").reset_index(drop=True)


def add_benchmark_features(breadth: pd.DataFrame, benchmark: pd.DataFrame) -> pd.DataFrame:
    piv = benchmark.pivot(index="date", columns="symbol", values="close").sort_index()
    out = breadth.set_index("date").join(piv, how="left")
    if {"RSP", "SPY"}.issubset(out.columns):
        out["rsp_spy_ratio"] = out["RSP"] / out["SPY"]
        out["rsp_spy_20d_change"] = out["rsp_spy_ratio"].pct_change(20)
    if "SPY" in out.columns:
        out["spy_return"] = out["SPY"].pct_change()
        out["spy_20dma"] = out["SPY"].rolling(20).mean()
        out["spy_50dma"] = out["SPY"].rolling(50).mean()
        out["spy_200dma"] = out["SPY"].rolling(200).mean()
    return out.reset_index()
