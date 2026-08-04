from pathlib import Path
import sys
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

st.set_page_config(page_title="Market Breadth Lab", page_icon="📈", layout="wide")

st.title("Market Breadth Lab")
st.caption("Local-first breadth monitoring, historical analogs, and signal research")

st.markdown(
    """
This MVP is designed around the market-internals workflow described in the Shoreline Capital reports:
advances and declines, new highs and lows, cumulative breadth, confirmation/divergence, and bull/bear regime context.

### Start here
1. Open **Data Manager** and load the included demo dataset or download live S&P 500 data.
2. Review **Dashboard** for the current breadth picture.
3. Use **Historical Analogs** and **Rule Backtest** for research.

### Data caveat
The free-data version reconstructs historical breadth using today's S&P 500 constituents. That creates survivorship bias. Treat it as a prototype and live-monitoring tool until a point-in-time constituent dataset is connected.
"""
)

st.info("No brokerage connection is included. The app reads market data and produces research outputs only.")
