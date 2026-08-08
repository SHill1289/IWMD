from pathlib import Path
import sys
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from breadthlab.storage import read_table
from breadthlab.glossary import tooltip

st.title("Breadth Dashboard")
df = read_table("daily_breadth")
if df.empty:
    st.error("Load data from Data Manager first.")
    st.stop()

df["date"] = __import__("pandas").to_datetime(df["date"])
latest = df.dropna(subset=["breadth_score"]).iloc[-1]
prev = df.dropna(subset=["breadth_score"]).iloc[-2]

cols = st.columns(5)

cols[0].metric(
    "Breadth Score",
    f"{latest.breadth_score:.1f}",
    f"{latest.breadth_score - prev.breadth_score:+.1f}",
    help=tooltip("breadth_score"),
)

cols[1].metric(
    "Regime",
    latest.regime,
    help=tooltip("regime"),
)

cols[2].metric(
    "Above 50-DMA",
    f"{latest.pct_above_50dma:.0%}",
    help=tooltip("above_50dma"),
)

cols[3].metric(
    "Above 200-DMA",
    f"{latest.pct_above_200dma:.0%}",
    help=tooltip("above_200dma"),
)

cols[4].metric(
    "52-week H-L",
    f"{int(latest.high_low_net):+d}",
    help=tooltip("high_low_net"),
)

st.subheader(
    "Breadth Score History",
    help=tooltip("breadth_score"),
)

st.plotly_chart(
    px.line(
        df,
        x="date",
        y="breadth_score",
        title=None,
    ),
    use_container_width=True,
)


left, right = st.columns(2)

with left:
    st.subheader(
        "Moving-Average Participation",
        help=tooltip("moving_average_participation"),
    )

    st.plotly_chart(
        px.line(
            df,
            x="date",
            y=[
                "pct_above_20dma",
                "pct_above_50dma",
                "pct_above_200dma",
            ],
            title=None,
        ),
        use_container_width=True,
    )

    st.subheader(
        "Cumulative Advance-Decline Line",
        help=tooltip("cumulative_ad_line"),
    )

    st.plotly_chart(
        px.line(
            df,
            x="date",
            y="ad_line",
            title=None,
        ),
        use_container_width=True,
    )


with right:
    if "SPY" in df.columns:
        st.subheader(
            "SPY vs. RSP",
            help=tooltip("spy_vs_rsp"),
        )

        st.plotly_chart(
            px.line(
                df,
                x="date",
                y=["SPY", "RSP"],
                title=None,
            ),
            use_container_width=True,
        )

    st.subheader(
        "52-Week Highs and Lows",
        help=tooltip("52_week_highs_lows"),
    )

    st.plotly_chart(
        px.bar(
            df.tail(120),
            x="date",
            y=["new_52w_highs", "new_52w_lows"],
            barmode="group",
            title=None,
        ),
        use_container_width=True,
    )


st.subheader(
    "Latest Reading",
    help=tooltip("latest_reading"),
)

st.dataframe(
    df.tail(20).sort_values("date", ascending=False),
    use_container_width=True,
    hide_index=True,
)