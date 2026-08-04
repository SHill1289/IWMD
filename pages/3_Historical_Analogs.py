from pathlib import Path
import sys
import streamlit as st
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from breadthlab.storage import read_table
from breadthlab.backtest import add_forward_returns, similar_periods

st.title("Historical Analogs")
df = read_table("daily_breadth")
if df.empty or "SPY" not in df.columns:
    st.error("Load data with SPY benchmark history first.")
    st.stop()
df["date"] = pd.to_datetime(df["date"])
df = add_forward_returns(df)

n = st.slider("Number of analogs", 5, 30, 12)
result = similar_periods(df, n_neighbors=n)
st.dataframe(result, use_container_width=True, hide_index=True, column_config={c: st.column_config.NumberColumn(format="%.2f%%") for c in result.columns if c.startswith("fwd_")})

if not result.empty:
    st.subheader("Forward-return summary")
    summary = result[[c for c in result.columns if c.startswith("fwd_")]].agg(["mean", "median", "min", "max", "count"]).T
    st.dataframe(summary, use_container_width=True)

st.caption("Nearest neighbors use standardized breadth variables. Similarity is descriptive, not a forecast.")
