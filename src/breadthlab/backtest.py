from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors


def add_forward_returns(df: pd.DataFrame, price_col: str = "SPY", horizons=(5, 20, 60, 120)) -> pd.DataFrame:
    out = df.copy()
    for h in horizons:
        out[f"fwd_{h}d_return"] = out[price_col].shift(-h) / out[price_col] - 1
    return out


def similar_periods(
    df: pd.DataFrame,
    as_of: pd.Timestamp | None = None,
    features=("breadth_score", "pct_above_50dma", "pct_above_200dma", "high_low_net", "rsp_spy_20d_change"),
    n_neighbors: int = 12,
    exclusion_days: int = 40,
) -> pd.DataFrame:
    work = df.copy().sort_values("date")
    usable = [f for f in features if f in work.columns]
    work = work.dropna(subset=usable)
    if work.empty:
        return work
    target_idx = work.index[-1] if as_of is None else work.loc[work["date"] <= as_of].index[-1]
    target_date = work.loc[target_idx, "date"]
    candidates = work[(work["date"] < target_date - pd.Timedelta(days=exclusion_days))].copy()
    if len(candidates) < n_neighbors:
        n_neighbors = max(1, len(candidates))
    scaler = StandardScaler()
    x = scaler.fit_transform(candidates[usable])
    target = scaler.transform(work.loc[[target_idx], usable])
    model = NearestNeighbors(n_neighbors=n_neighbors)
    model.fit(x)
    distances, indices = model.kneighbors(target)
    result = candidates.iloc[indices[0]].copy()
    result["distance"] = distances[0]
    cols = ["date", "distance"] + usable + [c for c in result.columns if c.startswith("fwd_")]
    return result[cols].sort_values("distance")


def run_rule_backtest(df: pd.DataFrame, min_score: float = 60, min_above_200: float = 0.5) -> tuple[pd.DataFrame, dict]:
    work = df.sort_values("date").copy()
    work["signal"] = ((work["breadth_score"] >= min_score) & (work["pct_above_200dma"] >= min_above_200)).astype(int)
    work["strategy_return"] = work["signal"].shift(1).fillna(0) * work["spy_return"].fillna(0)
    work["buy_hold_equity"] = (1 + work["spy_return"].fillna(0)).cumprod()
    work["strategy_equity"] = (1 + work["strategy_return"]).cumprod()
    daily = work["strategy_return"].dropna()
    ann_return = work["strategy_equity"].iloc[-1] ** (252 / max(1, len(work))) - 1
    ann_vol = daily.std() * np.sqrt(252)
    drawdown = work["strategy_equity"] / work["strategy_equity"].cummax() - 1
    stats = {
        "Annualized return": ann_return,
        "Annualized volatility": ann_vol,
        "Sharpe (0% rf)": ann_return / ann_vol if ann_vol else np.nan,
        "Maximum drawdown": drawdown.min(),
        "Time invested": work["signal"].mean(),
    }
    return work, stats
