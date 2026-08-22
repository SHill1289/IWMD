from pathlib import Path
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from breadthlab.storage import read_table
from breadthlab.backtest import run_rule_backtest
from breadthlab.glossary import tooltip

st.set_page_config(
    page_title="IWMD | Rule Research",
    page_icon="📈",
    layout="wide",
)

st.logo(
    str(ROOT / "assets" / "iwmd_logo.png"),
    size="large",
)

st.markdown(
    """
<div style="margin-bottom: 1.25rem;">
<div style="font-size: 0.85rem; opacity: 0.60; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.25rem;">
IWMD
</div>

<div style="font-size: 2.5rem; font-weight: 700; letter-spacing: -0.04em; margin-bottom: 0.35rem;">
Rule Research
</div>

<div style="font-size: 1.05rem; opacity: 0.72; max-width: 760px;">
Test whether specific breadth conditions historically improved the risk/reward of being invested in the market.
</div>
</div>
""",
    unsafe_allow_html=True,
)

df = read_table("daily_breadth")
if df.empty or "SPY" not in df.columns:
    st.error("Load data with benchmark history first.")
    st.stop()
df["date"] = pd.to_datetime(df["date"])

st.info(
    "This page does not predict the future. It asks a narrower research question: "
    "when these breadth conditions were present historically, how did a simple SPY strategy perform?"
)

min_score = st.slider(
    "Minimum Breadth Score to Stay Invested",
    0,
    100,
    60,
    help=(
        "The strategy stays invested only when the Breadth Score is at or above this level. "
        "Raising the threshold makes the rule more selective."
    ),
)
min_above = st.slider(
    "Minimum % of Stocks Above 200-DMA",
    0.0,
    1.0,
    0.50,
    0.05,
    format="%.0f%%",
    help=(
        "The strategy stays invested only when at least this share of S&P 500 stocks "
        "are above their 200-day moving average. Higher thresholds require broader "
        "long-term participation."
    ),
)
result, stats = run_rule_backtest(
    df,
    min_score=min_score,
    min_above_200=min_above,
)

metric_config = {
    "Annualized return": (
        "Annualized Return",
        "annualized_return",
        "percent",
    ),
    "Annualized volatility": (
        "Annualized Volatility",
        "annualized_volatility",
        "percent",
    ),
    "Sharpe (0% rf)": (
        "Sharpe Ratio",
        "sharpe",
        "number",
    ),
    "Maximum drawdown": (
        "Maximum Drawdown",
        "max_drawdown",
        "percent",
    ),
    "Time invested": (
        "Time Invested",
        "time_invested",
        "percent",
    ),
}

cols = st.columns(len(stats))

for col, (label, value) in zip(cols, stats.items()):
    display_label, help_key, format_type = metric_config.get(
        label,
        (label, "", "percent"),
    )

    if format_type == "number":
        display = f"{value:.2f}"
    else:
        display = f"{value:.1%}"

    col.metric(
        display_label,
        display,
        help=tooltip(help_key) if help_key else None,
    )

st.subheader("Strategy vs. Buy-and-Hold")

st.caption(
    "Shows how $1 would have grown under the breadth rule compared with staying invested in SPY."
)

st.plotly_chart(
    px.line(
        result,
        x="date",
        y=["strategy_equity", "buy_hold_equity"],
        title=None,
    ),
    use_container_width=True,
)

st.subheader("When the Rule Was Invested")

st.caption(
    "A value of 1 means the breadth conditions were met and the strategy held SPY. "
    "A value of 0 means the strategy moved to cash and did not hold SPY."
)

st.plotly_chart(
    px.area(
        result,
        x="date",
        y="signal",
        title=None,
    ),
    use_container_width=True,
)

st.warning(
    "Research caveat: Results are hypothetical and exclude fees, slippage, taxes, "
    "leverage, shorting costs, and point-in-time index membership. Use this as a "
    "research comparison, not as a prediction or trading recommendation."
)