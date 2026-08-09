from pathlib import Path
import sys
import streamlit as st
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from breadthlab.storage import read_table, database_status

st.title("Data Quality")
st.json(database_status())
prices = read_table("prices")
features = read_table("security_features")
daily = read_table("daily_breadth")

if prices.empty:
    st.error("No data loaded.")
    st.stop()

prices["date"] = pd.to_datetime(prices["date"])
summary = pd.DataFrame({
    "metric": ["First date", "Last date", "Symbols", "Price rows", "Duplicate date-symbol rows", "Missing close values"],
    "value": [prices.date.min(), prices.date.max(), prices.symbol.nunique(), len(prices), prices.duplicated(["date", "symbol"]).sum(), prices.close.isna().sum()],
})
st.dataframe(summary, use_container_width=True, hide_index=True)

coverage = prices.groupby("date")["symbol"].nunique().reset_index(name="symbols_with_data")
st.line_chart(coverage.set_index("date"))

st.subheader("Known limitations")
st.markdown("""
- Historical breadth uses current S&P 500 membership.
- Free vendor data may contain missing observations, symbol changes, and provider corrections.
- Exchange-level up/down volume, TRIN, and official NYSE/Nasdaq breadth are not yet included.
- The score is a transparent prototype, not Shoreline Capital's proprietary Differential or trading model.
""")
