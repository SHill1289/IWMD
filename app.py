import streamlit as st

st.set_page_config(
    page_title="IWMD | Market Breadth Research",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            letter-spacing: -0.02em;
        }

        [data-testid="stMetric"] {
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 12px;
            padding: 14px 16px;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(128, 128, 128, 0.20);
        }

        .iwmd-brand {
            font-size: 2.4rem;
            font-weight: 700;
            letter-spacing: -0.04em;
            margin-bottom: 0;
        }

        .iwmd-subtitle {
            font-size: 1rem;
            opacity: 0.70;
            margin-top: 0.15rem;
            margin-bottom: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
 '<div class="iwmd-brand">IWMD Home</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="iwmd-subtitle">Market Breadth Research & Market Internals</div>',
    unsafe_allow_html=True,
)

st.write(
    "A research platform for monitoring market participation, breadth, "
    "leadership, regime changes, and historical market behavior."
)

st.info(
    "Start with the Dashboard for the current market-internals picture, "
    "then use Historical Analogs and Rule Backtest for deeper research."
)