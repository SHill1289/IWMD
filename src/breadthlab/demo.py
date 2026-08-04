from __future__ import annotations
import numpy as np
import pandas as pd
from .calculations import calculate_security_features, calculate_daily_breadth, add_benchmark_features
from .scoring import add_breadth_score


def make_demo(seed: int = 42, n_symbols: int = 120, periods: int = 900):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=periods)
    market = rng.normal(0.00035, 0.009, periods)
    rows = []
    for i in range(n_symbols):
        beta = rng.normal(1.0, 0.2)
        idio = rng.normal(0, 0.012, periods)
        rets = beta * market + idio
        close = 50 * np.exp(np.cumsum(rets))
        rows.append(pd.DataFrame({"date": dates, "symbol": f"DEMO{i:03d}", "close": close, "open": close, "high": close*1.005, "low": close*0.995, "adj_close": close, "volume": rng.integers(100000, 3000000, periods)}))
    prices = pd.concat(rows, ignore_index=True)
    spy = 400 * np.exp(np.cumsum(market))
    rsp = 150 * np.exp(np.cumsum(market + rng.normal(0, 0.0025, periods)))
    benchmark = pd.concat([
        pd.DataFrame({"date": dates, "symbol": "SPY", "close": spy}),
        pd.DataFrame({"date": dates, "symbol": "RSP", "close": rsp}),
    ], ignore_index=True)
    for col in ["open", "high", "low", "adj_close"]:
        benchmark[col] = benchmark["close"]
    benchmark["volume"] = 1_000_000
    constituents = pd.DataFrame({"symbol": [f"DEMO{i:03d}" for i in range(n_symbols)], "yf_symbol": [f"DEMO{i:03d}" for i in range(n_symbols)], "name": "Demo security", "sector": "Demo"})
    features = calculate_security_features(prices)
    daily = add_benchmark_features(calculate_daily_breadth(features), benchmark)
    daily = add_breadth_score(daily)
    return prices, constituents, benchmark, features, daily
