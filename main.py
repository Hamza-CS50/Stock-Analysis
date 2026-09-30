import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# 1. USER INPUT
# ============================================================

ticker = input("Enter stock ticker (e.g. AAPL, MSFT, TSLA): ").upper().strip()

YEARS = 5
TRADING_DAYS = 252
RISK_FREE_RATE = 0.04       # 4% annual risk-free rate
RSI_PERIOD = 14
SMA_SHORT = 20
SMA_LONG = 50


# ============================================================
# 2. DOWNLOAD DATA
# ============================================================

print(f"\nDownloading {YEARS} years of data for {ticker}...")

stock = yf.Ticker(ticker)

data = stock.history(period=f"{YEARS}y", auto_adjust=True)

if data.empty:
    raise ValueError(
        f"No data found for {ticker}. "
        "Check that the ticker symbol is correct."
    )

# Remove timezone information
if data.index.tz is not None:
    data.index = data.index.tz_localize(None)

print(f"Downloaded {len(data)} trading days.")


# ============================================================
# 3. CLEAN DATA
# ============================================================

data = data.copy()

# Remove unnecessary columns if they exist
columns_to_keep = ["Open", "High", "Low", "Close", "Volume"]

data = data[[col for col in columns_to_keep if col in data.columns]]

# Remove missing values
data.dropna(inplace=True)

# Remove duplicate dates
data = data[~data.index.duplicated(keep="first")]


# ============================================================
# 4. DAILY RETURNS
# ============================================================

data["Daily Return"] = data["Close"].pct_change()

data.dropna(inplace=True)


# ============================================================
# 5. SIMPLE MOVING AVERAGES
# ============================================================

data["SMA_20"] = data["Close"].rolling(
    window=SMA_SHORT
).mean()

data["SMA_50"] = data["Close"].rolling(
    window=SMA_LONG
).mean()


# ============================================================
# 6. RSI
# ============================================================

delta = data["Close"].diff()

gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

average_gain = gain.rolling(
    window=RSI_PERIOD
).mean()

average_loss = loss.rolling(
    window=RSI_PERIOD
).mean()

rs = average_gain / average_loss

data["RSI"] = 100 - (100 / (1 + rs))


# ============================================================
# 7. CUMULATIVE RETURNS
# ============================================================

data["Cumulative Return"] = (
    1 + data["Daily Return"]
).cumprod() - 1


# ============================================================
# 8. BASIC STATISTICS
# ============================================================

mean_daily_return = data["Daily Return"].mean()

median_daily_return = data["Daily Return"].median()

std_daily_return = data["Daily Return"].std()

min_daily_return = data["Daily Return"].min()

max_daily_return = data["Daily Return"].max()


# ============================================================
# 9. TOTAL RETURN
# ============================================================

start_price = data["Close"].iloc[0]

end_price = data["Close"].iloc[-1]

total_return = (end_price / start_price) - 1


# ============================================================
# 10. CAGR
# ============================================================

start_date = data.index[0]
end_date = data.index[-1]

days = (end_date - start_date).days

years = days / 365.25

CAGR = (end_price / start_price) ** (1 / years) - 1


# ============================================================
# 11. ANNUALIZED VOLATILITY
# ============================================================

annualized_volatility = (
    std_daily_return * np.sqrt(TRADING_DAYS)
)


# ============================================================
# 12. SHARPE RATIO
# ============================================================

daily_risk_free_rate = (
    1 + RISK_FREE_RATE
) ** (1 / TRADING_DAYS) - 1

excess_daily_return = (
    data["Daily Return"] - daily_risk_free_rate
)

sharpe_ratio = (
    excess_daily_return.mean()
    / data["Daily Return"].std()
) * np.sqrt(TRADING_DAYS)


# ============================================================
# 13. MAXIMUM DRAWDOWN
# ============================================================

data["Running Maximum"] = data["Close"].cummax()

data["Drawdown"] = (
    data["Close"] / data["Running Maximum"]
) - 1

maximum_drawdown = data["Drawdown"].min()


# ============================================================
# 14. OTHER BASIC STATISTICS
# ============================================================

summary_statistics = data["Close"].describe()

average_volume = data["Volume"].mean()

highest_price = data["Close"].max()

lowest_price = data["Close"].min()


# ============================================================
# 15. CREATE SUMMARY TABLE
# ============================================================

