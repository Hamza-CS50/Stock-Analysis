# Stock Analysis  – Documentation

## 1. Overview

This Python script downloads **5 years of daily price data** for a stock ticker entered by the user, computes common performance and risk metrics and technical indicators, shows four charts, prints a summary in the console, and exports everything to a multi-sheet Excel file.

**Data source:** Yahoo Finance via the `yfinance` library. **Output:** Console summary, 4 matplotlib charts, and `<TICKER>_5Y_Stock_Analysis.xlsx`.

---

## 2. Requirements

| Library | Purpose |
| --- | --- |
| `yfinance` | Download historical market data |
| `pandas` | Data cleaning, calculations, Excel export |
| `numpy` | Numerical operations (e.g. square root for annualizing) |
| `matplotlib` | Charts |
| `openpyxl` | Excel writer engine used by pandas |

Install:

```bash
pip install yfinance pandas numpy matplotlib openpyxl
```

An internet connection is required to download data.

---

## 3. How to Run

```bash
python stock_analysis.py
```

When prompted, enter a ticker such as `AAPL`, `MSFT` or `TSLA`. Input is converted to uppercase and stripped of spaces. If no data is found, the script raises a `ValueError`.

---

## 4. Configuration Constants

| Constant | Default | Meaning |
| --- | --- | --- |
| `YEARS` | `5` | Length of history to download |
| `TRADING_DAYS` | `252` | Trading days per year, used to annualize volatility and Sharpe ratio |
| `RISK_FREE_RATE` | `0.04` | Annual risk-free rate (4%) used in the Sharpe ratio |
| `RSI_PERIOD` | `14` | Lookback window for RSI |
| `SMA_SHORT` | `20` | Short moving-average window (days) |
| `SMA_LONG` | `50` | Long moving-average window (days) |

Change these at the top of the file to alter the analysis without touching the logic.

---

## 5. Step-by-Step Explanation

### Section 2 – Download Data

`yf.Ticker(ticker).history(period="5y", auto_adjust=True)` fetches daily data. `auto_adjust=True` means prices are **adjusted for splits and dividends**. The timezone is removed from the index so dates export cleanly to Excel.

### Section 3 – Clean Data

- Keeps only `Open, High, Low, Close, Volume`.
- Drops rows with missing values.
- Removes duplicate dates (keeps first).

### Section 4 – Daily Returns

`Daily Return = Close.pct_change()` → percentage change from the previous day's close. The first row (NaN) is dropped.

### Section 5 – Simple Moving Averages

Rolling mean of the closing price over 20 and 50 days (`SMA_20`, `SMA_50`). The first 19 / 49 rows are NaN because there is not enough history.

### Section 6 – RSI (Relative Strength Index)

1. `delta` = day-to-day price change.
2. `gain` = positive changes, `loss` = absolute value of negative changes.
3. Average gain and average loss over 14 days (simple rolling mean).
4. `RS = avg_gain / avg_loss`
5. `RSI = 100 − 100 / (1 + RS)`

Interpretation: above **70** = overbought, below **30** = oversold.

### Section 7 – Cumulative Return

`(1 + daily return).cumprod() − 1` → total growth of the investment since the first day in the dataset.

### Section 8 – Basic Statistics

Mean, median, standard deviation, minimum and maximum of daily returns.

### Section 9 – Total Return

`(End Price / Start Price) − 1`

### Section 10 – CAGR (Compound Annual Growth Rate)

`CAGR = (End / Start)^(1 / years) − 1`, where `years = calendar days / 365.25`. It shows the smoothed yearly growth rate.

### Section 11 – Annualized Volatility

`Std of daily returns × √252`. Higher = riskier.

### Section 12 – Sharpe Ratio

1. Convert the annual risk-free rate to a daily rate: `(1 + 0.04)^(1/252) − 1`.
2. Excess return = daily return − daily risk-free rate.
3. `Sharpe = (mean excess return / std of daily returns) × √252`

Interpretation (rough guide): below 1 = weak, 1–2 = good, above 2 = very good.

### Section 13 – Maximum Drawdown

- `Running Maximum` = highest close so far.
- `Drawdown = Close / Running Maximum − 1`
- `Maximum Drawdown` = the most negative drawdown, i.e. the worst peak-to-trough fall.

### Section 14 – Other Statistics

`describe()` on the closing price, average volume, highest close, lowest close.

### Section 15 – Summary Table

All key metrics are placed in a dictionary and converted to a two-column DataFrame (`Metric`, `Value`) for Excel.

### Section 16 – Console Output

Prints a formatted summary: prices, total return, CAGR, volatility, Sharpe, max drawdown, average daily return, highest and lowest price.

---

## 6. Charts

| # | Chart | Shows |
| --- | --- | --- |
| 1 | Price & Moving Averages | Close price with 20-day and 50-day SMA |
| 2 | Cumulative Return | Percentage growth over time |
| 3 | RSI | RSI line with 70 and 30 threshold lines |
| 4 | Drawdown | Percentage decline from the previous peak |

Each chart opens in its own window. Close a window to see the next one (the script uses `plt.show()`).

---

## 7. Excel Output

File name: `<TICKER>_5Y_Stock_Analysis.xlsx` (saved in the working directory)

| Sheet | Contents |
| --- | --- |
| **Historical Data** | Cleaned OHLCV data plus Daily Return, SMA_20, SMA_50, RSI, Cumulative Return, Running Maximum, Drawdown |
| **Metrics** | Summary table of all key metrics |
| **Statistics** | `describe()` output for the closing price |

---

## 8. Metrics Reference

| Metric | Formula / Meaning |
| --- | --- |
| Total Return | End price ÷ start price − 1 |
| CAGR | Annualized compounded growth rate |
| Annualized Volatility | Daily std × √252 |
| Sharpe Ratio | Risk-adjusted return vs. risk-free rate |
| Maximum Drawdown | Largest peak-to-trough decline |
| Average / Median Daily Return | Central tendency of daily returns |
| Daily Return Std Dev | Day-to-day variability |
| Min / Max Daily Return | Worst and best single day |
| Highest / Lowest Closing Price | Extremes of the period |
| Average Volume | Mean daily shares traded |

---

## 9. Known Limitations and Notes

1. **Start price is day 2.** Because the first row is dropped after calculating returns, `Starting Price`, Total Return, CAGR and Cumulative Return begin from the second trading day, not the first.
2. **RSI method.** RSI uses a simple rolling average. The classic Wilder RSI uses exponential smoothing, so values may differ slightly from platforms like TradingView.
3. **Adjusted prices.** Prices are adjusted for dividends and splits, so they can differ from the historical prices originally quoted.
4. **Volume is also adjusted** by Yahoo Finance for splits.
5. **Sharpe ratio** divides by the standard deviation of raw returns rather than excess returns (the difference is negligible).
6. **Fixed risk-free rate** of 4% is an assumption; update it to the current T-bill yield for accuracy.
7. **Console header** always says "5 YEAR ANALYSIS" even if `YEARS` is changed, and the Excel filename also contains `5Y`.
8. **Not financial advice.** The output is for educational and analytical purposes only and does not predict future performance.

---

## 10. Possible Improvements

- Use Wilder's smoothing for RSI.
- Add a benchmark comparison (e.g. S&P 500) with beta and alpha.
- Save charts as PNG files instead of only displaying them.
- Accept `YEARS` as user input.
- Wrap the code in functions and a `main()` for reuse and testing.
