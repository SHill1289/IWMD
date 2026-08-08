TOOLTIPS = {
    "breadth_score": (
        "A 0-100 summary of overall market participation. Higher means more S&P 500 "
        "stocks are participating in the market's strength. Lower means the market "
        "is being supported by fewer stocks."
    ),

    "regime": (
        "A plain-English label based on the Breadth Score. It summarizes whether "
        "market participation currently looks bearish, fragile, bullish, or strongly bullish."
    ),

    "above_20dma": (
        "The percentage of S&P 500 stocks trading above their 20-day moving average. "
        "This is a short-term measure of market participation and momentum."
    ),

    "above_50dma": (
        "The percentage of S&P 500 stocks trading above their 50-day moving average. "
        "This gives a medium-term view of market health. A high reading means strength "
        "is spread across many stocks."
    ),

    "above_200dma": (
        "The percentage of S&P 500 stocks trading above their 200-day moving average. "
        "This is a long-term measure of market health. High readings mean most stocks "
        "are in established uptrends."
    ),

    "advances": (
        "The number of stocks that closed higher than they did the previous trading day."
    ),

    "declines": (
        "The number of stocks that closed lower than they did the previous trading day."
    ),

    "unchanged": (
        "The number of stocks that finished at the same closing price as the previous trading day."
    ),

    "ad_net": (
        "Advancing stocks minus declining stocks. A positive number means more stocks rose "
        "than fell that day. A negative number means more stocks fell than rose."
    ),

    "ad_ratio": (
        "Advancing stocks divided by declining stocks. For example, 2.0 means twice as many "
        "stocks rose as fell."
    ),

    "ad_line": (
        "A running total of daily advances minus declines. If the market rises and the A/D Line "
        "also rises, participation is confirming the move. If the market rises while the A/D Line "
        "weakens, fewer stocks may be supporting the rally."
    ),

    "pct_advancing": (
        "The percentage of stocks that rose during the trading day. This makes daily breadth "
        "easier to compare regardless of how many stocks are in the dataset."
    ),

    "pct_declining": (
        "The percentage of stocks that fell during the trading day."
    ),

    "new_52w_highs": (
        "The number of stocks reaching their highest price in roughly the previous 52 weeks. "
        "More new highs generally indicate broader market strength."
    ),

    "new_52w_lows": (
        "The number of stocks reaching their lowest price in roughly the previous 52 weeks. "
        "A growing number of new lows can indicate increasing internal weakness."
    ),

    "high_low_net": (
        "52-week new highs minus 52-week new lows. Positive means more stocks are breaking "
        "out to new highs than breaking down to new lows."
    ),

    "high_low_line": (
        "A running total of new 52-week highs minus new 52-week lows. It shows whether major "
        "breakouts or major breakdowns have been dominating over time."
    ),

    "spy": (
        "SPY tracks the S&P 500 using market-cap weighting. The largest companies therefore "
        "have much more influence on its performance."
    ),

    "rsp": (
        "RSP tracks the same S&P 500 companies but gives each stock roughly equal weight. "
        "It is useful for seeing how the average S&P 500 stock is performing."
    ),

    "rsp_spy_ratio": (
        "Compares the equal-weight S&P 500 with the cap-weighted S&P 500. When the ratio rises, "
        "the average stock is outperforming the largest companies. When it falls, leadership "
        "is becoming more concentrated in large stocks."
    ),

    "rsp_spy_20d_change": (
        "The 20-trading-day change in the RSP/SPY ratio. Positive values indicate broadening "
        "participation; negative values indicate narrowing leadership."
    ),

    "mean_return": (
        "The average return of all stocks in the index for the day. A few very large moves can "
        "pull this average higher or lower."
    ),

    "median_return": (
        "The return of the middle stock after ranking all stocks from worst to best. This often "
        "gives a cleaner picture of what the typical stock did."
    ),

    "spy_return": (
        "The daily percentage change in SPY, the market-cap-weighted S&P 500 ETF."
    ),

    "annualized_return": (
        "The strategy's compounded return expressed as an approximate yearly rate."
    ),

    "annualized_volatility": (
        "How much the strategy's returns fluctuate, expressed as an annualized number. "
        "Higher volatility generally means a bumpier ride."
    ),

    "sharpe": (
        "A measure of return relative to volatility. Higher generally means more return was "
        "earned for the amount of risk taken. This prototype assumes a 0% risk-free rate."
    ),

    "max_drawdown": (
        "The largest peak-to-trough loss during the test. For example, -15% means the strategy "
        "at one point fell 15% from a previous high before recovering."
    ),

    "time_invested": (
        "The percentage of trading days when the rule had money invested in SPY."
    ),

    "growth_of_1": (
        "Shows what a hypothetical $1 investment would have grown to under the strategy."
    ),

    "historical_distance": (
        "Measures how similar a past market-breadth environment was to the selected date. "
        "Smaller numbers mean the historical day looked more similar."
    ),

    "forward_5d": (
        "SPY's return over the next 5 trading days after the historical comparison date."
    ),

    "forward_20d": (
        "SPY's return over the next 20 trading days, roughly one month."
    ),

    "forward_60d": (
        "SPY's return over the next 60 trading days, roughly three months."
    ),

    "forward_120d": (
        "SPY's return over the next 120 trading days, roughly six months."
    ),
}


def tooltip(name: str) -> str:
    return TOOLTIPS.get(name, "No explanation available yet.")
    