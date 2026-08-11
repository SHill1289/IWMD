from pathlib import Path
import sys
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from breadthlab.storage import read_table
from breadthlab.glossary import tooltip

st.markdown(
    """
    <style>
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 14px;
            padding: 16px 18px;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.85rem;
            opacity: 0.72;
        }

        [data-testid="stMetricValue"] {
            font-weight: 650;
            letter-spacing: -0.02em;
        }

        [data-testid="stMetricDelta"] {
            font-size: 0.85rem;
        }

        .iwmd-section-rule {
            height: 1px;
            background: rgba(128, 128, 128, 0.20);
            margin: 1.2rem 0 1.5rem 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
<div style="margin-bottom: 1.25rem;">
<div style="font-size: 0.85rem; opacity: 0.60; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.25rem;">
IWMD
</div>

<div style="font-size: 2.5rem; font-weight: 700; letter-spacing: -0.04em; margin-bottom: 0.35rem;">
Market Dashboard
</div>

<div style="font-size: 1.05rem; opacity: 0.72; max-width: 760px;">
Breadth tells us how many stocks are actually participating in the market's move.
</div>
</div>
""",
    unsafe_allow_html=True,
)

df = read_table("daily_breadth")
if df.empty:
    st.error("Load data from Data Manager first.")
    st.stop()

df["date"] = __import__("pandas").to_datetime(df["date"])
latest = df.dropna(subset=["breadth_score"]).iloc[-1]
prev = df.dropna(subset=["breadth_score"]).iloc[-2]

row1 = st.columns(3)
row2 = st.columns(2)

row1[0].metric(
    "Breadth Score",
    f"{latest.breadth_score:.1f}",
    f"{latest.breadth_score - prev.breadth_score:+.1f}",
    help=tooltip("breadth_score"),
)

row1[1].metric(
    "Regime",
    latest.regime,
    help=tooltip("regime"),
)

row1[2].metric(
    "Above 50-DMA",
    f"{latest.pct_above_50dma:.0%}",
    help=tooltip("above_50dma"),
)

row2[0].metric(
    "Above 200-DMA",
    f"{latest.pct_above_200dma:.0%}",
    help=tooltip("above_200dma"),
)

row2[1].metric(
    "52-week H-L",
    f"{int(latest.high_low_net):+d}",
    help=tooltip("high_low_net"),
)

st.markdown(
    '<div class="iwmd-section-rule"></div>',
    unsafe_allow_html=True,
)

last_updated = df["date"].max()

st.caption(
    f"Data last updated: {last_updated:%B %d, %Y}"
)

st.subheader("Market Internals Summary")

summary_parts = []

# Overall breadth regime
summary_parts.append(
    f"Overall breadth is currently **{str(latest.regime).lower()}** "
    f"with a Breadth Score of **{latest.breadth_score:.1f}**."
)

# Participation
if latest.pct_above_50dma >= 0.70 and latest.pct_above_200dma >= 0.60:
    participation_text = (
        "Participation is broad, with a large majority of stocks above "
        "their medium- and long-term moving averages."
    )
elif latest.pct_above_50dma >= 0.50:
    participation_text = (
        "Participation is mixed. A reasonable number of stocks are healthy, "
        "but strength is not especially broad."
    )
else:
    participation_text = (
        "Participation is weak, with fewer stocks holding above their "
        "medium-term trend."
    )

summary_parts.append(participation_text)

# New highs vs lows
if latest.high_low_net > 0:
    highs_lows_text = (
        f"New 52-week highs exceed new lows by **{int(latest.high_low_net)}**, "
        "which is a positive sign for underlying market strength."
    )
elif latest.high_low_net < 0:
    highs_lows_text = (
        f"New 52-week lows exceed new highs by **{abs(int(latest.high_low_net))}**, "
        "which is a warning sign beneath the headline index."
    )
else:
    highs_lows_text = (
        "New 52-week highs and lows are roughly balanced."
    )

summary_parts.append(highs_lows_text)

st.info(" ".join(summary_parts))

st.subheader("What Changed Today?")

breadth_change = latest.breadth_score - prev.breadth_score
above_50_change = latest.pct_above_50dma - prev.pct_above_50dma
above_200_change = latest.pct_above_200dma - prev.pct_above_200dma
high_low_change = latest.high_low_net - prev.high_low_net

change_parts = []

# Breadth Score
if breadth_change > 1:
    change_parts.append(
        f"Breadth improved by **{breadth_change:+.1f} points**."
    )
