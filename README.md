# Market Breadth Lab

A private, local-first market breadth research dashboard built with Python, Streamlit, and DuckDB.

## What the MVP does

- Downloads current S&P 500 constituent history using Yahoo Finance via `yfinance`
- Calculates daily advances, declines, unchanged issues, A/D net and cumulative A/D line
- Calculates new 52-week highs and lows
- Calculates the percentage of stocks above 20-, 50-, and 200-day moving averages
- Compares equal-weight and capitalization-weight proxies using RSP and SPY
- Produces a normalized breadth score and a simple bullish/neutral/bearish regime
- Finds historically similar breadth conditions
- Backtests rule combinations against forward SPY returns
- Stores calculated data in a portable DuckDB database
- Includes a deterministic demo dataset so the interface can be reviewed before downloading live data

## Important limitation

The free-data build uses the **current** S&P 500 membership for historical calculations. This introduces survivorship bias. It is useful for prototyping and live monitoring, but it is not appropriate for institutional claims about multi-decade historical performance. The provider layer is isolated so point-in-time constituents and licensed price history can be added later.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app starts in demo mode. Use **Data Manager** to download live data.

## Project structure

- `app.py`: app entry point
- `pages/`: dashboard and research screens
- `src/breadthlab/`: data providers, calculations, storage, scoring, backtesting
- `data/`: local DuckDB database and exports
- `tests/`: calculation tests

## Recommended production upgrades

1. Replace current-membership history with point-in-time constituent data.
2. Add delisted securities and corporate-action-complete history.
3. Add licensed NYSE/Nasdaq issue-level advances, declines, and volume.
4. Add model versioning, authentication, and an audit log.
5. Schedule the refresh after the market close using cron, Task Scheduler, or a cloud job.

## Disclaimer

This software is a research tool, not investment advice. Validate every signal, data source, and calculation before using it in trading or client communications.