metrics = {
    "Ticker": ticker,
    "Data Start": start_date.date(),
    "Data End": end_date.date(),
    "Starting Price": start_price,
    "Ending Price": end_price,
    "Total Return": total_return,
    "CAGR": CAGR,
    "Annualized Volatility": annualized_volatility,
    "Sharpe Ratio": sharpe_ratio,
    "Maximum Drawdown": maximum_drawdown,
    "Average Daily Return": mean_daily_return,
    "Median Daily Return": median_daily_return,
    "Daily Return Std Dev": std_daily_return,
    "Minimum Daily Return": min_daily_return,
    "Maximum Daily Return": max_daily_return,
    "Highest Closing Price": highest_price,
    "Lowest Closing Price": lowest_price,
    "Average Volume": average_volume
}

metrics_df = pd.DataFrame(
    list(metrics.items()),
    columns=["Metric", "Value"]
)


# ============================================================
# 16. PRINT RESULTS
# ============================================================

print("\n" + "=" * 50)
print(f"        {ticker} - 5 YEAR ANALYSIS")
print("=" * 50)

print(f"Starting Price       : ${start_price:.2f}")
print(f"Ending Price         : ${end_price:.2f}")
print(f"Total Return         : {total_return:.2%}")
print(f"CAGR                 : {CAGR:.2%}")
print(f"Annual Volatility    : {annualized_volatility:.2%}")
print(f"Sharpe Ratio         : {sharpe_ratio:.2f}")
print(f"Maximum Drawdown     : {maximum_drawdown:.2%}")
print(f"Average Daily Return : {mean_daily_return:.4%}")
print(f"Highest Price        : ${highest_price:.2f}")
print(f"Lowest Price         : ${lowest_price:.2f}")
print("=" * 50)


# ============================================================
# 17. VISUALIZATION
# ============================================================

plt.figure(figsize=(14, 7))

plt.plot(
    data.index,
    data["Close"],
    label="Close Price"
)

plt.plot(
    data.index,
    data["SMA_20"],
    label="20-Day SMA"
)

plt.plot(
    data.index,
    data["SMA_50"],
    label="50-Day SMA"
)

plt.title(f"{ticker} - Price & Moving Averages")

plt.xlabel("Date")
plt.ylabel("Price")

plt.legend()

plt.grid(True)

plt.tight_layout()

plt.show()


# ============================================================
# 18. CUMULATIVE RETURN CHART
# ============================================================

plt.figure(figsize=(14, 6))

plt.plot(
    data.index,
    data["Cumulative Return"] * 100
)

plt.title(f"{ticker} - Cumulative Return")

plt.xlabel("Date")
plt.ylabel("Return (%)")

plt.grid(True)

plt.tight_layout()

plt.show()


# ============================================================
# 19. RSI CHART
# ============================================================

plt.figure(figsize=(14, 5))

plt.plot(
    data.index,
    data["RSI"],
    label="RSI"
)

plt.axhline(
    70,
    linestyle="--",
    label="Overbought (70)"
)

plt.axhline(
    30,
    linestyle="--",
    label="Oversold (30)"
)

plt.title(f"{ticker} - RSI")

plt.xlabel("Date")
plt.ylabel("RSI")

plt.legend()

plt.grid(True)

plt.tight_layout()

plt.show()


# ============================================================
# 20. DRAWDOWN CHART
# ============================================================

plt.figure(figsize=(14, 6))

plt.plot(
    data.index,
    data["Drawdown"] * 100
)

plt.title(f"{ticker} - Drawdown")

plt.xlabel("Date")
plt.ylabel("Drawdown (%)")

plt.grid(True)

plt.tight_layout()

plt.show()


# ============================================================
# 21. EXPORT TO EXCEL
# ============================================================

filename = f"{ticker}_5Y_Stock_Analysis.xlsx"

# Prepare statistics dataframe
statistics_df = summary_statistics.reset_index()

statistics_df.columns = [
    "Statistic",
    "Value"
]

# Export multiple sheets
with pd.ExcelWriter(
    filename,
    engine="openpyxl"
) as writer:

    # Cleaned historical data
    data.to_excel(
        writer,
        sheet_name="Historical Data"
    )

    # Main metrics
    metrics_df.to_excel(
        writer,
        sheet_name="Metrics",
        index=False
    )

    # Descriptive statistics
    statistics_df.to_excel(
        writer,
        sheet_name="Statistics",
        index=False
    )


print(f"\nExcel file created successfully:")
print(filename)