elif breadth_change < -1:
    change_parts.append(
        f"Breadth weakened by **{breadth_change:+.1f} points**."
    )
else:
    change_parts.append(
        f"Breadth was relatively stable at **{breadth_change:+.1f} points**."
    )

# 50-DMA participation
if above_50_change > 0.02:
    change_parts.append(
        f"Participation above the 50-day moving average increased by "
        f"**{above_50_change:+.1%}**."
    )
elif above_50_change < -0.02:
    change_parts.append(
        f"Participation above the 50-day moving average decreased by "
        f"**{above_50_change:+.1%}**."
    )

# 200-DMA participation
if above_200_change > 0.01:
    change_parts.append(
        f"Long-term participation improved by **{above_200_change:+.1%}**."
    )
elif above_200_change < -0.01:
    change_parts.append(
        f"Long-term participation weakened by **{above_200_change:+.1%}**."
    )

# Highs vs lows
if high_low_change > 10:
    change_parts.append(
        "The balance of new 52-week highs versus lows improved meaningfully."
    )
elif high_low_change < -10:
    change_parts.append(
        "The balance of new 52-week highs versus lows deteriorated meaningfully."
    )

st.write(" ".join(change_parts))

st.subheader("Breadth Confirmation")

recent = df.dropna(subset=["ad_line"]).tail(20).copy()

if len(recent) >= 2 and "SPY" in recent.columns:
    spy_change_20d = recent["SPY"].iloc[-1] / recent["SPY"].iloc[0] - 1
    ad_change_20d = recent["ad_line"].iloc[-1] - recent["ad_line"].iloc[0]

    if spy_change_20d > 0 and ad_change_20d > 0:
        confirmation_status = "🟢 Confirming"
        confirmation_text = (
            "The market and the Advance-Decline Line have both risen over the "
            "last 20 trading days. That suggests the broader market is participating "
            "in the move."
        )

    elif spy_change_20d > 0 and ad_change_20d <= 0:
        confirmation_status = "🔴 Negative Divergence"
        confirmation_text = (
            "SPY has risen over the last 20 trading days, but the Advance-Decline "
            "Line has not. That means fewer stocks are supporting the market's rise "
            "and is a potential warning sign."
        )

    elif spy_change_20d < 0 and ad_change_20d > 0:
        confirmation_status = "🟡 Improving Internals"
        confirmation_text = (
            "SPY has weakened over the last 20 trading days while the Advance-Decline "
            "Line has improved. That can indicate the market's internal condition is "
            "strengthening beneath a weak headline index."
        )

    else:
        confirmation_status = "🔴 Weak"
        confirmation_text = (
            "Both SPY and the Advance-Decline Line have weakened over the last "
            "20 trading days, indicating broad market weakness."
        )

    st.markdown(f"### {confirmation_status}")
    st.write(confirmation_text)

else:
    st.write(
        "Not enough data is currently available to evaluate breadth confirmation."
    )

st.caption(
    "Prototype note: This confirmation/divergence test uses a simple 20-trading-day "
    "comparison between SPY and the Advance-Decline Line. It is a research tool and "
    "does not represent any proprietary trading methodology."
)

st.subheader("Regime History")

regime_map = {
    "Bearish": 0,
    "Fragile": 1,
    "Bullish": 2,
    "Strong bullish": 3,
    "Strong Bullish": 3,
}

regime_df = df.dropna(subset=["regime"]).copy()

regime_df["regime_level"] = regime_df["regime"].map(regime_map)

regime_df = regime_df.dropna(subset=["regime_level"])

fig_regime = px.line(
    regime_df,
    x="date",
    y="regime_level",
    title=None,
)

fig_regime.update_yaxes(
    tickmode="array",
    tickvals=[0, 1, 2, 3],
    ticktext=[
        "Bearish",
        "Fragile",
        "Bullish",
        "Strong Bullish",
    ],
    title=None,
)

fig_regime.update_xaxes(title=None)

st.plotly_chart(
    fig_regime,
    use_container_width=True,
)

st.caption(
    "This chart shows the prototype market regime assigned by the Breadth Score over time. "
    "It is intended to show changes in overall market participation and is not a proprietary "
    "trading signal."
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
st.markdown(
    '<div class="iwmd-section-rule"></div>',
    unsafe_allow_html=True,
)

st.caption(
    "IWMD is an independent market breadth research prototype. "
    "Its Breadth Score, regime labels, confirmation tests, and backtests are "
    "research tools only and are not investment recommendations. "
    "Past market behavior does not guarantee future results."
)