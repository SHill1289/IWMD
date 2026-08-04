from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
from typing import Iterable
import pandas as pd
import requests
import yfinance as yf

WIKI_SP500 = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

@dataclass(frozen=True)
class DownloadResult:
    prices: pd.DataFrame
    constituents: pd.DataFrame
    benchmark: pd.DataFrame


def get_sp500_constituents(timeout: int = 30) -> pd.DataFrame:
    headers = {"User-Agent": "MarketBreadthLab/0.1 research@example.invalid"}
    response = requests.get(WIKI_SP500, headers=headers, timeout=timeout)
    response.raise_for_status()
    tables = pd.read_html(StringIO(response.text))
    frame = tables[0].rename(columns={"Symbol": "symbol", "Security": "name", "GICS Sector": "sector"})
    frame["yf_symbol"] = frame["symbol"].str.replace(".", "-", regex=False)
    return frame[["symbol", "yf_symbol", "name", "sector"]].copy()


def _normalize_download(raw: pd.DataFrame, symbols: Iterable[str]) -> pd.DataFrame:
    if raw.empty:
        raise RuntimeError("No price data was returned by the provider.")
    symbols = list(symbols)
    if not isinstance(raw.columns, pd.MultiIndex):
        raw.columns = pd.MultiIndex.from_product([raw.columns, symbols[:1]])
    stacked = raw.stack(level=1, future_stack=True).reset_index()
    stacked = stacked.rename(
    columns={
        "Date": "date",
        "Ticker": "symbol",
        "ticker": "symbol",
        "level_1": "symbol",
    }
)
    rename = {c: c.lower().replace(" ", "_") for c in stacked.columns}
    stacked = stacked.rename(columns=rename)
    wanted = ["date", "symbol", "open", "high", "low", "close", "adj_close", "volume"]
    for col in wanted:
        if col not in stacked.columns:
            stacked[col] = pd.NA
    stacked["date"] = pd.to_datetime(stacked["date"]).dt.tz_localize(None)
    stacked = stacked.dropna(subset=["close"])
    return stacked[wanted].sort_values(["symbol", "date"]).reset_index(drop=True)


def download_market_data(start: str = "2015-01-01", end: str | None = None, batch_size: int = 80) -> DownloadResult:
    constituents = get_sp500_constituents()
    symbols = constituents["yf_symbol"].tolist()
    chunks: list[pd.DataFrame] = []
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i : i + batch_size]
        raw = yf.download(
            tickers=batch,
            start=start,
            end=end,
            auto_adjust=False,
            actions=False,
            progress=False,
            group_by="column",
            threads=True,
        )
        chunks.append(_normalize_download(raw, batch))
    prices = pd.concat(chunks, ignore_index=True)
    benchmark_symbols = ["SPY", "RSP", "QQQ", "IWM", "^VIX", "^TNX"]
    benchmark_raw = yf.download(
        tickers=benchmark_symbols,
        start=start,
        end=end,
        auto_adjust=False,
        actions=False,
        progress=False,
        group_by="column",
        threads=True,
    )
    benchmark = _normalize_download(benchmark_raw, benchmark_symbols)
    return DownloadResult(prices=prices, constituents=constituents, benchmark=benchmark)
