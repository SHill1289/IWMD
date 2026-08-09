from pathlib import Path
import sys
import streamlit as st
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from breadthlab.storage import read_table
from breadthlab.backtest import add_forward_returns, similar_periods
from breadthlab.glossary import tooltip

st.markdown(
    """
<div style="margin-bottom: 1.25rem;">
<div style="font-size: 0.85rem; opacity: 0.60; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.25rem;">
IWMD
</div>

<div style="font-size: 2.5rem; font-weight: 700; letter-spacing: -0.04em; margin-bottom: 0.35rem;">
Historical Analogs
</div>

<div style="font-size: 1.05rem; opacity: 0.72; max-width: 760px;">
When the market looked like this before, what tended to happen next?
</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
    Historical Analogs looks for past market environments that most closely
    resemble the selected date based on market breadth and participation.

    The goal is not to predict the future. It is to answer a simpler question:
    **When the market looked like this before, what tended to happen next?**
    """
)

st.info(
    "A smaller **Distance** means the historical market environment was more similar "
    "to the selected date. Forward returns show what SPY did after that historical "
    "date over 5, 20, 60, and 120 trading days."
)

df = read_table("daily_breadth")
if df.empty or "SPY" not in df.columns:
    st.error("Load data with SPY benchmark history first.")
    st.stop()
df["date"] = pd.to_datetime(df["date"])
df = add_forward_returns(df)

n = st.slider(
    "Number of analogs",
    5,
    30,
    12,
    help=tooltip("number_of_analogs"),
)
result = similar_periods(df, n_neighbors=n)

st.caption(
    "Distance measures similarity. Lower values mean the historical period "
    "looked more like the current market environment."
)

st.dataframe(result, use_container_width=True, hide_index=True, column_config={c: st.column_config.NumberColumn(format="%.2f%%") for c in result.columns if c.startswith("fwd_")})

if not result.empty:
    st.subheader("Forward-return summary")

    st.caption(
        "These figures summarize what SPY did after the similar historical periods. "
        "The 5-, 20-, 60-, and 120-day horizons are approximately one week, one month, "
        "three months, and six months of trading."
    )

    summary = result[
        [c for c in result.columns if c.startswith("fwd_")]
    ].agg(["mean", "median", "min", "max", "count"]).T

    summary = summary.rename(
        index={
    "fwd_5d_return": "5-Day Forward Return",
    "fwd_20d_return": "20-Day Forward Return",
    "fwd_60d_return": "60-Day Forward Return",
    "fwd_120d_return": "120-Day Forward Return",
},
        columns={
            "mean": "Average",
            "median": "Median",
            "min": "Worst",
            "max": "Best",
            "count": "Sample Size",
        },
    )

    st.dataframe(
        summary,
        use_container_width=True,
    )

st.caption("Nearest neighbors use standardized breadth variables. Similarity is descriptive, not a forecast.")

st.markdown("---")

st.caption(
    "IWMD Historical Analogs is a research tool for comparing current market breadth "
    "conditions with similar historical periods. Similarity does not imply that future "
    "market behavior will repeat."
)