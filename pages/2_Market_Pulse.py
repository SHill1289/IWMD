from pathlib import Path
import sys
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from breadthlab.storage import read_table
from breadthlab.glossary import tooltip

st.set_page_config(
    page_title="IWMD | Market Pulse",
    page_icon="📈",
    layout="wide",
)

st.logo(
    str(ROOT / "assets" / "iwmd_logo.png"),
    size="large",
)

st.markdown(
    """
    <style>
        .iwmd-section-heading {
            font-size: 1.45rem;
            font-weight: 700;
            color: #d7e3f4;
            margin-top: 1.4rem;
            margin-bottom: 0.65rem;
        }

        .iwmd-brief-label {
            color: #9fb7d1;
            font-weight: 700;
        }

        .iwmd-body-muted {
            color: rgba(255, 255, 255, 0.78);
        }

        .iwmd-positive {
            color: #22c55e;
            font-weight: 700;
        }

        .iwmd-negative {
            color: #ef4444;
            font-weight: 700;
        }

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
Market Pulse
</div>

<div style="font-size: 1.05rem; opacity: 0.72; max-width: 760px;">
A plain-English read on market health, participation, and internal momentum.
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

breadth_change = latest.breadth_score - prev.breadth_score

if latest.breadth_score >= 70:
    pulse_status = "STRONG"
elif latest.breadth_score >= 55:
    pulse_status = "HEALTHY"
elif latest.breadth_score >= 35:
    pulse_status = "FRAGILE"
else:
    pulse_status = "WEAK"

if breadth_change > 2:
    momentum = "improving"
elif breadth_change < -2:
    momentum = "deteriorating"
else:
    momentum = "stable"

if latest.high_low_net > 0:
    high_low_text = "new highs still exceed new lows"
else:
    high_low_text = "new lows now exceed new highs"

recent = df.dropna(subset=["ad_line"]).tail(20).copy()

if len(recent) >= 2 and "SPY" in recent.columns:
    spy_change_20d = recent["SPY"].iloc[-1] / recent["SPY"].iloc[0] - 1
    ad_change_20d = recent["ad_line"].iloc[-1] - recent["ad_line"].iloc[0]

    if spy_change_20d > 0 and ad_change_20d > 0:
        confirmation = "Confirming"
    elif spy_change_20d > 0 and ad_change_20d <= 0:
        confirmation = "Diverging"
    elif spy_change_20d < 0 and ad_change_20d > 0:
        confirmation = "Improving"
    else:
        confirmation = "Weak"
else:
    confirmation = "Unavailable"

pulse_text = (
    f"The broader market backdrop remains **{pulse_status.lower()}**, "
    f"but breadth is currently **{momentum}** versus the prior session. "
    f"Long-term participation stands at {latest.pct_above_200dma:.0%}. "
    f"{'New highs still exceed new lows.' if latest.high_low_net > 0 else 'New lows now exceed new highs.'} "
    f"The Advance-Decline Line is currently **{confirmation.lower()}** the index move."
)

st.subheader(f"Current Market Internals: {pulse_status}")

st.info(pulse_text)

pulse_cols = st.columns(3)

pulse_cols[0].metric(
    "Market Health",
    pulse_status.title(),
    help="A summary judgment based on the current Breadth Score.",
)

pulse_cols[1].metric(
    "Breadth Momentum",
    momentum.title(),
    help="Shows whether breadth improved, weakened, or stayed roughly stable versus the prior session.",
)

pulse_cols[2].metric(
    "Index Confirmation",
    confirmation,
    help="Compares the recent direction of SPY with the Advance-Decline Line to see whether market participation is confirming the index move.",
)

st.markdown(
    '<div class="iwmd-section-heading">Market Internals Brief</div>',
    unsafe_allow_html=True,
)

brief_items = [
    (
        "Backdrop",
        f"The broader market backdrop remains {pulse_status.lower()}, "
        f"with long-term participation at {latest.pct_above_200dma:.0%}."
    ),
    (
        "Confirmation",
        (
            "The Advance-Decline Line is still confirming the index move."
            if confirmation == "Confirming"
            else "The Advance-Decline Line is no longer fully confirming the index move."
        )
    ),
    (
        "Pressure Point",
        (
            "Breadth momentum is deteriorating, so the main risk is continued weakening beneath the headline index."
            if momentum == "deteriorating"
            else f"Breadth momentum is currently {momentum}, with no major deterioration signal from the prior session."
        )
    ),
]

st.markdown(
    "<div style='margin-bottom: 0.75rem;'>"
    + "".join(
        f"<div style='margin-bottom: 0.50rem;'>"
        f"• <span class='iwmd-brief-label'>{label}:</span> "
        f"<span class='iwmd-body-muted'>{text}</span>"
        f"</div>"
        for label, text in brief_items
    )
    + "</div>",
    unsafe_allow_html=True,
)

st.markdown('<div style="height: 0.75rem;"></div>', unsafe_allow_html=True)

st.markdown(
    '<div class="iwmd-section-heading">What to Watch</div>',
    unsafe_allow_html=True,
)

watch_items = []

if momentum == "deteriorating":
    watch_items.append(
        "Breadth has weakened from the prior session. A rebound in the Breadth Score "
        "would suggest the recent deterioration is stabilizing."
    )
else:
    watch_items.append(
        "Breadth is not currently deteriorating. Continued improvement would strengthen "
        "the current market-health reading."
    )

if confirmation == "Diverging":
    watch_items.append(
        "SPY is rising without confirmation from the Advance-Decline Line. "
        "That kind of divergence can signal narrowing participation."
    )
elif confirmation == "Confirming":
    watch_items.append(
        "The Advance-Decline Line is currently confirming the index. Watch for this "
        "relationship to weaken if SPY continues higher."
    )
else:
    watch_items.append(
        "Watch the relationship between SPY and the Advance-Decline Line for a clearer "
        "confirmation or divergence signal."
    )

if latest.high_low_net > 0:
    watch_items.append(
        "New 52-week highs still exceed new lows. A move toward zero or into negative "
        "territory would be a notable deterioration in market internals."
    )
else:
    watch_items.append(
        "New 52-week lows exceed new highs, which is a warning sign. Improvement would "
        "require this balance to move back toward positive territory."
    )

st.markdown(
    "<div style='margin-bottom: 0.75rem;'>"
    + "".join(
        f"<div class='iwmd-body-muted' style='margin-bottom: 0.50rem;'>"
        f"• {item}"
        f"</div>"
        for item in watch_items
    )
    + "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="iwmd-section-rule"></div>',
    unsafe_allow_html=True,
)

row1 = st.columns(3)
row2 = st.columns(2)

row1[0].metric(
    "Breadth Score",
    f"{latest.breadth_score:.1f}",
    f"{latest.breadth_score - prev.breadth_score:+.1f}",
    help=tooltip("breadth_score"),
)

row1[1].metric(
    "Breadth Regime",
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