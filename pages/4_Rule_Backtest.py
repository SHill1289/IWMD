from pathlib import Path
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from breadthlab.storage import read_table
from breadthlab.backtest import run_rule_backtest

st.title("Rule Backtest")
df = read_table("daily_breadth")
if df.empty or "SPY" not in df.columns:
    st.error("Load data with benchmark history first.")
    st.stop()
df["date"] = pd.to_datetime(df["date"])

min_score = st.slider("Minimum breadth score", 0, 100, 60)
min_above = st.slider("Minimum fraction above 200-DMA", 0.0, 1.0, 0.50, 0.05)
result, stats = run_rule_backtest(df, min_score=min_score, min_above_200=min_above)

cols = st.columns(len(stats))
for col, (label, value) in zip(cols, stats.items()):
    display = f"{value:.2f}" if "Sharpe" in label else f"{value:.1%}"
    col.metric(label, display)

st.plotly_chart(px.line(result, x="date", y=["strategy_equity", "buy_hold_equity"], title="Growth of $1"), use_container_width=True)
st.plotly_chart(px.area(result, x="date", y="signal", title="Invested regime"), use_container_width=True)
st.warning("This simplified backtest excludes fees, slippage, taxes, leverage, shorting costs, and point-in-time membership. Do not treat it as a production result.")
